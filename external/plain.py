from __future__ import annotations

from typing import Dict, List, Optional

from LLM_Collab_Code_Completion.utils.parse_completion import (
    extract_method_snippets,
)
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


def format_followup_prompts(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
    original_prompt_flag: bool = True,
    previous_response_flag: bool = True,
    num_agents: int = 2,
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
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
        # Always include full per-agent history (CoMLRL now defaults to full history)
        hist = render_history_block_for_agent(
            i,
            prompt_history_per_agent=prompt_history_per_agent,
            response_history_per_agent=response_history_per_agent,
        )
        if hist:
            parts.extend([hist, ""])  # history + blank line
        if original_prompt_flag:
            parts.extend([base, ""])  # context + blank line

        if previous_response_flag:
            prev_text = join_previous_impls(prev_funcs_per_agent[i])
            parts.extend([
                "Your previous implementation(s):",
                prev_text,
                "",
            ])

        # Closing reminder: concise + rough count
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
