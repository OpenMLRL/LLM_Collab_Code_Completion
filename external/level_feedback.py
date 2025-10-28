from __future__ import annotations

from typing import Dict, List, Tuple

from LLM_Collab_Code_Completion.utils.parse_completion import (
    extract_method_snippets,
)
from LLM_Collab_Code_Completion.utils.merge import merge_methods_into_skeleton
from LLM_Collab_Code_Completion.rewards.CE_reward import run_unittests_with_details
from LLM_Collab_Code_Completion.utils.test_analysis import methods_called_per_test
from .common import (
    build_agent_context_block,
    build_take_job_context_block,
    join_previous_impls,
)


def _aggregate_prev_and_merged(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    completions: List[str],
) -> Tuple[List[List[str]], str]:
    """Return (prev_snippets_per_agent, combined_code) using union of parsed methods."""
    method_set = set(method_names or [])
    prev: List[List[str]] = []
    method_to_code: Dict[str, str] = {}
    for text in completions:
        parsed = extract_method_snippets(text or "", allowed_methods=method_set)
        vals = list(parsed.values())
        if not vals and (text or "").strip():
            vals = [(text or "").strip()]
        prev.append(vals)
        method_to_code.update(parsed)
    combined = merge_methods_into_skeleton(skeleton, class_name or "", method_to_code)
    return prev, combined


def format_followup_prompts(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
    test_code: str,
    original_prompt_flag: bool = True,
    previous_response_flag: bool = True,
    num_agents: int = 2,
) -> List[str]:
    """Diagnostics‑driven prompts: include syntax/tests results and per‑test hints."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    prev_per_agent, combined = _aggregate_prev_and_merged(
        skeleton, class_name, method_names, agent_completions
    )
    res = run_unittests_with_details(combined, test_code)
    syntax_ok = bool(res.get("syntax_ok", False))
    total = int(res.get("testsRun", 0))
    passed_n = int(res.get("passed", 0))
    test_details = res.get("test_results", []) or []

    # Map unittest IDs to called methods for targeted hints
    per_test_used = methods_called_per_test(
        test_code=test_code,
        candidate_methods=set(method_names or []),
        class_name=class_name or None,
    )

    # Build a short readable diagnostics block
    diag_lines: List[str] = []
    diag_lines.append(f"- Syntax: {'OK' if syntax_ok else 'ERROR'}")
    if total > 0:
        diag_lines.append(f"- Tests: {passed_n}/{total} passed")
        # Include at most a handful of failing cases with implicated methods
        fail_count = 0
        for td in test_details:
            if td.get("outcome") in ("failed", "error"):
                tid = str(td.get("id", ""))
                used = ", ".join(sorted(per_test_used.get(tid, set())))
                et = td.get("outcome")
                diag_lines.append(f"  - {tid}: {et}; methods: [{used}]")
                fail_count += 1
                if fail_count >= 4:
                    break
    else:
        diag_lines.append("- Tests: no test cases found")

    diag_block = "\n".join(diag_lines)

    for i in range(n):
        assigned = list(assignments.get(i, []) if assignments else [])
        if assignments and any(assignments.values()):
            base = build_agent_context_block(skeleton, class_name, assigned)
        else:
            base = build_take_job_context_block(
                skeleton=skeleton,
                class_name=class_name,
                method_names=list(method_names or []),
                num_agents=n,
            )

        parts: List[str] = []
        if original_prompt_flag:
            parts.extend([base, ""])  # context + blank
        if previous_response_flag:
            parts.extend([
                "Your previous implementation(s):",
                join_previous_impls(prev_per_agent[i]),
                "",
            ])

        parts.extend([
            "Diagnostics:",
            diag_block,
            "",
        ])

        methods = list(method_names or [])
        total_methods = len(methods)
        target_count = (total_methods + n - 1) // n if total_methods > 0 else 0
        if assigned:
            closing = (
                f"Revise your code. Implement your assigned {len(assigned)} method(s)."
            )
        else:
            closing = (
                f"Revise your code. Aim for ~{max(1, target_count)} method(s)."
            )
        parts.append(closing)
        prompts[i] = "\n".join(parts)

    return prompts
