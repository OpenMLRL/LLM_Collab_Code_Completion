from __future__ import annotations

from typing import Dict, List, Tuple, Optional

from LLM_Collab_Code_Completion.utils.prompting import build_take_job_prompt
from LLM_Collab_Code_Completion.utils.parse_completion import (
    extract_method_snippets,
)
from LLM_Collab_Code_Completion.utils.merge import (
    merge_methods_into_skeleton,
    build_method_map_with_syntax_selection,
)
from LLM_Collab_Code_Completion.rewards.CE_reward import run_unittests_with_details
from LLM_Collab_Code_Completion.utils.text_tools import (
    count_new_tokens,
    get_effective_max_new_tokens,
)


def _collect_names_and_merge(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    completions: List[str],
) -> Tuple[Dict[int, List[str]], str]:
    """Return (names_per_agent, combined_code) using union with syntax-aware selection.

    - names_per_agent[i] is the list of method names parsed from agent i's raw output.
    - combined_code is produced by merging selected implementations into the skeleton.
      Selection is done via build_method_map_with_syntax_selection to mirror reward logic.
    """
    method_set = set(method_names or [])

    # Parse method names per agent (names only, no bodies will be shared to others)
    names_per_agent: Dict[int, List[str]] = {}
    for idx, text in enumerate(completions):
        try:
            parsed = extract_method_snippets(text or "", allowed_methods=method_set)
        except Exception:
            parsed = {}
        names_per_agent[idx] = list(parsed.keys())

    # Build a partition mapping method -> agent when assignments are provided
    partition: Dict[str, int] = {}
    if assignments and any(assignments.values()):
        for aidx, names in assignments.items():
            for n in (names or []):
                partition[n] = int(aidx)

    # Self-select when no explicit assignments are provided
    self_select = not (assignments and any(assignments.values()))

    # Select one implementation per method mirroring reward's syntax-based selection
    try:
        method_to_code = build_method_map_with_syntax_selection(
            agent_texts=completions,
            method_names=method_names,
            partition=partition,
            self_select=self_select,
        )
    except Exception:
        method_to_code = {}

    combined = merge_methods_into_skeleton(skeleton, class_name or "", method_to_code)
    return names_per_agent, combined


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
    """Personal detailed feedback mode.

    For each agent i:
    - Provide TAKE_JOB-style base prompt (via build_take_job_prompt).
    - Show ONLY its own previous raw output (no other agents' code).
    - Report whether the processed merged output has a syntax error (reuse reward's compile check).
    - Report whether this agent's raw output likely hit the max new tokens limit (reuse token counter and limit source).
    - Show, for each agent, the count and names of methods they selected (names only, no code).
    - End with a reminder to revise code aiming for approximately target_count methods while minimizing overlap,
      and to avoid triple-quoted string comments.
    """
    n = int(num_agents)
    prompts: List[str] = [""] * n

    # Collect per-agent chosen names and build merged code to check syntax, mirroring reward path
    names_per_agent, combined = _collect_names_and_merge(
        skeleton, class_name, method_names, assignments, agent_completions
    )

    run_res = run_unittests_with_details(combined, test_code)
    syntax_ok = bool(run_res.get("syntax_ok", False))

    # Token limit reference used by reward function
    try:
        L = int(get_effective_max_new_tokens())
    except Exception:
        L = 512
    limit_ref = max(1, L - 1)  # reward clamps to [0, L-1]

    methods = list(method_names or [])
    total_methods = len(methods)
    target_count = (total_methods + n - 1) // n if total_methods > 0 else 0

    # Build per-agent prompts
    for i in range(n):
        # Base task instructions (TAKE_JOB variant)
        parts: List[str] = []
        if original_prompt_flag:
            base = build_take_job_prompt(
                skeleton=skeleton,
                class_name=class_name,
                method_names=methods,
                num_agents=n,
            )
            parts.extend([base, ""])  # context + blank line

        # Previous raw output for this agent only
        if previous_response_flag:
            raw_i = agent_completions[i] if i < len(agent_completions) else ""
            parts.extend([
                "Your previous raw output:",
                (raw_i if (raw_i or "").strip() else "<empty>"),
                "",
            ])

        # Processed output status (syntax + token usage)
        try:
            used_tokens = count_new_tokens(agent_completions[i] if i < len(agent_completions) else "")
        except Exception:
            used_tokens = len((agent_completions[i] or "").split()) if i < len(agent_completions) else 0
        reached_limit = used_tokens >= limit_ref
        parts.extend([
            "Processed output status:",
            f"- Syntax: {'OK' if syntax_ok else 'ERROR'}",
            f"- New tokens used: {used_tokens}/{limit_ref} (max)",
            f"- Reached max new token limit: {'Yes' if reached_limit else 'No'}",
            "",
        ])

        # Group summary: per-agent selected functions (names only)
        group_lines: List[str] = []
        for j in range(n):
            sel_names = names_per_agent.get(j, [])
            group_lines.append(
                f"- Agent {j}: {len(sel_names)} function(s): " + ("[" + ", ".join(sel_names) + "]" if sel_names else "[]")
            )
        parts.extend([
            "Agents’ selections:",
            "\n".join(group_lines),
            "",
        ])

        # Final reminders
        parts.extend([
            f"Revise your code. Aiming to implement approximately {max(1, target_count)} method(s) while minimizing overlap with method(s) selected for implementation by other agents.",
            'Avoid using triple-quoted string comments (""" ... """) inside your code.',
        ])

        prompts[i] = "\n".join(parts)

    return prompts

