"""
ClassEval reward computation utilities.

Implements a subprocess-based unittest runner that returns detailed per-test outcomes,
and a helper to run tests on combined code (skeleton merged with completions).

Scoring (updated CEB design):
- lv1 CEB (3 pts):
  Coverage/Overlap/Balance on self-selected method sets A_i across agents.
- lv2 Syntax (2 pts):
  +2 if combined code compiles (slightly lenient by design).
- lv3 Tests (4 pts):
  4 * (sum_test x * [test passed]) / (sum_test x),
  where x is the number of agents involved for that test. For TAKE_JOB, x is the
  number of agents whose chosen sets intersect the test's used methods. Otherwise,
  x is number of distinct assigned agents for the used methods.
- lv4 Components (1 pt):
  For each connected component in the class method-call graph, if it is solved by a
  single agent, add 1/num_agents. Total capped at 1.0.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from typing import Any, Dict, List, Optional, Set, Tuple
import os


def _combine_code(impl_code: str, test_code: str) -> str:
    return (impl_code or "").rstrip() + "\n\n" + (test_code or "").lstrip()


def run_unittests_with_details(impl_code: str, test_code: str, timeout: int = 40) -> Dict[str, Any]:
    """Run unittests with a custom TestResult that records per-test outcomes.

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
    except Exception:
        syntax_ok = False

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
from typing import Callable  # re-export type for signatures
from LLM_Collab_Module_Completion.utils.data import (
    extract_class_name,
    extract_incomplete_methods,
)
from LLM_Collab_Module_Completion.utils.parse_completion import extract_method_snippets
from LLM_Collab_Module_Completion.utils.merge import merge_methods_into_skeleton
from LLM_Collab_Module_Completion.utils.test_analysis import methods_called_per_test
from LLM_Collab_Module_Completion.loggers.reward_logger import RewardLogger


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
    """Return a reward function that merges per-agent completions, runs tests,
    and computes reward (CEB lv1 + syntax lv2 + tests lv3 + components lv4).
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

            partition = strategy.partition(example)

            method_to_code: Dict[str, str] = {}
            agent_texts: List[str] = []
            # Per-agent chosen set A_i (from completions), always parsed against full V
            A_sets: List[Set[str]] = []
            for agent_idx in range(num_agents):
                comp_text = ""
                try:
                    comp_text = agent_completions[agent_idx][i]
                except Exception:
                    comp_text = ""
                agent_texts.append(comp_text)
                # Parse against full V to get chosen set
                parsed_all = extract_method_snippets(comp_text or "", allowed_methods=set(method_names))
                A_sets.append(set(parsed_all.keys()))
                # For merging into candidate code, honor strategy behavior
                if getattr(strategy, "self_select", False):
                    allowed = set(method_names)
                else:
                    allowed = {m for m, a in partition.items() if a == agent_idx}
                if allowed:
                    snippets = extract_method_snippets(comp_text or "", allowed_methods=allowed)
                    method_to_code.update(snippets)

            # Preview generations to stdout (captured by job logs and optionally by W&B console)
            # try:
            #     preview_limit = 40000
            #     task_id = example.get("task_id")
            #     header = f"[gen] class={class_name or 'unknown'} task_id={str(task_id) if task_id is not None else 'N/A'}"
            #     print(header, flush=True)
            #     for aidx, text in enumerate(agent_texts):
            #         # Keep newlines for readability; still cap total chars
            #         snippet = (text or "")[:preview_limit]
            #         if text and len(text) > preview_limit:
            #             snippet += "..."
            #         print(f"[agent_{aidx}] {snippet}", flush=True)
            # except Exception:
            #     pass

            combined_code = merge_methods_into_skeleton(
                skeleton=skeleton,
                class_name=class_name,
                method_to_code=method_to_code,
            )

            # print('=' * 20)
            # print(combined_code)
            # print('=' * 20)

            # print('=' * 20)
            # print(test_code)
            # print('=' * 20)

            per_test_methods = methods_called_per_test(
                test_code=test_code,
                candidate_methods=set(method_names),
                class_name=class_name,
            )

            # Special case: if any agent didn't choose any method and n <= k, total reward is 0
            k = len(method_names)
            if any(len(s) == 0 for s in A_sets) and num_agents <= max(0, k):
                rewards.append(0.0)
                continue

            run_res = run_unittests_with_details(combined_code, test_code)
            syntax_ok = bool(run_res.get("syntax_ok", False))
            syntax_score = 2.0 if syntax_ok else 0.0

            # print('=' * 20)
            # print(run_res)
            # print('=' * 20)

            tests_run = int(run_res.get("testsRun", 0) or 0)
            test_results = run_res.get("test_results", []) or []
            # Compute lv3 using weighted pass by x
            num_x_total = 0
            num_x_passed = 0
            for tr in test_results:
                t_id = str(tr.get("id", ""))
                outcome = str(tr.get("outcome", ""))
                used = per_test_methods.get(t_id, set())
                if not used:
                    continue
                if getattr(strategy, "self_select", False):
                    # Count agents that chose any used method
                    x = sum(1 for s in A_sets if s & used)
                else:
                    agents_involved = {partition.get(m, -1) for m in used if m in partition}
                    agents_involved.discard(-1)
                    x = len(agents_involved)
                if x > 0:
                    num_x_total += x
                    if outcome == "passed":
                        num_x_passed += x
            pass_score = (4.0 * (num_x_passed / num_x_total)) if num_x_total > 0 else 0.0

            # print('=' * 20)
            # print(passed, tests_run)
            # print('=' * 20)

            # lv1: CEB (Coverage, 1-OverlapPenalty, Balance)
            V: Set[str] = set(method_names)
            k = len(V)
            n = max(1, num_agents)
            if k > 0:
                # Coverage
                union_size = len(set().union(*A_sets)) if A_sets else 0
                coverage = (union_size / k) if k > 0 else 0.0
                # Overlap penalty
                counts: Dict[str, int] = {m: 0 for m in V}
                for s in A_sets:
                    for m in s:
                        if m in counts:
                            counts[m] += 1
                overlap_pen = (sum(max(0, counts[m] - 1) for m in V) / k) if k > 0 else 0.0
                # Balance
                # Capacity C = ceil(eta * k/n), eta in [0.9,1.2], default 1.0
                try:
                    eta_env = float(os.environ.get("CEB_ETA", "1.0"))
                except Exception:
                    eta_env = 1.0
                eta = min(1.2, max(0.9, eta_env))
                import math as _math
                C = int(_math.ceil(eta * (k / n))) if n > 0 else 0
                if C <= 0:
                    balance = 0.0
                else:
                    balance = 1.0 - (sum(abs(len(s) - C) for s in A_sets) / (n * C))
                    balance = max(0.0, min(1.0, balance))
                # Weights from env or defaults
                def _w(name: str, default: float) -> float:
                    try:
                        v = os.environ.get(name, None)
                        return float(v) if v is not None else default
                    except Exception:
                        return default
                wc = _w("CEB_WC", 0.5)
                wo = _w("CEB_WO", 0.3)
                wb = _w("CEB_WB", 0.2)
                ssum = wc + wo + wb
                if ssum <= 0:
                    wc, wo, wb = 1.0, 0.0, 0.0
                    ssum = 1.0
                wc, wo, wb = wc / ssum, wo / ssum, wb / ssum
                ceb = 3.0 * (wc * coverage + wo * (1.0 - overlap_pen) + wb * balance)
                ceb = max(0.0, min(3.0, float(ceb)))
            else:
                ceb = 0.0

            # lv4: connected components solved by a single agent
            comps = _compute_call_graph_components(combined_code, class_name, V)
            solved = 0
            for comp in comps:
                if not comp:
                    continue
                if getattr(strategy, "self_select", False):
                    if any(comp.issubset(s) for s in A_sets):
                        solved += 1
                else:
                    agents_involved = {partition.get(m, -1) for m in comp if m in partition}
                    agents_involved.discard(-1)
                    if len(agents_involved) == 1:
                        solved += 1
            lv4 = min(1.0, solved / max(1, num_agents))

            total = float(ceb + syntax_score + pass_score + lv4)

            # Log per-level rewards to wandb during evaluation (phase=='eval')
            try:
                phase = str(example.get("phase", "")).lower() if isinstance(example, dict) else ""
            except Exception:
                phase = ""
            if phase == "eval":
                try:
                    RewardLogger.log_ce_levels(
                        ceb=ceb,
                        syntax=syntax_score,
                        tests=pass_score,
                        components=lv4,
                        total=total,
                        step=None,
                        commit=False,
                        prefix="eval/ce_reward",
                    )
                except Exception:
                    pass

            print('=' * 20)
            print(num_x_passed, num_x_total)
            print(ceb, syntax_score, pass_score, lv4)
            print('=' * 20)

            rewards.append(total)

        return rewards

    return reward_wrapper
