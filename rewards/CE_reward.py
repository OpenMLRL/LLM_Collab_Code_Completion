"""
Reward pipeline for ClassEval collaborative completion.

- `run_unittests_with_details` merges agent completions with the class skeleton, performs
  a syntax check, and (when valid) runs the hidden tests in an isolated subprocess while
  recording per-test outcomes.
- `get_reward_function` parses each agent’s code, builds per-method selections, and applies
  the simplified ClassEval shaping:
    * `lv1`: syntax score proportional to syntactically valid method outputs (range [0, 2]).
      If the combined program fails syntax, the total reward is set to 0.
    * `lv2`: test bonus proportional to the pass rate (passed/total), scaled to [0, 4].
    * `lv3`: overlap penalty normalized by total methods (range [-1, 0]).
- Optional logging hooks export the individual levels for eval batches.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Set
import io
import tokenize
import os

VERBOSE = True



def _combine_code(impl_code: str, test_code: str) -> str:
    return (impl_code or "").rstrip() + "\n\n" + (test_code or "").lstrip()


def run_unittests_with_details(impl_code: str, test_code: str, timeout: int = 40) -> Dict[str, Any]:
    """Run unittests with a custom TestResult that records per-test outcomes.

    Behavior:
    - First performs a syntax check on the merged code (implementation + tests).
    - If syntax fails, returns immediately without launching the subprocess test runner.
    - Otherwise, runs tests in an isolated temp directory and reports detailed outcomes.

    Returns a JSON-serializable dict including:
    - syntax_ok: bool
    - testsRun, passed, failures, errors, skipped
    - test_results: list of {id, outcome}
    - stdout, stderr, exit_code
    - timeout: bool
    """
    combined_code = _combine_code(impl_code, test_code)

    # Syntax check first (no formatting here; formatting is applied upstream after merge)
    try:
        compile(combined_code, "<combined>", "exec")
        syntax_ok = True
    except Exception as e:
        syntax_ok = False
        # Early return: do not run tests when syntax is invalid
        return {
            "syntax_ok": False,
            "timeout": False,
            "success": False,
            "testsRun": 0,
            "failures": 0,
            "errors": 1,
            "skipped": 0,
            "passed": 0,
            "stdout": "",
            "stderr": f"SyntaxError: {e}",
            "exit_code": None,
            "test_results": [],
        }

    runner_code = """
import json, sys, importlib.util, unittest, io, time, traceback, contextlib

class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({"id": str(test), "outcome": "passed"})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({"id": str(test), "outcome": "failed"})
    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({"id": str(test), "outcome": "error"})
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({"id": str(test), "outcome": "skipped"})

def main(py_file):
    import importlib.util
    spec = importlib.util.spec_from_file_location("task_module", py_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        runner = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordingResult)
        res = runner.run(suite)
    out = stream.getvalue()
    result = dict(
        testsRun=res.testsRun,
        failures=len(res.failures),
        errors=len(res.errors),
        skipped=len(res.skipped),
        passed=res.testsRun - len(res.failures) - len(res.errors) - len(res.skipped),
        success=res.wasSuccessful(),
        test_results=getattr(res, "records", []),
        output=out,
    )
    print(json.dumps(result))

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except SystemExit as e:
        import traceback as _tb
        print(json.dumps({"exception": "SystemExit", "code": getattr(e, 'code', None), "traceback": _tb.format_exc()}))
        sys.exit(3)
    except Exception as e:
        import traceback as _tb
        print(json.dumps({"exception": str(e), "traceback": _tb.format_exc()}))
        sys.exit(2)
