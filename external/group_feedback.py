from __future__ import annotations

from typing import Dict, List, Tuple

from LLM_Collab_Code_Completion.utils.parse_completion import (
    extract_method_snippets,
)
from LLM_Collab_Code_Completion.utils.merge import merge_methods_into_skeleton
from LLM_Collab_Code_Completion.rewards.CE_reward import run_unittests_with_details
from .common import (
    build_agent_context_block,
    build_take_job_context_block,
    join_previous_impls,
)


def _aggregate_group_state(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    completions: List[str],
) -> Tuple[List[List[str]], Dict[int, List[str]], str]:
    """Collect per-agent parsed functions, name lists, and merged combined code.

    Returns (prev_snippets_per_agent, names_per_agent, combined_code).
    """
    method_set = set(method_names or [])
    prev_per_agent: List[List[str]] = []
    names_per_agent: Dict[int, List[str]] = {}
    method_to_code: Dict[str, str] = {}

    for idx, text in enumerate(completions):
        parsed = extract_method_snippets(text or "", allowed_methods=method_set)
        vals = list(parsed.values())
        if not vals and (text or "").strip():
            vals = [(text or "").strip()]
        prev_per_agent.append(vals)
        names_per_agent[idx] = list(parsed.keys())
        method_to_code.update(parsed)

    combined = merge_methods_into_skeleton(skeleton, class_name or "", method_to_code)
    return prev_per_agent, names_per_agent, combined


def _identity_block(text: str) -> Tuple[str, bool]:
    """Return text as-is without truncation."""
    if not isinstance(text, str):
        return "", False
    return text, False


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
    """Group feedback mode: show merged code snapshot, per-agent counts, and test signals."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    prev_per_agent, names_per_agent, combined = _aggregate_group_state(
        skeleton, class_name, method_names, agent_completions
    )
    res = run_unittests_with_details(combined, test_code)
    syntax_ok = bool(res.get("syntax_ok", False))
    total = int(res.get("testsRun", 0))
    passed_n = int(res.get("passed", 0))
    tests_line = (
        f"- Tests: {passed_n}/{total} passed" if total > 0 else "- Tests: no test cases found"
    )
    syntax_line = f"- Syntax: {'OK' if syntax_ok else 'ERROR'}"

    # Build a short group summary of function counts by agent
    group_lines: List[str] = []
    for i in range(n):
        names = names_per_agent.get(i, [])
        group_lines.append(f"- Agent {i}: {len(names)} function(s)")
    group_summary = "\n".join(group_lines)

    combined_view, _ = _identity_block(combined)
    combined_block = f"COMBINED CODE START\n{combined_view}\nCOMBINED CODE END"

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

        # Group summary: who produced how many functions
        parts.extend([
            "Group summary:",
            group_summary,
            "",
            "Overall status:",
            syntax_line,
            tests_line,
            "",
            combined_block,
            "",
        ])

        if previous_response_flag:
            parts.extend([
                "Your previous implementation(s):",
                join_previous_impls(prev_per_agent[i]),
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
