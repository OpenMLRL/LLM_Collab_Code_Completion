from __future__ import annotations

from typing import Iterable, List, Optional

from LLM_Collab_Code_Completion.utils.parse_completion import extract_method_snippets


def _filter_response_to_methods(response: str, allowed_methods: Iterable[str]) -> str:
    try:
        snippets = extract_method_snippets(response or "", allowed_methods=allowed_methods)
    except Exception:
        snippets = {}
    if not snippets:
        return ""
    return "\n\n".join(snippets.values()).strip()


def render_history_block_for_agent(
    agent_idx: int,
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
    include_original_prompt: bool = True,
    include_previous_response: bool = True,
    allowed_methods: Optional[Iterable[str]] = None,
) -> str:
    """Render a readable history block for one agent.

    - Lists all previous prompts for that agent (Turn 1..T)
    - Lists all previous responses for that agent (Turn 1..T)
    - Optionally filters responses to allowed method definitions only
    Returns an empty string if there is no history.
    """
    lines: List[str] = []
    allowed_methods_list = list(allowed_methods) if allowed_methods is not None else None
    if prompt_history_per_agent and 0 <= agent_idx < len(prompt_history_per_agent):
        ph = prompt_history_per_agent[agent_idx] or []
        if ph:
            prompt_lines: List[str] = []
            for t, p in enumerate(ph, start=1):
                if t == 1 and not include_original_prompt:
                    continue
                prompt_lines.append(f"- Turn {t} prompt:\n{p}")
            if prompt_lines:
                lines.append("History: previous prompts:")
                lines.extend(prompt_lines)
                lines.append("")
    if include_previous_response and response_history_per_agent and 0 <= agent_idx < len(response_history_per_agent):
        rh = response_history_per_agent[agent_idx] or []
        if rh:
            response_lines: List[str] = []
            for t, r in enumerate(rh, start=1):
                if allowed_methods_list is None:
                    filtered = r or ""
                else:
                    filtered = _filter_response_to_methods(r, allowed_methods_list)
                if not filtered:
                    continue
                response_lines.append(f"- Turn {t} response:\n{filtered}")
            if response_lines:
                lines.append("History: your previous responses:")
                lines.extend(response_lines)
                lines.append("")
    return "\n".join(lines).rstrip()