"""

    # Run tests in an isolated temporary working directory so that any
    # file system side effects from user code or tests do not pollute the repo root.
    # If a job id is available, group temp dirs under it to avoid collisions
    # across concurrent processes while keeping per-call isolation.
    base_tmp = os.environ.get("CLASSEVAL_TMP_BASE", tempfile.gettempdir())
    tmp_parent = base_tmp
    try:
        tmp_parent = os.path.abspath(tmp_parent)
    except Exception:
        pass
    try:
        os.makedirs(tmp_parent, exist_ok=True)
    except Exception:
        pass

    with tempfile.TemporaryDirectory(dir=tmp_parent) as tmpdir:
        # Normalize tmpdir and pass relative payload to runner
        try:
            tmpdir_abs = os.path.abspath(tmpdir)
        except Exception:
            tmpdir_abs = tmpdir
        payload_name = "task_module_payload.py"
        py_path = os.path.join(tmpdir_abs, payload_name)
        with open(py_path, "w", encoding="utf-8") as fh:
            fh.write(combined_code)
        try:
            proc = subprocess.run(
                [sys.executable, "-c", runner_code, payload_name],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                cwd=tmpdir_abs,
            )
        except subprocess.TimeoutExpired:
            return {
                "syntax_ok": syntax_ok,
                "timeout": True,
                "success": False,
                "testsRun": 0,
                "failures": 0,
                "errors": 1,
                "skipped": 0,
                "passed": 0,
                "stdout": "",
                "stderr": "TimeoutExpired",
                "exit_code": None,
                "test_results": [],
            }

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    try:
        res = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        res = {
            "success": False,
            "testsRun": 0,
            "failures": 0,
            "errors": 1,
            "skipped": 0,
            "passed": 0,
            "parse_error": True,
            "output": stdout,
        }

    res.update(
        {
            "syntax_ok": syntax_ok,
            "timeout": False,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode,
        }
    )
    return res


# ---------- Reward Factory (multi-agent merge + scoring) ----------
def _is_triple_quoted_string_literal(s: str) -> bool:
    """Heuristic check if a token string is triple-quoted (handles prefixes rRuUbBfF)."""
    i = 0
    while i < len(s) and s[i] in 'rRbBuUfF':
        i += 1
    if i + 2 < len(s) and s[i] in ("'", '"') and s[i] == s[i+1] == s[i+2]:
        return True
    return False


def _docstring_line_indices(text: str) -> Set[int]:
    """Return 1-based line numbers that belong to triple-quoted string literals.

    Tries tokenize first for accuracy; falls back to a simple delimiter scan
    if tokenization fails.
    """
    doc_lines: Set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.STRING and _is_triple_quoted_string_literal(tok.string):
                start_line = tok.start[0]
                end_line = tok.end[0]
                for ln in range(start_line, end_line + 1):
                    doc_lines.add(ln)
        return doc_lines
    except Exception:
        # Fallback: naive scanning for """ or ''' blocks
        pass

    lines = text.splitlines()
    in_triple = False
    delim = None
    for idx, line in enumerate(lines, start=1):
        j = 0
        found_segment = False
        L = len(line)
        while j + 2 < L:
            seg = line[j:j+3]
            if not in_triple and (seg == '"""' or seg == "'''"):
                in_triple = True
                delim = seg
                found_segment = True
                j += 3
                continue
            if in_triple and seg == delim:
                in_triple = False
                delim = None
                found_segment = True
                j += 3
                continue
            j += 1
        if in_triple or found_segment:
            doc_lines.add(idx)
    return doc_lines


def _compute_comment_ratio_including_docstrings(text: str) -> float:
    """Compute comment ratio counting both # lines and triple-quoted blocks.

    Ratio = comment_like_nonempty_lines / total_nonempty_lines. Lines inside
    triple-quoted strings (three double quotes or three single quotes) are counted as comment-like.
    """
    if not text:
        return 0.0
    lines = text.splitlines()
    doc_lines = _docstring_line_indices(text)
    nonempty_total = 0
    comment_like = 0
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        nonempty_total += 1
        if line.lstrip().startswith('#') or (idx in doc_lines):
            comment_like += 1
    return (comment_like / nonempty_total) if nonempty_total > 0 else 0.0

from typing import Callable  # re-export type for signatures
from LLM_Collab_Code_Completion.utils.data import (
    extract_class_name,
    extract_incomplete_methods,
)
from LLM_Collab_Code_Completion.utils.parse_completion import extract_method_snippets
from LLM_Collab_Code_Completion.loggers.reward_logger import RewardLogger
from LLM_Collab_Code_Completion.utils.merge import (
    merge_methods_into_skeleton,
    build_method_map_with_syntax_selection,
)


def _compute_call_graph_components(source_code: str, class_name: str, methods: Set[str]) -> List[Set[str]]:
    """Build undirected connected components of method-call graph within the class.

    Edges between methods u-v if method u contains a call to v (e.g., self.v(...)).
    Only consider methods within the provided `methods` set.
    Returns a list of components (each as a set of method names).
    """
    comps: List[Set[str]] = []
    if not source_code or not class_name or not methods:
        return comps
    try:
        import ast
    except Exception:
        return comps
    try:
        tree = ast.parse(source_code)
    except Exception:
        return comps

    # Locate class
    target = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            target = node
            break
    if target is None:
        return comps

    # Build adjacency
    adj: Dict[str, Set[str]] = {m: set() for m in methods}

    def collect_calls(fn: "ast.FunctionDef") -> Set[str]:
        called: Set[str] = set()
        for ch in ast.walk(fn):
            if isinstance(ch, ast.Call):
                f = ch.func
                # self.method(...) or obj.method(...)
                if isinstance(f, ast.Attribute):
                    name = f.attr
                    if name in methods:
                        called.add(name)
                # direct function call (unlikely in class method context)
        return called

    for item in target.body:
        if isinstance(item, (ast.FunctionDef,)):
            src = item.name
            if src not in methods:
                continue
            outs = collect_calls(item)
            for dst in outs:
                if dst in methods and dst != src:
                    adj[src].add(dst)
                    adj[dst].add(src)

    # Connected components on adjacency
    seen: Set[str] = set()
    for m in methods:
        if m in seen:
            continue
        stack = [m]
        comp: Set[str] = set()
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp.add(u)
            for v in adj.get(u, set()):
                if v not in seen:
                    stack.append(v)
        if comp:
            comps.append(comp)
    return comps

