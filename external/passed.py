from __future__ import annotations

from typing import Dict, List, Optional

import textwrap

from LLM_Collab_Code_Completion.rewards.CE_reward import run_unittests_with_details
from LLM_Collab_Code_Completion.utils.merge import (
    build_method_map_with_syntax_selection,
    merge_methods_into_skeleton,
)
from LLM_Collab_Code_Completion.utils.parse_completion import extract_method_snippets
from .common import (
    build_agent_context_block,
    build_take_job_context_block,
    join_previous_impls,
    render_history_block_for_agent,
)


def _per_agent_prev_snippets(
    completions: List[str],
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
) -> List[List[str]]:
    """Parse previous implementation snippets per agent."""
    n = len(completions)
    method_set = set(method_names or [])
    out: List[List[str]] = [[] for _ in range(n)]
    for i in range(n):
        text = completions[i] or ""
        allowed = set(assignments.get(i, []) or []) if assignments else method_set
        if not allowed:
            allowed = method_set
        parsed = extract_method_snippets(text, allowed_methods=allowed)
        vals = list(parsed.values())
        if not vals and text.strip():
            vals = [text.strip()]
        out[i] = vals
    return out


def _build_combined_code(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    completions: List[str],
) -> str:
    """Merge selected implementations into the skeleton following reward logic."""
    partition: Dict[str, int] = {}
    if assignments and any(assignments.values()):
        for aidx, names in assignments.items():
            for name in (names or []):
                partition[name] = int(aidx)
    self_select = not (assignments and any(assignments.values()))
    try:
        method_to_code = build_method_map_with_syntax_selection(
            agent_texts=completions,
            method_names=method_names,
            partition=partition,
            self_select=self_select,
        )
    except Exception:
        method_to_code = {}

    try:
        merged = merge_methods_into_skeleton(
            skeleton=skeleton,
            class_name=class_name or "",
            method_to_code=method_to_code,
        )
    except Exception:
        merged = skeleton or ""
    return merged


def _format_test_summary(run_res: Dict[str, object]) -> List[str]:
    syntax_ok = bool(run_res.get("syntax_ok", False))
    timeout = bool(run_res.get("timeout", False))
    tests_run = int(run_res.get("testsRun") or 0)
    passed_cnt = int(run_res.get("passed") or 0)
    details = run_res.get("test_results") or []
    failed_ids: List[str] = []
    passed_ids: List[str] = []
    if isinstance(details, list):
        for item in details:
            try:
                outcome = str(item.get("outcome", ""))
                case_id = str(item.get("id", ""))
            except Exception:
                continue
            if outcome == "passed":
                passed_ids.append(case_id)
            elif case_id:
                failed_ids.append(case_id)
    lines = [
        "Hidden tests summary:",
        f"- Syntax check: {'OK' if syntax_ok else 'ERROR'}",
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
    elif passed_ids:
        preview = ", ".join(passed_ids[:5])
        lines.append(f"- Passing cases: {preview}")

    lines.append("")
    return lines


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
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
) -> List[str]:
    """TAKE_JOB-style prompt with aggregate hidden-test feedback."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    prev_snippets = _per_agent_prev_snippets(agent_completions, method_names, assignments)
    combined_code = _build_combined_code(
        skeleton,
        class_name or "",
        method_names,
        assignments,
        agent_completions,
    )
    run_res = run_unittests_with_details(combined_code, test_code)
    test_summary = _format_test_summary(run_res)

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
        hist = render_history_block_for_agent(
            i,
            prompt_history_per_agent=prompt_history_per_agent,
            response_history_per_agent=response_history_per_agent,
        )
        if hist:
            parts.extend([hist, ""])
        if original_prompt_flag:
            parts.extend([base, ""])

        parts.extend(test_summary)

        if previous_response_flag:
            prev_text = join_previous_impls(prev_snippets[i])
            parts.extend(
                [
                    "Your previous implementation(s):",
                    prev_text,
                    "",
                ]
            )

        closing = textwrap.dedent(
            """
            Revise your code to fix the failing cases while preserving every provided method signature.
            Output ONLY the Python function definitions you are responsible for—no class header, no prose.
            """
        ).strip()
        parts.append(closing)
        prompts[i] = "\n".join(parts).strip()

    return prompts
