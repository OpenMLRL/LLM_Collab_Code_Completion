from __future__ import annotations

"""
Utility to log ClassEval reward breakdown (levels) to Weights & Biases.

Usage example (inside rewards/CE_reward.py after computing scores):

    from LLM_Collab_Module_Completion.loggers.reward_logger import RewardLogger

    RewardLogger.log_ce_levels(
        ceb=ceb,                 # lv1 (0..3)
        syntax=syntax_score,     # lv2 (0 or 2)
        tests=pass_score,        # lv3 (0..4)
        components=lv4,          # lv4 (0..1)
        total=total,             # optional overall sum
        step=None,               # optional step; None -> let wandb handle
        commit=False,            # default False to not interfere with trainer's step commits
        prefix="ce_reward",     # metric namespace prefix
        extra=None,              # optional dict for additional fields
    )

This module is a no-op when wandb is not installed or no active run is present.
"""

from typing import Any, Dict, Mapping, Optional


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

            # Filter out None values to avoid serialization issues
            filtered = {k: v for k, v in dict(metrics).items() if v is not None}
            if step is None:
                wandb.log(filtered, commit=commit)
            else:
                wandb.log(filtered, step=int(step), commit=commit)
        except Exception:
            # Swallow logging errors to keep training running
            return

    @staticmethod
    def log_ce_levels(
        *,
        ceb: float,
        syntax: float,
        tests: float,
        components: float,
        total: Optional[float] = None,
        step: Optional[int] = None,
        commit: bool = False,
        prefix: str = "ce_reward",
        extra: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Log CE reward breakdown to wandb.

        Parameters
        - ceb: level 1 (Coverage/Overlap/Balance) score in [0, 3]
        - syntax: level 2 syntax score in {0, 2}
        - tests: level 3 weighted test pass score in [0, 4]
        - components: level 4 component score in [0, 1]
        - total: optional overall reward sum
        - step: optional global step for wandb.log
        - commit: whether to commit this logging step (default False)
        - prefix: metric namespace prefix (default "ce_reward")
        - extra: optional dict for additional fields (e.g., num_x_passed/total)
        """
        # Normalize numbers defensively
        def _f(x: Any) -> Optional[float]:
            try:
                return float(x)
            except Exception:
                return None

        payload: Dict[str, Any] = {
            f"{prefix}/level1_ceb": _f(ceb),
            f"{prefix}/level2_syntax": _f(syntax),
            f"{prefix}/level3_tests": _f(tests),
            f"{prefix}/level4_components": _f(components),
        }
        if total is not None:
            payload[f"{prefix}/total"] = _f(total)

        if extra:
            # Namespaced extras under the same prefix for clarity
            for k, v in extra.items():
                key = f"{prefix}/{k}" if not str(k).startswith(f"{prefix}/") else str(k)
                payload[key] = v

        RewardLogger.log(payload, step=step, commit=commit)

    @staticmethod
    def log_ce_levels_mean(
        levels: Mapping[str, float],
        *,
        step: Optional[int] = None,
        commit: bool = False,
        prefix: str = "ce_reward",
    ) -> None:
        """Log already-aggregated mean CE levels. Expects keys: ceb, syntax, tests, components, [total]."""
        RewardLogger.log_ce_levels(
            ceb=float(levels.get("ceb", 0.0)),
            syntax=float(levels.get("syntax", 0.0)),
            tests=float(levels.get("tests", 0.0)),
            components=float(levels.get("components", 0.0)),
            total=(float(levels["total"]) if "total" in levels else None),
            step=step,
            commit=commit,
            prefix=prefix,
        )

    @staticmethod
    def log_ce_levels_batch(
        batch_levels: Mapping[str, Any] | None = None,
        *,
        ceb_list: Optional[list[float]] = None,
        syntax_list: Optional[list[float]] = None,
        tests_list: Optional[list[float]] = None,
        components_list: Optional[list[float]] = None,
        total_list: Optional[list[float]] = None,
        step: Optional[int] = None,
        commit: bool = False,
        prefix: str = "ce_reward",
    ) -> None:
        """Convenience to log per-batch mean of each level.

        Provide either a dict with lists under keys {ceb, syntax, tests, components, total}
        or pass individual lists.
        """
        import math

        def _mean(xs: Optional[list[float]]) -> float:
            if not xs:
                return 0.0
            vals = [float(x) for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
            return float(sum(vals) / len(vals)) if vals else 0.0

        if batch_levels is not None:
            ceb_list = batch_levels.get("ceb")
            syntax_list = batch_levels.get("syntax")
            tests_list = batch_levels.get("tests")
            components_list = batch_levels.get("components")
            total_list = batch_levels.get("total")

        RewardLogger.log_ce_levels(
            ceb=_mean(ceb_list),
            syntax=_mean(syntax_list),
            tests=_mean(tests_list),
            components=_mean(components_list),
            total=_mean(total_list) if total_list is not None else None,
            step=step,
            commit=commit,
            prefix=f"{prefix}_mean",
        )