def get_reward_function(strategy, num_agents: int) -> Callable[..., List[float]]:
    """Return a reward function
    """

    def reward_wrapper(*agent_completions, batch_items=None, prompts=None):
        if not agent_completions:
            return []
        batch_size = len(agent_completions[0])
        rewards: List[float] = []

        for i in range(batch_size):
            example = {}
            try:
                example = batch_items[i] if batch_items is not None else {}
            except Exception:
                pass

            skeleton: str = example.get("skeleton", "")
            test_code: str = example.get("test", "")
            class_name = extract_class_name(skeleton) or ""
            method_names = extract_incomplete_methods(skeleton)
            total_methods = len(method_names)

            partition = strategy.partition(example)

            agent_texts: List[str] = []
            A_sets: List[Set[str]] = []
            for agent_idx in range(num_agents):
                comp_text = ""
                try:
                    comp_text = agent_completions[agent_idx][i]
                except Exception:
                    comp_text = ""
                agent_texts.append(comp_text)
                parsed_all = extract_method_snippets(comp_text or "", allowed_methods=set(method_names))
                A_sets.append(set(parsed_all.keys()))

            # lv3: overlap penalty normalized by total methods
            lv3 = 0.0
            try:
                method_hits: Dict[str, int] = {}
                for s in A_sets:
                    if not s:
                        continue
                    for m in s:
                        method_hits[m] = method_hits.get(m, 0) + 1
                overlap_count = sum(1 for cnt in method_hits.values() if cnt > 1)
                if total_methods > 0:
                    lv3 = -float(overlap_count) / float(total_methods)
                else:
                    lv3 = 0.0
            except Exception:
                lv3 = 0.0

            # ---------- lv1 (syntax) and lv2 (tests) ----------
            # Build merged candidate code from agent completions for syntax/tests evaluation.
            # For duplicate method names across agents, choose only syntactically valid snippets;
            # if multiple are valid, pick one at random. Invalid-only methods are omitted.
            try:
                method_to_code: Dict[str, str] = build_method_map_with_syntax_selection(
                    agent_texts=agent_texts,
                    method_names=method_names,
                    partition=partition,
                    self_select=bool(getattr(strategy, "self_select", False)),
                )
            except Exception:
                method_to_code = {}

            valid_method_count = len(method_to_code)
            if total_methods > 0:
                lv1 = 2.0 * (float(valid_method_count) / float(total_methods))
            else:
                lv1 = 0.0

            combined_code = merge_methods_into_skeleton(
                skeleton=skeleton,
                class_name=class_name,
                method_to_code=method_to_code,
            )

            run_res = run_unittests_with_details(combined_code, test_code)
            syntax_ok = bool(run_res.get("syntax_ok", False))

            # ensure syntax_ok...
            if not syntax_ok:
                rewards.append(0.0)
                continue

            tests_run = int(run_res.get("testsRun") or 0)
            passed_cnt = int(run_res.get("passed") or 0)
            lv2 = (4.0 * float(passed_cnt) / float(tests_run)) if tests_run > 0 else 0.0

            total = float(lv1 + lv2 + lv3)

            if VERBOSE:
                print("=" * 50)
                print(lv1, lv2, lv3)

            # Optional eval logging (reuse field names for compatibility)
            try:
                phase = str(example.get("phase", "")).lower() if isinstance(example, dict) else ""
            except Exception:
                phase = ""
            if phase == "eval":
                try:
                    RewardLogger.log_ce_levels(
                        cover=lv1,
                        overlap=lv2,
                        balance=lv3,
                        components=0.0,
                        total=total,
                        step=None,
                        commit=False,
                        prefix="eval/ce_reward",
                        extra={
                            "level1_syntax": lv1,
                            "level2_tests": lv2,
                            "level3_overlap_penalty": lv3,
                        },
                    )
                except Exception:
                    pass

            if VERBOSE:
                # Preview generations: print each agent's code and number of functions parsed
                try:
                    preview_limit = 5000
                    task_id = example.get("task_id")
                    header = f"[gen] class={class_name or 'unknown'} task_id={str(task_id) if task_id is not None else 'N/A'}"
                    print(header, flush=True)
                    print(f"total funcs: {total_methods}")
                    for aidx, text in enumerate(agent_texts):
                        funcs_cnt = len(A_sets[aidx]) if aidx < len(A_sets) else 0
                        snippet = (text or "")[:preview_limit]
                        if text and len(text) > preview_limit:
                            snippet += "..."
                        print(f"[agent_{aidx}] funcs={funcs_cnt}", flush=True)
                        print(f"[agent_{aidx}] code:\n{snippet}", flush=True)
                except Exception:
                    pass
                print("=" * 50)

            rewards.append(total)

        return rewards

    return reward_wrapper
