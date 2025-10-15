from __future__ import annotations

from typing import Dict, List

from LLM_Collab_Module_Completion.utils.parse_completion import (
    extract_method_snippets,
)
from .common import (
    build_agent_context_block,
    build_take_job_context_block,
    join_previous_impls,
)


def _per_agent_prev_snippets(
    completions: List[str],
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
) -> List[List[str]]:
    n = len(completions)
    method_set = set(method_names or [])
    out: List[List[str]] = [[] for _ in range(n)]
    def _truncate(text: str, limit: int = 4000) -> str:
        t = text or ""
        if len(t) <= limit:
            return t
        return t[:limit] + "\n... [TRUNCATED]"

    for i in range(n):
        text = completions[i] or ""
        allowed = set(assignments.get(i, []) or []) if assignments else method_set
        if not allowed:
            allowed = method_set
        parsed = extract_method_snippets(text, allowed_methods=allowed)
        vals = list(parsed.values())
        if not vals and text.strip():
            vals = [_truncate(text.strip())]
        out[i] = vals
    return out


def format_followup_prompts(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
    original_prompt_flag: bool = True,
    previous_response_flag: bool = True,
    num_agents: int = 2,
) -> List[str]:
    """Plain mode for ClassEval: include skeleton + previous implementations, no diagnostics."""
    n = int(num_agents)
    prompts: List[str] = [""] * n
    prev_funcs_per_agent = _per_agent_prev_snippets(agent_completions, method_names, assignments)

    for i in range(n):
        assigned = list(assignments.get(i, []) if assignments else [])
        # Choose appropriate context block
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
            parts.extend([base, ""])  # context + blank line

        if previous_response_flag:
            prev_text = join_previous_impls(prev_funcs_per_agent[i])
            parts.extend([
                "Your previous implementation(s):",
                prev_text,
                "",
            ])

        parts.append(
            "Revise ONLY the target methods. Output ONLY the function definition(s); no prose, no fences."
        )
        prompts[i] = "\n".join(parts)

    return prompts
