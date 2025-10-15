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
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import builtins

# Mode implementations live alongside this file
from . import plain
from . import passed
from . import level_feedback
from . import level_passed
from . import group_feedback
from . import personal_feedback

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
    mode: str = "plain",
    **kwargs,
) -> Union[List[str], Tuple[str, ...]]:
    """Build next‑turn prompts per agent for ClassEval.

    Args:
        prompt: The original per‑agent prompt string (used to resolve context).
        agent_completions: Best completions from previous turn, one per agent.
        num_agents: Number of collaborating agents.
        mode: One of 'plain' | 'passed' | 'level_feedback' | 'level_passed'.
        **kwargs: Mode flags:
            - original_prompt: bool (include base context block)
            - previous_response: bool (include previous code snippets)

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

    # Common flags
    original_prompt_flag = kwargs.get("original_prompt", True)
    previous_response_flag = kwargs.get("previous_response", True)

    # Route to mode implementation
    mode_key = (mode or "").lower()

    if mode_key == "plain":
        prompts = plain.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            original_prompt_flag=original_prompt_flag,
            previous_response_flag=previous_response_flag,
            num_agents=n,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: plain")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    if mode_key == "passed":
        prompts = passed.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            test_code=test_code,
            original_prompt_flag=original_prompt_flag,
            previous_response_flag=previous_response_flag,
            num_agents=n,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: passed")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    if mode_key == "level_feedback":
        prompts = level_feedback.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            test_code=test_code,
            original_prompt_flag=original_prompt_flag,
            previous_response_flag=previous_response_flag,
            num_agents=n,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: level_feedback")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    if mode_key == "level_passed":
        prompts = level_passed.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            test_code=test_code,
            original_prompt_flag=original_prompt_flag,
            previous_response_flag=previous_response_flag,
            num_agents=n,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: level_passed")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    if mode_key == "group_feedback":
        prompts = group_feedback.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            test_code=test_code,
            original_prompt_flag=original_prompt_flag,
            previous_response_flag=previous_response_flag,
            num_agents=n,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: group_feedback")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    if mode_key == "personal_feedback":
        prompts = personal_feedback.format_followup_prompts(
            skeleton=skeleton,
            class_name=class_name,
            method_names=method_names,
            assignments=assignments,
            agent_completions=list(agent_completions),
            test_code=test_code,
            original_prompt_flag=original_prompt_flag,
            previous_response_flag=previous_response_flag,
            num_agents=n,
        )
        print("\n" + "=" * 60)
        print("EXTERNAL MODE PREVIEW: personal_feedback")
        for i, p in enumerate(prompts):
            print("-" * 60)
            print(f"AGENT {i} PROMPT:\n{p}")
        print("=" * 60 + "\n")
        return prompts

    supported = ["plain", "passed", "level_feedback", "level_passed", "group_feedback", "personal_feedback"]
    raise NotImplementedError(
        f"External transition mode '{mode}' is not implemented. Supported: {', '.join(supported)}"
    )
