from __future__ import annotations

"""Partition strategy for assigning class methods across agents."""

from typing import Any, Dict, List

from LLM_Collab_Code_Completion.utils.data import (
    extract_incomplete_methods,
    extract_class_name,
    extract_method_param_counts,
    _sanitize_python_source,
)
from LLM_Collab_Code_Completion.utils.prompting import build_agent_prompt


class CollaborationStrategy:
    """Base strategy for partitioning methods across agents."""

    def __init__(self, num_agents: int, seed: int) -> None:
        self.num_agents = int(max(1, num_agents))
        self.seed = int(seed)
        # Whether agents self-select tasks (no allocator/partition)
        self.self_select = False

    def partition(self, example: Dict[str, Any]) -> Dict[str, int]:
        """Return mapping method_name -> agent_index (0..num_agents-1)."""
        raise NotImplementedError


class ParamCountStrategy(CollaborationStrategy):
    """Assign methods by parameter count: 1-param -> agent 0, others -> agent 1.

    Additional agents (if any) receive no assignments.
    """

    def __init__(self, num_agents: int, seed: int) -> None:
        super().__init__(num_agents=num_agents, seed=seed)
        self.self_select = False

    def partition(self, example: Dict[str, Any]) -> Dict[str, int]:
        skeleton = _sanitize_python_source(str(example.get("skeleton", "")))
        if not skeleton:
            return {}
        methods = extract_incomplete_methods(skeleton)
        if not methods:
            return {}
        counts = extract_method_param_counts(skeleton)
        partition: Dict[str, int] = {}
        for name in methods:
            if self.num_agents <= 1:
                partition[name] = 0
                continue
            param_count = counts.get(name, -1)
            if param_count == 1:
                partition[name] = 0
            else:
                partition[name] = 1
        return partition


def get_strategy(num_agents: int, seed: int) -> CollaborationStrategy:
    return ParamCountStrategy(num_agents=num_agents, seed=seed)


def build_agent_formatters(strategy: CollaborationStrategy) -> List:
    """Return per-agent prompt formatters based on the strategy partition."""
    def make_fmt(agent_idx: int):
        def _fmt(example: Dict[str, Any]) -> str:
            skeleton = example.get("skeleton", "")
            skeleton = _sanitize_python_source(skeleton)
            class_name = example.get("class_name") or extract_class_name(skeleton) or ""
            try:
                partition = strategy.partition(example) or {}
            except Exception:
                partition = {}
            assigned = [m for m, a in partition.items() if int(a) == int(agent_idx)]
            return build_agent_prompt(
                skeleton=skeleton,
                class_name=class_name,
                assigned_methods=assigned,
            )

        return _fmt

    return [make_fmt(i) for i in range(strategy.num_agents)]
