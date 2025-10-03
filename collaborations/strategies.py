from __future__ import annotations

"""Partition strategies for assigning class methods across agents.

Two built-in strategies:
- OneStrategy: assign all methods to agent 0 (single-agent case)
- RandomPartitionStrategy: assign methods to agents uniformly at random, deterministically per (seed, task_id)

New strategy:
- TakeJobStrategy ("TAKE_JOB"): no allocator. Each agent sees the full class
  and is instructed to self-select a subset of methods to implement. Agents are
  informed of the total number of agents.

A small helper `build_agent_formatters` returns per-agent prompt formatters that
include the full class skeleton and enumerate the methods assigned to that agent.
"""

import hashlib
import random
from typing import Any, Dict, List

from LLM_Collab_Module_Completion.utils.data import (
    extract_incomplete_methods,
    extract_class_name,
    _sanitize_python_source,
)
from LLM_Collab_Module_Completion.utils.prompting import (
    build_agent_prompt,
    build_take_job_prompt,
)


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


class OneStrategy(CollaborationStrategy):
    """All methods go to agent 0 (single-agent flow)."""

    def partition(self, example: Dict[str, Any]) -> Dict[str, int]:
        methods = extract_incomplete_methods(example.get("skeleton", ""))
        return {m: 0 for m in methods}


class RandomPartitionStrategy(CollaborationStrategy):
    """Uniform random assignment per example, deterministic w.r.t (seed, task_id)."""

    def _rng_for(self, task_id: str | None) -> random.Random:
        h = hashlib.sha256(str(task_id or "").encode("utf-8")).hexdigest()
        off = int(h[:16], 16)
        return random.Random(self.seed ^ off)

    def partition(self, example: Dict[str, Any]) -> Dict[str, int]:
        methods = extract_incomplete_methods(example.get("skeleton", ""))
        rng = self._rng_for(str(example.get("task_id", "")))
        return {m: rng.randrange(self.num_agents) for m in methods}


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
        # No pre-assignment; return empty mapping.
        return {}


def get_strategy(mode: str, num_agents: int, seed: int) -> CollaborationStrategy:
    m = (mode or "ONE").upper()
    if m == "ONE" or num_agents <= 1:
        return OneStrategy(num_agents=1, seed=seed)
    if m == "RAND_PARTITION":
        return RandomPartitionStrategy(num_agents=num_agents, seed=seed)
    if m == "TAKE_JOB":
        return TakeJobStrategy(num_agents=num_agents, seed=seed)
    # Fallback default to ONE
    return OneStrategy(num_agents=1, seed=seed)


def build_agent_formatters(strategy: CollaborationStrategy) -> List:
    """Return per-agent prompt formatters per strategy.

    Each formatter(example) -> prompt string for that agent.
    """
    if getattr(strategy, "self_select", False):
        # TAKE_JOB: each agent gets the same prompt, including total number of agents
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

    # Default partition-based formatters
    def make_fmt(agent_idx: int):
        def _fmt(example: Dict[str, Any]) -> str:
            skeleton = example.get("skeleton", "")
            skeleton = _sanitize_python_source(skeleton)
            class_name = example.get("class_name") or extract_class_name(skeleton) or ""
            # class_name may not be present; it's ok to pass empty
            partition = strategy.partition(example)
            assigned = [m for m, a in partition.items() if a == agent_idx]
            return build_agent_prompt(
                skeleton=skeleton,
                class_name=class_name,
                assigned_methods=assigned,
            )

        return _fmt

    return [make_fmt(i) for i in range(strategy.num_agents)]
