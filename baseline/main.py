#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single-turn evaluation on ClassEval dataset using a base LLM.

Features:
- Read config from config.yaml to select base model and data split.
- Prompt the base model with only the skeleton (no tests) to complete code.
- Strict output requirements: pure Python, no extra text or markdown fences.
- Concatenate generated code with the dataset's unittest code.
- Execute combined code in an isolated subprocess with timeout and collect pass/fail stats.
- Save concatenated code to output/codes/<task_id>.py and results JSON to output/.

Note:
- This script is designed to work offline if the dataset and models are in cache.
- If you need to run fully offline, ensure Hugging Face caches exist, or provide a local dataset path.
"""

import argparse
import json
import os
import re
import sys
import time
import textwrap
import traceback
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


def load_yaml(path: str) -> Dict[str, Any]:
    """Load YAML file with a safe fallback message if PyYAML is missing."""
    try:
        import yaml  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            f"PyYAML is required to read config.yaml. Please install pyyaml. Error: {e}"
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str) -> None:
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def now_iso() -> str:
    """Return current time in ISO format without microseconds."""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


@dataclass
class ModelConfig:
    name: str
    dtype: str = "auto"
    device_map: str = "auto"
    max_new_tokens: int = 4096
    temperature: float = 0.2
    top_p: float = 0.95
    top_k: int = 50
    do_sample: bool = True


@dataclass
class DataConfig:
    dataset_name: str = "FudanSELab/ClassEval"
    split: str = "auto"  # auto | train | validation | test
    limit: int = 50       # -1 for all
    task_ids: Optional[List[Any]] = None


@dataclass
class EvalConfig:
    timeout_seconds: int = 30
    save_generated: bool = True


@dataclass
class OutputConfig:
    dir: str = "baseline/output"


def parse_config(cfg_path: str) -> Dict[str, Any]:
    cfg = load_yaml(cfg_path)
    model = ModelConfig(**cfg.get("model", {}))
    data = DataConfig(**cfg.get("data", {}))
    eval_cfg = EvalConfig(**cfg.get("eval", {}))
    out = OutputConfig(**cfg.get("output", {}))
    return {
        "model": model,
        "data": data,
        "eval": eval_cfg,
        "output": out,
    }


def select_split(dataset_name: str, split: str):
    """Resolve dataset split. If split == auto, probe common splits in order."""
    from datasets import load_dataset  # type: ignore

    if split != "auto":
        return load_dataset(dataset_name, split=split)

    for candidate in ("test", "validation", "dev", "train"):
        try:
            return load_dataset(dataset_name, split=candidate)
        except Exception:
            continue
    # Fallback to default builder (may be entire dataset)
    try:
        ds = load_dataset(dataset_name)
        # Try a common key order if available
        for key in ("test", "validation", "dev", "train"):
            if key in ds:
                return ds[key]
        # Else take the first split
        return next(iter(ds.values()))
    except Exception as e:
        raise RuntimeError(f"Failed to load dataset '{dataset_name}': {e}")


def load_classeval_dataset(dataset_name: str, split: str):
    """Load ClassEval dataset split."""
    try:
        ds = select_split(dataset_name, split)
    except Exception as e:
        raise
    return ds


def build_prompt(skeleton: str) -> str:
    """Build the instruction prompt given a skeleton.

    The prompt strictly instructs the model to output only pure Python code.
    """
    instructions = textwrap.dedent(
        """
        You are a Python coding assistant.

        Task: Complete the following Python skeleton so that it fully implements the described behavior.
        Only fill in or add executable Python code that makes the implementation correct. Do not include any test code.

        Output constraints (must follow exactly):
        - You must only generate pure Python code without any other words (your output must be executable Python code).
        - Do NOT include markdown code blocks (```python)
        - Do NOT include any text before or after the code (no explanations, no comments outside the code).
        - Do NOT include print statements unless required by the skeleton's behavior.
        - Do NOT remove or alter the given imports unless necessary.

        Provide only the completed Python code for the skeleton below.
        """
    ).strip()

    # Delimit the skeleton clearly without implying markdown code fences
    prompt = (
        instructions
        + "\n\nSKELETON START\n" + skeleton.strip() + "\nSKELETON END\n\n"
        + "Return only the completed Python code that replaces the skeleton above."
    )
    return prompt


def _get_torch_dtype(dtype_str: str):
    """Map string to torch dtype."""
    import torch  # type: ignore

    mapping = {
        "auto": None,
        "float16": torch.float16,
        "fp16": torch.float16,
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float32": torch.float32,
        "fp32": torch.float32,
    }
    if dtype_str not in mapping:
        return None
    return mapping[dtype_str]


class LMGenerator:
    """Wrap a HF Transformers causal LM for text generation."""

    def __init__(self, cfg: ModelConfig):
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

        trust_remote_code = True  # Qwen family may require custom code
        torch_dtype = _get_torch_dtype(cfg.dtype)

        self.tokenizer = AutoTokenizer.from_pretrained(
            cfg.name, trust_remote_code=trust_remote_code
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            cfg.name,
            trust_remote_code=trust_remote_code,
            torch_dtype=torch_dtype,
            device_map=cfg.device_map,
        )
        self.cfg = cfg

        # Ensure EOS token is set for clean stopping
        self.eos_token_id = self.tokenizer.eos_token_id

    def generate(self, prompt: str) -> str:
        import torch  # type: ignore

        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=True)
        input_ids = inputs["input_ids"].to(self.model.device)
        attention_mask = inputs.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.model.device)

        gen_kwargs = {
            "max_new_tokens": self.cfg.max_new_tokens,
            "do_sample": self.cfg.do_sample,
            "temperature": self.cfg.temperature,
            "top_p": self.cfg.top_p,
            "top_k": self.cfg.top_k,
            "eos_token_id": self.eos_token_id,
            "pad_token_id": self.tokenizer.eos_token_id,
        }

        with torch.no_grad():
            if attention_mask is not None:
                outputs = self.model.generate(input_ids=input_ids, attention_mask=attention_mask, **gen_kwargs)
            else:
                outputs = self.model.generate(input_ids=input_ids, **gen_kwargs)

        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt prefix
        if text.startswith(prompt):
            text = text[len(prompt):]
        return text.strip()


def extract_pure_python(text: str) -> str:
    """Post-process model output to enforce pure Python code.

    - Remove markdown-style code fences if present.
    - Strip any leading/trailing non-code commentary if fences are present.
    - Otherwise, return the raw text stripped.
    """
    s = text.strip()
    # Normalize potential Windows newlines
    s = s.replace("\r\n", "\n")

    if "```" in s:
        # Extract content within the outermost triple backticks
        parts = re.split(r"```+", s)
        # parts may look like: ['', 'python', 'code', ''] or ['', 'code', '']
        extracted = None
        for i in range(len(parts) - 1):
            body = parts[i + 1]
            # Skip a 'python' language tag line if present
            if body.lstrip().lower().startswith("python\n"):
                body = body.split("\n", 1)[1] if "\n" in body else ""
            if body.strip():
                extracted = body
                break
        if extracted is None:
            extracted = s
        s = extracted

    # Strip any leading explanatory lines that start with common phrases
    # but keep this conservative to avoid trimming valid code.
    leading_noise_patterns = [
        r"^Here is the",
        r"^The solution",
        r"^Answer:",
        r"^Implementation:",
    ]
    lines = s.split("\n")
    while lines and any(re.match(p, lines[0], flags=re.IGNORECASE) for p in leading_noise_patterns):
        lines.pop(0)
    s = "\n".join(lines).strip()

    return s


def write_combined_code(out_code_path: str, code: str, test_code: str) -> None:
    """Write the concatenated implementation and unittest code to a file."""
    combined = code.rstrip() + "\n\n" + test_code.lstrip()
    with open(out_code_path, "w", encoding="utf-8") as f:
        f.write(combined)


def run_unittests_in_subprocess(py_file: str, timeout: int) -> Dict[str, Any]:
    """Run unittests from a module file in a sandboxed subprocess with timeout.

    The subprocess imports the module, discovers tests via unittest loader,
    runs them with TextTestRunner, and prints a single JSON line to stdout.
    All test runner output and print statements are captured into the JSON.
    """
    runner_code = """
import json, sys, importlib.util, unittest, io, time, traceback, contextlib

start = time.time()
py_file = sys.argv[1]
spec = importlib.util.spec_from_file_location("task_module", py_file)
mod = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(mod)
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        res = runner.run(suite)
    out = stream.getvalue()
    result = dict(
        testsRun=res.testsRun,
        failures=len(res.failures),
        errors=len(res.errors),
        skipped=len(res.skipped),
        passed=res.testsRun - len(res.failures) - len(res.errors) - len(res.skipped),
        success=res.wasSuccessful(),
        duration=time.time() - start,
        output=out,
    )
    print(json.dumps(result))
except SystemExit as e:
    # Some tests may call sys.exit; treat as error
    tb = traceback.format_exc()
    print(json.dumps({"exception": "SystemExit", "code": getattr(e, 'code', None), "traceback": tb}))
    sys.exit(3)
except Exception as e:
    tb = traceback.format_exc()
    print(json.dumps({"exception": str(e), "traceback": tb}))
    sys.exit(2)
"""

    try:
        proc = subprocess.run(
            [sys.executable, "-c", runner_code, py_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "timeout": True,
            "success": False,
            "testsRun": 0,
            "failures": 0,
            "errors": 1,
            "skipped": 0,
            "passed": 0,
            "duration": timeout,
            "stdout": "",
            "stderr": "TimeoutExpired",
            "exit_code": None,
        }

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()

    result: Dict[str, Any]
    try:
        result = json.loads(stdout) if stdout else {}
        # Merge metadata
        result.update({
            "timeout": False,
            "exit_code": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
        })
    except json.JSONDecodeError:
        # If JSON parsing fails, report raw outputs
        result = {
            "timeout": False,
            "success": False,
            "testsRun": 0,
            "failures": 0,
            "errors": 1,
            "skipped": 0,
            "passed": 0,
            "duration": None,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode,
            "parse_error": True,
        }

    return result


def sanitize_model_name(name: str) -> str:
    """Sanitize model name for filenames."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def main():
    parser = argparse.ArgumentParser(description="Evaluate base LLM on ClassEval (single-turn)")
    parser.add_argument("--config", type=str, default=os.path.join(os.path.dirname(__file__), "config.yaml"))
    parser.add_argument("--limit", type=int, default=None, help="Override limit from config")
    parser.add_argument("--tasks", type=str, default=None, help="Comma-separated task_ids to run (overrides config)")
    parser.add_argument("--offline", action="store_true", help="Set HF_HUB_OFFLINE=1 for offline mode")
    args = parser.parse_args()

    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"

    cfg = parse_config(args.config)
    model_cfg: ModelConfig = cfg["model"]
    data_cfg: DataConfig = cfg["data"]
    eval_cfg: EvalConfig = cfg["eval"]
    out_cfg: OutputConfig = cfg["output"]

    # CLI overrides
    if args.limit is not None:
        data_cfg.limit = args.limit
    if args.tasks:
        data_cfg.task_ids = [t.strip() for t in args.tasks.split(",") if t.strip()]

    # Prepare outputs
    output_dir = out_cfg.dir
    codes_dir = os.path.join(output_dir, "codes")
    ensure_dir(output_dir)
    ensure_dir(codes_dir)

    # Load dataset
    print(f"[{now_iso()}] Loading dataset: {data_cfg.dataset_name} (split={data_cfg.split})")
    try:
        ds = load_classeval_dataset(data_cfg.dataset_name, data_cfg.split)
    except Exception as e:
        print(f"Failed to load dataset '{data_cfg.dataset_name}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[{now_iso()}] Dataset size: {len(ds)}")

    # Build index by task_id for selection if needed
    id_to_item: Dict[str, Any] = {}
    ds_list: List[Any] = list(ds)
    for it in ds_list:
        tid = str(it.get("task_id", "")).strip()
        if tid:
            id_to_item[tid] = it

    def resolve_one(tid_raw: Any) -> Optional[Any]:
        # Accept exact task_id, numeric index, or auto-map numeric to ClassEval_<n>
        s = str(tid_raw).strip()
        if s in id_to_item:
            return id_to_item[s]
        # If looks like digits, try index or prefixed id
        if s.isdigit():
            n = int(s)
            # Prefer matching prefixed id if exists
            pref = f"ClassEval_{n}"
            if pref in id_to_item:
                return id_to_item[pref]
            # Fall back to index in dataset
            if 0 <= n < len(ds_list):
                return ds_list[n]
        # If already in form ClassEval_<n> but not found, try parsing and fallback to index
        m = re.match(r"^ClassEval[_-](\d+)$", s)
        if m:
            n = int(m.group(1))
            if 0 <= n < len(ds_list):
                return ds_list[n]
        return None

    # Select items
    items: List[Any] = []
    if data_cfg.task_ids:
        for tid in data_cfg.task_ids:
            it = resolve_one(tid)
            if it is not None:
                items.append(it)
            else:
                print(f"Warning: task_id/index '{tid}' not found; skipping.")
    else:
        items = ds_list
        if data_cfg.limit is not None and data_cfg.limit >= 0:
            items = items[: data_cfg.limit]

    if not items:
        print("No items selected for evaluation.", file=sys.stderr)
        sys.exit(1)

    # Load model
    print(f"[{now_iso()}] Loading model: {model_cfg.name}")
    try:
        generator = LMGenerator(model_cfg)
    except Exception as e:
        print(f"Failed to load model '{model_cfg.name}': {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    # Evaluate items
    results: List[Dict[str, Any]] = []

    for idx, item in enumerate(items):
        task_id = str(item.get("task_id", f"idx_{idx}"))
        skeleton = item.get("skeleton")
        test_code = item.get("test")

        if not isinstance(skeleton, str) or not isinstance(test_code, str):
            print(f"[{now_iso()}] Skipping task {task_id}: missing skeleton or test.")
            continue

        print(f"[{now_iso()}] [{idx+1}/{len(items)}] Generating for task_id={task_id} ...")
        prompt = build_prompt(skeleton)
        raw_output = generator.generate(prompt)
        code = extract_pure_python(raw_output)

        # Optionally save generated-only code
        if eval_cfg.save_generated:
            gen_only_path = os.path.join(codes_dir, f"{task_id}__gen_only.py")
            try:
                with open(gen_only_path, "w", encoding="utf-8") as f:
                    f.write(code)
            except Exception as e:
                print(f"Warning: failed to write generated-only code for {task_id}: {e}")

        # Write combined code to file
        out_file = os.path.join(codes_dir, f"{task_id}.py")
        try:
            write_combined_code(out_file, code, test_code)
        except Exception as e:
            print(f"Failed to write combined code for {task_id}: {e}", file=sys.stderr)
            continue

        # Run unit tests with timeout
        res = run_unittests_in_subprocess(out_file, timeout=eval_cfg.timeout_seconds)
        res.update({
            "task_id": task_id,
            "code_path": os.path.relpath(out_file),
        })
        results.append(res)

        status = "PASS" if res.get("success") else "FAIL"
        print(
            f"[{now_iso()}] Result {status} | testsRun={res.get('testsRun')} "
            f"passed={res.get('passed')} failures={res.get('failures')} errors={res.get('errors')} timeout={res.get('timeout')}"
        )

    # Aggregate
    total = len(results)
    passed_all = sum(1 for r in results if r.get("success"))
    pass_rate = (passed_all / total) if total > 0 else 0.0

    summary = {
        "timestamp": now_iso(),
        "model_name": model_cfg.name,
        "dataset": data_cfg.dataset_name,
        "split": data_cfg.split,
        "num_evaluated": total,
        "num_passed_all": passed_all,
        "pass_rate": pass_rate,
        "timeout_seconds": eval_cfg.timeout_seconds,
        "results": results,
    }

    # Save results JSON
    model_stub = sanitize_model_name(model_cfg.name)
    out_json = os.path.join(output_dir, f"eval_results_{model_stub}.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[{now_iso()}] Saved results to {out_json}")


if __name__ == "__main__":
    main()
