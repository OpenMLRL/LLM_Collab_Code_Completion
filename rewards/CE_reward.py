"""
Reward pipeline for ClassEval collaborative completion.

- `run_unittests_with_details` merges agent completions with the class skeleton, performs
  a syntax check, and (when valid) runs the hidden tests in an isolated subprocess while
  recording per-test outcomes.
- `get_reward_function` parses each agent’s code, builds per-method selections, and applies
  the redesigned ClassEval shaping:
    * Early gates: penalize agents that emit zero methods, require union coverage ≥50%, and
      reject samples whose total picks exceed `2V+2`.
    * `lv1`: coverage score `2 * |union| / V` (with a soft zero zone when coverage ∈ [0.5, 0.65)).
    * `lv2`: total-picks/overlap control implemented as a Jaccard-based penalty to discourage
      duplicate work; combined with `lv1`/`lv3` via a 0.5 scaling factor.
    * `lv3`: load-balance reward computed from the mean-squared deviation of per-agent method
      counts around the ideal `V / N`.
    * `lv4`: syntax bonus (2 points) that also carries a token-length penalty per agent; if
      syntax fails the total reward is forced to zero.
    * `lv5`: test bonus proportional to the number of agents responsible for each passing test,
      using the per-test method usage analysis.
- Counters track how many samples clear each gate, and optional logging hooks export the
  individual levels for eval batches.
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


from LLM_Collab_Code_Completion.utils.text_tools import (
    count_new_tokens,
    get_effective_max_new_tokens,
)

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
    # If a job id is available (e.g., SLURM_JOB_ID), group temp dirs under it to
    # avoid collisions across concurrent processes while keeping per-call isolation.
    base_tmp = os.environ.get("CLASSEVAL_TMP_BASE", tempfile.gettempdir())
    job_id = os.environ.get("SLURM_JOB_ID") or os.environ.get("JOB_ID")
    # Support placeholder in base path: ".../[jobid]/tmp"
    if isinstance(base_tmp, str) and job_id and "[jobid]" in base_tmp:
        try:
            base_tmp = base_tmp.replace("[jobid]", str(job_id))
        except Exception:
            pass
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
from LLM_Collab_Code_Completion.utils.test_analysis import methods_called_per_test


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

# count rate of passing lv1 + lv2
_count_total, _count_pass_lv1_2, _count_pass_lv0 = 0, 0, 0
_count_pass_syntax = 0

def get_reward_function(strategy, num_agents: int) -> Callable[..., List[float]]:
    """Return a reward function implementing the redesigned lv1+lv2+lv3 scoring.

    - V = total number of class methods requiring implementation
    - lv1 = 2 * (|union of chosen methods across agents| / V)
      Special case: if coverage < 1/2 then reward = 0 for this sample
    - lv2 = total-picks control:
      Let S = Σ_i |A_i| be the total number of functions generated by all agents.
        * If S ≥ 2V+2: terminate this sample early with total reward = -INF (=-1)
        * If 0 <= S <= V: lv2(S) = 2 - 3 * ((S - V)^2) / V^2 (assuming V>0)
        * If V < S <= 2V+2: lv2(S) = 2 - 3 * ((S - V)^2) / (V + 1)^2
    - lv3 = balance based on variance of |A_i| around t = V/N, with
      MSD = (1/N) * Σ (s_i - t)^2 and MSD_max = (1/N) * V^2 * (1 - 1/N),
      R_bal = max(0, 1 - MSD/(MSD_max + eps))
    Total reward = lv1 + lv2 + lv3
    """

    def reward_wrapper(*agent_completions, batch_items=None, prompts=None):
        # Use module-level counters for pass rate tracking
        global _count_total, _count_pass_lv1_2, _count_pass_lv0
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

            INF = 1
            _count_total += 1

            # Early penalty: penalize by number of agents with zero functions (k * -INF) and skip
            try:
                zeros = sum(1 for s in A_sets if (len(s) if s is not None else 0) == 0)
                if zeros > 0:
                    rewards.append(-INF * 0.5 * zeros)
                    continue
            except Exception:
                # fall back to normal flow on unexpected structure
                pass
            
            _count_pass_lv0 += 1

            # New reward rules (lv1 + lv2)
            V_set: Set[str] = set(method_names)
            V = len(V_set)
            if V <= 0:
                rewards.append(-INF)
                continue

            # lv1: 2 * (|union| / V); if coverage < 1/2 => reward 0
            union_size = len(set().union(*A_sets)) if A_sets else 0
            coverage_ratio = union_size / V
            if coverage_ratio < 0.5:
                rewards.append(-INF)
                continue
            elif coverage_ratio < 0.65:
                rewards.append(0)
                continue
            
            lv1 = 2.0 * coverage_ratio

            # lv2: constrain total picks S = sum_i |A_i|
            S_total = sum(len(s) for s in A_sets)
            # Early termination if total picks exceed 2V
            if S_total > 2 * V + 2:
                rewards.append(-INF)
                continue

            # Piecewise quadratic for lv2 (total picks control)
            # - Left branch: lv2_left(S) = 2 - 3 * ((S - V)^2) / V^2
            # - Right branch: lv2_right(S) = 2 - 3 * ((S - V)^2) / (V + 1)^2
            # if V > 0:
            #     if S_total <= V:
            #         dv = float(S_total) - float(V)
            #         lv2 = 2.0 - 3.0 * (dv * dv) / (float(V) * float(V))
            #     elif S_total <= V * 2 + 1:
            #         dv = float(S_total) - float(V)
            #         lv2 = 2.0 - 3.0 * (dv * dv) / float((V + 1) * (V + 1))
            #     elif S_total == V * 2 + 2:
            #         lv2 = -2.5
            #     else:
            #         lv2 = -2.0 * INF
            # else:
            #     lv2 = -2.0 * INF

            # Add Pairwise Jaccard penalty (mean) into lv2, mapped to [-2, 2]
            # J(A_i, A_j) = |A_i ∩ A_j| / |A_i ∪ A_j|, averaged over all unordered pairs.
            # Map mean_J in [0,1] to term T in [-2,2] via T = 2 * (1 - 2*mean_J).
            lv2 = 0
            try:
                N_pairs = 0
                sum_J = 0.0
                N_sets = len(A_sets)
                for p in range(N_sets):
                    Si = A_sets[p] or set()
                    for q in range(p + 1, N_sets):
                        Sj = A_sets[q] or set()
                        u = len(Si | Sj)
                        if u == 0:
                            J = 0.0
                        else:
                            J = len(Si & Sj) / float(u)
                        sum_J += J
                        N_pairs += 1
                mean_J = (sum_J / N_pairs) if N_pairs > 0 else 0.0
                jaccard_term = 1.0 * (1.0 - 1.5 * mean_J)
                # if jaccard_term > 2.0:
                #     jaccard_term = 2.0
                # elif jaccard_term < -2.0:
                #     jaccard_term = -2.0
                lv2 += jaccard_term
            except Exception:
                pass

            # lv3: balance via MSD of chosen set sizes
            N = max(1, int(num_agents))
            t = V / N
            s_list = [float(len(s)) for s in A_sets] if A_sets else [0.0] * N
            msd = (sum((si - t) ** 2 for si in s_list) / N) if N > 0 else 0.0
            msd_max = (1.0 / N) * (V ** 2) * (1.0 - 1.0 / N) if N > 0 else 0.0
            eps = 1e-8
            lv3 = 3 * max(0.0, 1.0 - (msd / (msd_max + eps)))

            discount_lv123 = 0.5
            lv1 *= discount_lv123
            lv2 *= discount_lv123
            lv3 *= discount_lv123

            # ---------- Added lv4 (syntax) and lv5 (tests) per prior design ----------
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

            combined_code = merge_methods_into_skeleton(
                skeleton=skeleton,
                class_name=class_name,
                method_to_code=method_to_code,
            )

            # Compute per-test used methods for weighting (reused from earlier version)
            per_test_methods = methods_called_per_test(
                test_code=test_code,
                candidate_methods=set(method_names),
                class_name=class_name,
            )

            run_res = run_unittests_with_details(combined_code, test_code)
            syntax_ok = bool(run_res.get("syntax_ok", False))
            lv4 = 2.0 if syntax_ok else 0.0

            # ensure syntax_ok...
            if not syntax_ok:
                rewards.append(0)
                continue

            # Per-agent length penalty based on max_new_tokens L from config:
            # For each agent with output token count x, define a parabola with axis at a=(L-1)/2,
            # passing through ((L-1)/2, 0) and (L-1, -lv4/num_agents). When x < a, penalty is 0.
            try:
                base_lv4 = float(lv4)
                N_agents = int(num_agents) if num_agents else max(1, len(agent_texts))
                # Allow override via env; else use parsed config value
                try:
                    L = int(os.environ.get("CLASSEVAL_MAX_NEW_TOKENS", get_effective_max_new_tokens()))
                except Exception:
                    L = get_effective_max_new_tokens()
                a = (float(L) - 1.0) / 2.0
                if a > 0.0 and N_agents > 0 and base_lv4 > 0.0:
                    k = (base_lv4 / float(N_agents)) / (a * a)
                    total_penalty = 0.0
                    for agent_idx in range(N_agents):
                        comp_text = agent_texts[agent_idx] if agent_idx < len(agent_texts) else ""
                        # Prefer actual token count via HF tokenizer; fallback heuristic otherwise
                        try:
                            x_int = count_new_tokens(comp_text or "")
                        except Exception:
                            x_int = len((comp_text or "").split())
                        # Clamp to [0, L-1] per definition
                        if x_int < 0:
                            x_int = 0
                        if x_int > (L - 1):
                            x_int = (L - 1)
                        x = float(x_int)
                        if x >= a:
                            y = -k * (x - a) * (x - a)
                            # Cap per-agent penalty at [-base_lv4/N_agents, 0]
                            lower_cap = -base_lv4 / float(N_agents)
                            if y < lower_cap:
                                y = lower_cap
                            if y > 0.0:
                                y = 0.0
                            total_penalty += y
                    lv4 = float(lv4) + total_penalty * 0.6
            except Exception:
                # On any parsing/calculation issues, leave lv4 unchanged
                pass

            # _count_pass_syntax += 1

            test_results = run_res.get("test_results", []) or []
            num_x_total = 0
            num_x_passed = 0
            for tr in test_results:
                t_id = str(tr.get("id", ""))
                outcome = str(tr.get("outcome", ""))
                used = per_test_methods.get(t_id, set())
                if not used:
                    continue
                if getattr(strategy, "self_select", False):
                    x = sum(1 for s in A_sets if s & used)
                else:
                    agents_involved = {partition.get(m, -1) for m in used if m in partition}
                    agents_involved.discard(-1)
                    x = len(agents_involved)
                if x > 0:
                    num_x_total += x
                    if outcome == "passed":
                        num_x_passed += x
            lv5 = (3.0 * (num_x_passed / num_x_total)) if num_x_total > 0 else 0.0

            _count_pass_lv1_2 += 1
            total = float(lv1 + lv2 + lv3 + lv4 + lv5)

            print('=' * 50)
            print(lv1, lv2, lv3, lv4, lv5)
            print(_count_pass_lv0 / _count_total)
            print(_count_pass_lv1_2 / _count_total)
            # print(_count_pass_syntax / _count_total)

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
                            "level4_syntax": lv4,
                            "level5_tests": lv5,
                        },
                    )
                except Exception:
                    pass

            # Preview generations: print each agent's code and number of functions parsed
            try:
                preview_limit = 5000
                task_id = example.get("task_id")
                header = f"[gen] class={class_name or 'unknown'} task_id={str(task_id) if task_id is not None else 'N/A'}"
                print(header, flush=True)
                print(f"total funcs: {V}")
                for aidx, text in enumerate(agent_texts):
                    funcs_cnt = len(A_sets[aidx]) if aidx < len(A_sets) else 0
                    snippet = (text or "")[:preview_limit]
                    if text and len(text) > preview_limit:
                        snippet += "..."
                    print(f"[agent_{aidx}] funcs={funcs_cnt}", flush=True)
                    print(f"[agent_{aidx}] code:\n{snippet}", flush=True)
            except Exception:
                pass

            print('=' * 50)

            rewards.append(total)

        return rewards

    return reward_wrapper
