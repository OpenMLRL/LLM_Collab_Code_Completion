from __future__ import annotations

"""Partition strategy for assigning class methods across agents."""

from typing import Any, Dict, List

from LLM_Collab_Code_Completion.utils.data import (
    extract_incomplete_methods,
    extract_class_name,
    _sanitize_python_source,
)
from LLM_Collab_Code_Completion.utils.prompting import build_take_job_prompt


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


class TakeJobStrategy(CollaborationStrategy):
    """No allocator: each agent is prompted to self-select a subset of methods.

    The `partition` here is intentionally a no-op mapping (empty), as assignment
    is left to agents via prompt. Downstream code must handle self-select by
    parsing agent outputs and should not rely on this partition for filtering.
    """

    def __init__(self, num_agents: int, seed: int) -> None:
        super().__init__(num_agents=num_agents, seed=seed)
        self.self_select = True

    def partition(self, example: Dict[str, Any]) -> Dict[str, int]:
        return {}


def get_strategy(num_agents: int, seed: int) -> CollaborationStrategy:
    return TakeJobStrategy(num_agents=num_agents, seed=seed)


def build_agent_formatters(strategy: CollaborationStrategy) -> List:
    """Return per-agent prompt formatters for TAKE_JOB self-selection."""
    def make_fmt(agent_idx: int):
        def _fmt(example: Dict[str, Any]) -> str:
            skeleton = example.get("skeleton", "")
            skeleton = _sanitize_python_source(skeleton)
            class_name = example.get("class_name") or extract_class_name(skeleton) or ""
            methods = extract_incomplete_methods(skeleton)
            return build_take_job_prompt(
                skeleton=skeleton,
                class_name=class_name,
                method_names=methods,
                num_agents=strategy.num_agents,
            )

        return _fmt

    return [make_fmt(i) for i in range(strategy.num_agents)]
