"""
ClassEval reward computation utilities.

Implements a subprocess-based unittest runner that returns detailed per-test outcomes,
and a helper to run tests on combined code (skeleton merged with completions).

Scoring (computed in train_grpo.py reward wrapper):
- Syntax correctness: +3 if combined code compiles
- Pass ratio r: +5 * r
- Collaboration: 2 * (sum_test x * [test passed]) / (sum_test x)
  where x is the number of distinct agents involved in methods called by that test.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from typing import Any, Dict, List, Optional
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

    # Syntax check first
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
        os.makedirs(tmp_parent, exist_ok=True)
    except Exception:
        pass

    with tempfile.TemporaryDirectory(dir=tmp_parent) as tmpdir:
        py_path = os.path.join(tmpdir, "task_module_payload.py")
        with open(py_path, "w", encoding="utf-8") as fh:
            fh.write(combined_code)
        try:
            proc = subprocess.run(
                [sys.executable, "-c", runner_code, py_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                cwd=tmpdir,
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
