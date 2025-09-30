"""Collaboration strategies for assigning class methods to agents.

Exports a simple factory and helpers:
- get_strategy(mode, num_agents, seed)
- build_agent_formatters(strategy)
"""

from .strategies import (
    CollaborationStrategy,
    OneStrategy,
    RandomPartitionStrategy,
    get_strategy,
    build_agent_formatters,
)

__all__ = [
    "CollaborationStrategy",
    "OneStrategy",
    "RandomPartitionStrategy",
    "get_strategy",
    "build_agent_formatters",
]

