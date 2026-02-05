from __future__ import annotations

"""
Utility to log ClassEval reward breakdown (levels) to Weights & Biases.

No-op when wandb is not installed or no active run is present.
"""

from typing import Dict, Mapping, Optional


class RewardLogger:
    """Stateless helper for logging CE reward levels to wandb.

    All methods are safe to call when wandb is unavailable or not initialized.
    """

    @staticmethod
    def _wandb_run():
        try:
            import wandb  # type: ignore

            return getattr(wandb, "run", None)
        except Exception:
            return None

    @staticmethod
    def is_enabled() -> bool:
        """Return True if wandb is importable and an active run exists."""
        return RewardLogger._wandb_run() is not None

    @staticmethod
    def log(
        metrics: Mapping[str, float | int | str | None],
        *,
        step: Optional[int] = None,
        commit: bool = False,
    ) -> None:
        """Thin wrapper around wandb.log with safety checks.

        - If wandb isn't available or no run is active, this is a no-op.
        - By default, commit=False to avoid interfering with external logging cadence.
        """
        run = RewardLogger._wandb_run()
        if run is None:
            return
        try:
            import wandb  # type: ignore
            filtered = {k: v for k, v in dict(metrics).items() if v is not None}
            if step is None:
                wandb.log(filtered, commit=commit)
            else:
                wandb.log(filtered, step=int(step), commit=commit)
        except Exception:
            # Swallow logging errors to keep training running
            return

    @staticmethod
