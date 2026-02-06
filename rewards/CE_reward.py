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
import copy
import hashlib
import subprocess
import sys
import tempfile
from collections import OrderedDict
from typing import Any, Dict, List, Set
import io
import os

VERBOSE = True
TEST_TIMEOUT: float = 40.0
MAX_TIMEOUTS: int = 3
SUBPROCESS_TIMEOUT: float = TEST_TIMEOUT * max(1, MAX_TIMEOUTS) + 5.0
TEST_CACHE_MAX: int = 256
_TEST_CACHE: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
EVAL_LOG_EVERY: int | None = None
_EVAL_LV1: List[float] = []
_EVAL_LV2: List[float] = []
_EVAL_LV3: List[float] = []
_EVAL_TOTAL: List[float] = []


def reset_eval_log_state() -> None:
    _EVAL_LV1.clear()
    _EVAL_LV2.clear()
    _EVAL_LV3.clear()
    _EVAL_TOTAL.clear()



def _combine_code(impl_code: str, test_code: str) -> str:
    return (impl_code or "").rstrip() + "\n\n" + (test_code or "").lstrip()


def run_unittests_with_details(
    impl_code: str, test_code: str, timeout: float | None = None
) -> Dict[str, Any]:
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
    timeout_val = SUBPROCESS_TIMEOUT if timeout is None else float(timeout)
    cache_key = _make_test_cache_key(combined_code, test_code, timeout_val)
    cached = _cache_get_result(cache_key)
    if cached is not None:
        return cached

    # Syntax check first (no formatting here; formatting is applied upstream after merge)
    try:
        compile(combined_code, "<combined>", "exec")
        syntax_ok = True
    except Exception as e:
        syntax_ok = False
        # Early return: do not run tests when syntax is invalid
        res = {
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
        _cache_set_result(cache_key, res)
        return res

    runner_code = """
import json, sys, importlib.util, unittest, io, time, traceback, contextlib, os, signal

TEST_TIMEOUT = float(os.getenv("CE_TEST_TIMEOUT", "40"))
MAX_TIMEOUTS = int(os.getenv("CE_MAX_TIMEOUTS", "3"))

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Test timed out")

def _set_timeout():
    if TEST_TIMEOUT <= 0:
        return
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        if hasattr(signal, "setitimer"):
            signal.setitimer(signal.ITIMER_REAL, TEST_TIMEOUT)
        else:
            signal.alarm(int(TEST_TIMEOUT))
    except Exception:
        return

def _clear_timeout():
    if TEST_TIMEOUT <= 0:
        return
    try:
        if hasattr(signal, "setitimer"):
            signal.setitimer(signal.ITIMER_REAL, 0)
        else:
            signal.alarm(0)
    except Exception:
        return

class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.timeout_count = 0
    def startTest(self, test):
        super().startTest(test)
        if MAX_TIMEOUTS > 0 and self.timeout_count >= MAX_TIMEOUTS:
            self.shouldStop = True
            return
        _set_timeout()
    def stopTest(self, test):
        _clear_timeout()
        super().stopTest(test)
    def addSuccess(self, test):
        _clear_timeout()
        super().addSuccess(test)
        self.records.append({"id": str(test), "outcome": "passed"})
    def addFailure(self, test, err):
        _clear_timeout()
        super().addFailure(test, err)
        self.records.append({"id": str(test), "outcome": "failed"})
    def addError(self, test, err):
        _clear_timeout()
        super().addError(test, err)
        outcome = "error"
        try:
            if err and isinstance(err, tuple) and err[0] is TimeoutException:
                outcome = "timeout"
                self.timeout_count += 1
        except Exception:
            outcome = "error"
        self.records.append({"id": str(test), "outcome": outcome})
        if MAX_TIMEOUTS > 0 and self.timeout_count >= MAX_TIMEOUTS:
            self.shouldStop = True
    def addSkip(self, test, reason):
        _clear_timeout()
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
        timeouts=getattr(res, "timeout_count", 0),
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
    tmp_parent = os.path.abspath(tmp_parent)
    os.makedirs(tmp_parent, exist_ok=True)
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
            env = os.environ.copy()
            env["CE_TEST_TIMEOUT"] = str(TEST_TIMEOUT)
            env["CE_MAX_TIMEOUTS"] = str(MAX_TIMEOUTS)
            proc = subprocess.run(
                [sys.executable, "-c", runner_code, payload_name],
                capture_output=True,
                text=True,
                timeout=timeout_val,
                check=False,
                cwd=tmpdir_abs,
                env=env,
            )
        except subprocess.TimeoutExpired:
            res = {
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
            _cache_set_result(cache_key, res)
            return res

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
    _cache_set_result(cache_key, res)
    return res


# ---------- Reward Factory (multi-agent merge + scoring) ----------
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
            example = batch_items[i] if batch_items is not None else {}
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

            # Optional eval logging (mean metrics per eval sweep)
            try:
                phase = str(example.get("phase", "")).lower() if isinstance(example, dict) else ""
            except Exception:
                phase = ""
            is_eval = phase == "eval"

            if VERBOSE and is_eval:
                print("=" * 50)
                print(lv1, lv2, lv3)
            if is_eval:
                _EVAL_LV1.append(float(lv1))
                _EVAL_LV2.append(float(lv2))
                _EVAL_LV3.append(float(lv3))
                _EVAL_TOTAL.append(float(total))
                should_log = False
                if EVAL_LOG_EVERY is None or EVAL_LOG_EVERY <= 0:
                    should_log = True
                elif len(_EVAL_LV1) >= int(EVAL_LOG_EVERY):
                    should_log = True
                if should_log:
                    def _mean(xs: List[float]) -> float:
                        return float(sum(xs) / len(xs)) if xs else 0.0
                    RewardLogger.log(
                        {
                            "eval/ce_reward/level1_syntax": _mean(_EVAL_LV1),
                            "eval/ce_reward/level2_tests": _mean(_EVAL_LV2),
                            "eval/ce_reward/level3_overlap_penalty": _mean(_EVAL_LV3),
                            "eval/ce_reward/total": _mean(_EVAL_TOTAL),
                        },
                        step=None,
                        commit=False,
                    )
                    reset_eval_log_state()
            if VERBOSE and is_eval:
                # Preview generations: print each agent's code and number of functions parsed
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
                print("=" * 50)

            rewards.append(total)

        return rewards

    return reward_wrapper
def _make_test_cache_key(impl_code: str, test_code: str, timeout_val: float) -> str:
    h = hashlib.sha256()
    h.update(str(TEST_TIMEOUT).encode("utf-8"))
    h.update(b"\0")
    h.update(str(MAX_TIMEOUTS).encode("utf-8"))
    h.update(b"\0")
    h.update(str(timeout_val).encode("utf-8"))
    h.update(b"\0")
    h.update((impl_code or "").encode("utf-8", errors="ignore"))
    h.update(b"\0")
    h.update((test_code or "").encode("utf-8", errors="ignore"))
    return h.hexdigest()


def _cache_get_result(key: str) -> Dict[str, Any] | None:
    cached = _TEST_CACHE.get(key)
    if cached is None:
        return None
    _TEST_CACHE.move_to_end(key)
    return copy.deepcopy(cached)


def _cache_set_result(key: str, value: Dict[str, Any]) -> None:
    if TEST_CACHE_MAX <= 0:
        return
    _TEST_CACHE[key] = copy.deepcopy(value)
    _TEST_CACHE.move_to_end(key)
    if len(_TEST_CACHE) > TEST_CACHE_MAX:
        _TEST_CACHE.popitem(last=False)
