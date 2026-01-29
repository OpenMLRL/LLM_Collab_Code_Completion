from __future__ import annotations

from typing import Dict, List, Optional

import textwrap

from LLM_Collab_Code_Completion.rewards.CE_reward import run_unittests_with_details
from LLM_Collab_Code_Completion.utils.merge import (
    build_method_map_with_syntax_selection,
    merge_methods_into_skeleton,
)
from .common import render_history_block_for_agent


def _build_combined_code(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
) -> str:
    partition: Dict[str, int] = {}
    if assignments and any(assignments.values()):
        for aidx, names in assignments.items():
            for name in (names or []):
                partition[name] = int(aidx)

    self_select = not (assignments and any(assignments.values()))

    try:
        method_to_code = build_method_map_with_syntax_selection(
            agent_texts=agent_completions,
            method_names=method_names,
            partition=partition,
            self_select=self_select,
        )
    except Exception:
        method_to_code = {}

    try:
        return merge_methods_into_skeleton(
            skeleton,
            class_name or "",
            method_to_code,
        )
    except Exception:
        return skeleton or ""


def _format_test_summary(run_res: Dict[str, object]) -> List[str]:
    syntax_ok = bool(run_res.get("syntax_ok", False))
    timeout = bool(run_res.get("timeout", False))
    tests_run = int(run_res.get("testsRun") or 0)
    passed_cnt = int(run_res.get("passed") or 0)
    details = run_res.get("test_results") or []
    failed_ids: List[str] = []
    if isinstance(details, list):
        for item in details:
            try:
                outcome = str(item.get("outcome", ""))
                case_id = str(item.get("id", ""))
            except Exception:
                continue
            if outcome != "passed" and case_id:
                failed_ids.append(case_id)
    lines = [
        "Diagnostics:",
        f"- Syntax: {'OK' if syntax_ok else 'ERROR'}",
    ]
    if timeout:
        lines.append("- Test runner timed out before completion.")
    if syntax_ok and tests_run > 0:
        lines.append(f"- Hidden tests passed: {passed_cnt}/{tests_run}")
    elif tests_run == 0:
        lines.append("- Hidden tests not available or not executed.")
    else:
        lines.append("- Hidden tests skipped due to syntax failure.")

    if failed_ids:
        preview = ", ".join(failed_ids[:5])
        more = len(failed_ids) - 5
        suffix = f" (+{more} more)" if more > 0 else ""
        lines.append(f"- Failing cases: {preview}{suffix}")
    lines.append("")
    return lines


def format_followup_prompts(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
    test_code: str,
    num_agents: int = 2,
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
    original_prompt_flag: bool = True,
    previous_response_flag: bool = True,
) -> List[str]:
    """Revision prompt with history + syntax/test summary (no assignment hints)."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    combined_code = _build_combined_code(
        skeleton,
        class_name or "",
        method_names,
        assignments,
        agent_completions,
    )
    run_res = run_unittests_with_details(combined_code, test_code)
    test_summary = _format_test_summary(run_res)

    if prompt_history_per_agent is None:
        prompt_history_per_agent = [[] for _ in range(n)]
    if response_history_per_agent is None:
        response_history_per_agent = [[] for _ in range(n)]
    has_assignments = bool(assignments and any(assignments.values()))

    def _allowed_methods_for_agent(agent_idx: int) -> List[str]:
        if has_assignments:
            return list((assignments or {}).get(agent_idx, []))
        return list(method_names or [])

    skeleton_block = textwrap.dedent(
        f"""
        Class skeleton reference for '{class_name or "unknown"}':
        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()

    for idx in range(n):
        sections: List[str] = []
        sections.append(
            "Review the history and diagnostics below. Keep every method signature unchanged and produce only the improved implementation."
        )
        hist = render_history_block_for_agent(
            idx,
            prompt_history_per_agent=prompt_history_per_agent,
            response_history_per_agent=response_history_per_agent,
            include_original_prompt=original_prompt_flag,
            include_previous_response=previous_response_flag,
            allowed_methods=_allowed_methods_for_agent(idx),
        )
        if hist:
            sections.extend([hist, ""])

        sections.extend([skeleton_block, ""])

        sections.extend(test_summary)

        sections.extend(
            [
                "Respond with ONLY your revised implementation enclosed in a single ```python ...``` block.",
                "Do not add explanations, tests, or any text outside that fence.",
            ]
        )

        prompts[idx] = "\n".join(sections).strip()

    return prompts
