from __future__ import annotations

"""
External transition utilities for multi‑turn training on ClassEval (module completion).

This mirrors the interface provided by LLM_Collab_Code_Generation/external, but
the prompt content and analysis are adapted to ClassEval where agents implement
class methods inside a provided skeleton.

Usage:
- Register a context resolver via set_context_resolver(fn).
  The resolver must accept a prompt string and return a dict containing:
    {
      'skeleton': str,
      'class_name': str | None,
      'tests_eval': str,
      'tests_sandbox': str | None,
      'method_names': list[str],           # methods requiring implementation
      'assignments': dict[int, list[str]]  # optional: agent_idx -> assigned methods
    }
- Call get_external_transition(...) to produce next‑turn prompts per agent.
  Supported modes: code_feedback, plain.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import builtins

# Mode implementations live alongside this file
from . import code_feedback
from . import plain

# Verbose toggle for external previews
VERBOSE = True


# -----------------------------
# Context resolver API
# -----------------------------
_context_resolver: Optional[Callable[[str], Optional[Dict[str, Any]]]] = None


def set_context_resolver(fn: Callable[[str], Optional[Dict[str, Any]]]):
    """Register a resolver that maps prompt -> context dict.

    Expected dict keys:
      - skeleton: str
      - class_name: Optional[str]
      - tests_eval: str
      - tests_sandbox: Optional[str]
      - method_names: List[str]
      - assignments: Optional[Dict[int, List[str]]]  # agent_idx -> methods
    """
    global _context_resolver
    _context_resolver = fn


def get_context(prompt: str) -> Optional[Dict[str, Any]]:
    if _context_resolver is None:
        return None
    try:
        return _context_resolver(prompt)
    except Exception:
        return None


def get_external_transition(
    prompt: str,
    agent_completions: Union[List[str], Tuple[str, ...]],
    num_agents: int = 2,
    mode: str = "code_feedback",
    *,
    # Per-agent history provided by CoMLRL (full history by default)
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
    **kwargs,
) -> Union[List[str], Tuple[str, ...]]:
    """Build next‑turn prompts per agent for ClassEval.

    Args:
        prompt: The original per‑agent prompt string (used to resolve context).
        agent_completions: Best completions from previous turn, one per agent.
        num_agents: Number of collaborating agents.
    mode: 'code_feedback' or 'plain'.

    Returns:
        A list (or tuple) of strings, one per agent.
    """
    if not VERBOSE:
        def print(*_args, **_kwargs):  # type: ignore
            return None
    else:
        print = builtins.print  # type: ignore

    n = int(num_agents)
    if n <= 0:
        raise ValueError("num_agents must be >= 1")

    if not isinstance(agent_completions, (list, tuple)) or len(agent_completions) != n:
        raise ValueError(
            f"Expected {n} agent completions, got {len(agent_completions) if isinstance(agent_completions, (list, tuple)) else 'invalid type'}"
        )

    ctx = get_context(prompt) or {}
    # Required context
    skeleton = ctx.get("skeleton", "")
    class_name = ctx.get("class_name") or ""
    method_names = list(ctx.get("method_names", []))
    test_code = ctx.get("tests_sandbox") or ctx.get("tests_eval", "")
    assignments = ctx.get("assignments", {}) or {}

    # Normalize histories (full history: all previous prompts/responses per agent)
    if prompt_history_per_agent is None:
        prompt_history_per_agent = [[] for _ in range(n)]
    if response_history_per_agent is None:
        response_history_per_agent = [[] for _ in range(n)]

    mode_key = (mode or "").lower()
    if mode_key == "code_feedback":
        prompts = code_feedback.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            test_code=test_code,
            num_agents=n,
            prompt_history_per_agent=prompt_history_per_agent,
            response_history_per_agent=response_history_per_agent,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: code_feedback")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    if mode_key == "plain":
        prompts = plain.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            num_agents=n,
            prompt_history_per_agent=prompt_history_per_agent,
            response_history_per_agent=response_history_per_agent,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: plain")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    raise NotImplementedError(
        f"External transition mode '{mode}' is not supported. Use 'code_feedback' or 'plain'."
    )
