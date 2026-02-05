from __future__ import annotations

"""
Thin wrappers around shared CoMLRL patch utilities.

Keeps local imports stable while centralizing patch logic in comlrl.utils.patches.
"""

from typing import Dict

from comlrl.utils.patches import (
    patch_iac_generation_for_memory,
    patch_maac_generation_for_memory,
    patch_single_agent_returns,
    patch_trainer_generation_for_memory,
)


def apply_default_patches(cfg: Dict[str, Any] | None = None) -> None:
    """Apply default patches with optional gating via cfg['patches'].

    cfg example:
      patches:
        generation_memory: true
        single_agent_returns: true
    """
    gates = (cfg or {}).get("patches", {}) if isinstance(cfg, dict) else {}

    if gates.get("generation_memory", True):
        patch_trainer_generation_for_memory()
        patch_maac_generation_for_memory()
        patch_iac_generation_for_memory()
    if gates.get("single_agent_returns", True):
        patch_single_agent_returns()


__all__ = [
    "apply_default_patches",
    "patch_trainer_generation_for_memory",
    "patch_maac_generation_for_memory",
    "patch_iac_generation_for_memory",
    "patch_single_agent_returns",
]
