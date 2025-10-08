"""
ClassEval reward computation utilities.

Implements a subprocess-based unittest runner that returns detailed per-test outcomes,
and a helper to run tests on combined code (skeleton merged with completions).

Scoring (redesigned):
- Let V be the total number of methods in the class.
- lv1 (coverage): let x be the size of the union of all agents' selected method sets; score = 2 * (x / V).
  Special case: if (x / V) < 1/2, total reward = 0 for this sample.
- lv2 (overlap): let x be the total overlap count across methods (sum over m of max(0, count(m) - 1)).
  Let n be the number of agents and define T = ceil(((n - 1) * V) / 2) + n.
  For x <= V: score = 1 - (x / V) (linear).
  For V < x <= T: use a concave-down interpolation that accelerates away from V and reaches -2*INF at x = T.
  A simple choice convenient for training is the scaled power curve:
    lv2(x) = -2*INF * ((x - V) / (T - V))^p, with p >= 1 (default p=2; override via env `CE_LV2_EXP`).
  If x > T: terminate this sample with reward = -INF immediately.
- lv3 (balance via variance): let N be the number of agents, and s_i the number of methods chosen by agent i.
  Target t = V/N, MSD = (1/N) * Σ (s_i - t)^2, MSD_max = (1/N) * V^2 * (1 - 1/N).
  Score R_bal = max(0, 1 - MSD / (MSD_max + eps)).
Total reward = lv1 + lv2 + lv3.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from typing import Any, Dict, List, Optional, Set, Tuple
import os
import math

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
from typing import Callable  # re-export type for signatures
from LLM_Collab_Module_Completion.utils.data import (
    extract_class_name,
    extract_incomplete_methods,
)
from LLM_Collab_Module_Completion.utils.parse_completion import extract_method_snippets
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

# count rate of passing lv1 + lv2
_count_total, _count_pass, _count_pass_lv1 = 0, 0, 0

def get_reward_function(strategy, num_agents: int) -> Callable[..., List[float]]:
    """Return a reward function implementing the redesigned lv1+lv2+lv3 scoring.

    - V = total number of class methods requiring implementation
    - lv1 = 2 * (|union of chosen methods across agents| / V)
      Special case: if coverage < 1/2 then reward = 0 for this sample
    - lv2 = piecewise overlap penalty with concave interpolation beyond V:
      Let overlap_total = Σ_m max(0, count(m) - 1) and T = ceil(((n-1)*V)/2) + n where n = num_agents.
        * If overlap_total <= V: lv2 = 1 - (overlap_total / V)
        * If V < overlap_total <= T: lv2 = -2*INF * ((overlap_total - V) / (T - V))^p, default p=2 (p >= 1)
        * If overlap_total > T: terminate this sample early with total reward = -INF (=-1)
    - lv3 = balance based on variance of |A_i| around t = V/N, with
      MSD = (1/N) * Σ (s_i - t)^2 and MSD_max = (1/N) * V^2 * (1 - 1/N),
      R_bal = max(0, 1 - MSD/(MSD_max + eps))
    Total reward = lv1 + lv2 + lv3
    """

    def reward_wrapper(*agent_completions, batch_items=None, prompts=None):
        # Use module-level counters for pass rate tracking
        global _count_total, _count_pass, _count_pass_lv1
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

            # Early penalty: if any agent generated zero functions, assign -2 and skip
            try:
                if any((len(s) if s is not None else 0) == 0 for s in A_sets):
                    rewards.append(-INF * 2)
                    continue
            except Exception:
                # fall back to normal flow on unexpected structure
                pass


            # New reward rules (lv1 + lv2)
            V_set: Set[str] = set(method_names)
            V = len(V_set)
            if V <= 0:
                rewards.append(-INF)
                continue

            # lv1: 2 * (|union| / V); if coverage < 1/2 => reward 0
            union_size = len(set().union(*A_sets)) if A_sets else 0
            coverage_ratio = union_size / V
            if coverage_ratio < 0.35:
                rewards.append(-INF)
                continue
            
            lv1 = 2.0 * coverage_ratio
            if coverage_ratio < 0.5:
                lv1 = 0

            _count_pass_lv1 += 1

            # lv2: concave penalty beyond V; reaches -2*INF at T = ceil(((n-1)*V)/2) + n
            counts: Dict[str, int] = {m: 0 for m in V_set}
            for s in A_sets:
                for m in s:
                    if m in counts:
                        counts[m] += 1
            overlap_x = sum(max(0, c - 1) for c in counts.values())
            n_agents = max(1, int(num_agents))
            # T_val = math.ceil(((n_agents - 1) * V) / 2.0) + n_agents
            T_val = math.ceil(((n_agents - 1) * V) / 2.0)

            # Early termination if overlap exceeds T
            if overlap_x > T_val:
                rewards.append(-INF)
                continue
            if overlap_x <= V:
                lv2 = 1.0 - (overlap_x / V)
            else:
                # Concave-down interpolation on (V, T]:
                #   lv2(x) = -2*INF * ((x - V) / (T - V))^p, p >= 1 (default 2)
                try:
                    p = float(os.environ.get("CE_LV2_EXP", "2.0"))
                    if p < 1:
                        p = 2.0
                except Exception:
                    p = 2.0
                # Guard against degenerate T==V (no interpolation range)
                denom = float(T_val - V)
                if denom <= 0:
                    lv2 = -2.0 * INF  # fall back to strongest penalty in this band
                else:
                    ratio = (float(overlap_x) - float(V)) / denom
                    if ratio < 0:
                        ratio = 0.0
                    elif ratio > 1:
                        ratio = 1.0
                    lv2 = -(2.0 * INF) * (ratio ** p)

            # get bonus after passing lv1, lv2
            lv_bonus = 0.2

            # lv3: balance via entropy of chosen set sizes
            N = max(1, int(num_agents))
            s_list = [float(len(s)) for s in A_sets] if A_sets else [0.0] * N
            total_s = sum(s_list)
            if total_s > 0:
                ps = [si / total_s for si in s_list if si > 0]
                # Entropy H = -sum p_i ln p_i, normalized by ln(N)
                H = -sum(p * math.log(p) for p in ps)
                H_norm = (H / math.log(N)) if N > 1 else 1.0
                H_norm = max(0.0, min(1.0, H_norm))
                lv3 = 2.8 * H_norm
            else:
                lv3 = -INF

            _count_pass += 1
            total = float(lv1 + lv2 + lv3 + lv_bonus)

            print('=' * 50)
            print(lv1, lv2, lv3)
            print(_count_pass_lv1 / _count_total)
            print(_count_pass / _count_total)
            print('=' * 50)

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
                    )
                except Exception:
                    pass

            # Preview generations: print each agent's code and number of functions parsed
            try:
                preview_limit = 40000
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
                    # print(f"[agent_{aidx}] code:\n{snippet}", flush=True)
            except Exception:
                pass

            rewards.append(total)

        return rewards

    return reward_wrapper
