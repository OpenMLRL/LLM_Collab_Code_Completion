from __future__ import annotations

from typing import Dict, List, Tuple

from LLM_Collab_Module_Completion.utils.parse_completion import (
    extract_method_snippets,
)
from LLM_Collab_Module_Completion.utils.merge import merge_methods_into_skeleton
from LLM_Collab_Module_Completion.rewards.CE_reward import run_unittests_with_details
from .common import (
    build_agent_context_block,
    build_take_job_context_block,
)


def _collect_counts_and_merge(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    completions: List[str],
) -> Tuple[Dict[int, List[str]], str]:
    """Return (names_per_agent, combined_code) using union over parsed methods.

    names_per_agent maps agent index -> list of parsed method names from its raw text.
    """
    method_set = set(method_names or [])
    names_per_agent: Dict[int, List[str]] = {}
    method_to_code: Dict[str, str] = {}
    for idx, text in enumerate(completions):
        parsed = extract_method_snippets(text or "", allowed_methods=method_set)
        names_per_agent[idx] = list(parsed.keys())
        method_to_code.update(parsed)
    combined = merge_methods_into_skeleton(skeleton, class_name or "", method_to_code)
    return names_per_agent, combined


def _identity_raw(text: str) -> tuple[str, bool]:
    """Return raw output as-is without truncation."""
    s = text or ""
    return s, False


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
    """Personal feedback mode.

    For each agent i:
    - Show: "You are agent i of N".
    - Show per-agent counts for all agents (numbers only).
    - Show overall Syntax OK/ERROR and test pass ratio based on merged code.
    - If enabled, show that agent's previous raw output (unprocessed), truncated only for safety.
    - End with strict output rules reminder to output ONLY target function definitions.
    """
    n = int(num_agents)
    prompts: List[str] = [""] * n

    names_per_agent, combined = _collect_counts_and_merge(
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

    # Build counts summary (numbers only, no other agents' code)
    group_lines: List[str] = []
    for i in range(n):
        names = names_per_agent.get(i, [])
        group_lines.append(f"- Agent {i}: {len(names)} function(s)")
    group_summary = "\n".join(group_lines)

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

        parts.extend([
            f"You are agent {i} of {n}.",
            "Group summary:",
            group_summary,
            "",
            "Overall status:",
            syntax_line,
            tests_line,
            "",
        ])

        if previous_response_flag:
            raw_i = agent_completions[i] if i < len(agent_completions) else ""
            raw_view, _ = _identity_raw(raw_i or "")
            parts.extend([
                "Your previous raw output:",
                raw_view if raw_view.strip() else "<empty>",
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
