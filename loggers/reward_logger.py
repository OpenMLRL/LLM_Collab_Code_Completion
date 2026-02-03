from __future__ import annotations

"""
Utility to log ClassEval reward breakdown (levels) to Weights & Biases.

No-op when wandb is not installed or no active run is present.
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
        cover: Optional[float] = None,
        overlap: Optional[float] = None,
        balance: Optional[float] = None,
        ceb: Optional[float] = None,
        syntax: Optional[float] = None,
        tests: Optional[float] = None,
        total: Optional[float] = None,
        step: Optional[int] = None,
        commit: bool = False,
        prefix: str = "ce_reward",
        extra: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Log CE reward breakdown to wandb.

        Parameters
        - cover (alias: ceb): level 1 "cover" score
        - overlap (alias: syntax): level 2 "overlap" score
        - balance (alias: tests): level 3 "balance" score
        - total: optional overall reward sum
        - step: optional global step for wandb.log
        - commit: whether to commit this logging step (default False)
        - prefix: metric namespace prefix (default "ce_reward")
        - extra: optional dict for additional fields (e.g., num_x_passed/total)
        """
        if cover is None:
            cover = ceb
        if overlap is None:
            overlap = syntax
        if balance is None:
            balance = tests

        def _f(x: Any) -> Optional[float]:
            try:
                return float(x)
            except Exception:
                return None

        payload: Dict[str, Any] = {
            f"{prefix}/level1_cover": _f(cover),
            f"{prefix}/level2_overlap": _f(overlap),
            f"{prefix}/level3_balance": _f(balance),
        }
        if total is not None:
            payload[f"{prefix}/total"] = _f(total)

        if extra:
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
        """Log already-aggregated mean CE levels.
        Accepts either new keys {cover, overlap, balance, [total]} or
        legacy keys {ceb, syntax, tests, [total]}.
        """
        def _get(d: Mapping[str, float], *keys: str) -> float:
            for k in keys:
                if k in d and d[k] is not None:
                    return float(d[k])
            return 0.0

        RewardLogger.log_ce_levels(
            cover=_get(levels, "cover", "ceb"),
            overlap=_get(levels, "overlap", "syntax"),
            balance=_get(levels, "balance", "tests"),
            total=(_get(levels, "total") if "total" in levels else None),
            step=step,
            commit=commit,
            prefix=prefix,
        )

    @staticmethod
    def log_ce_levels_batch(
        batch_levels: Mapping[str, Any] | None = None,
        *,
        cover_list: Optional[list[float]] = None,
        overlap_list: Optional[list[float]] = None,
        balance_list: Optional[list[float]] = None,
        ceb_list: Optional[list[float]] = None,
        syntax_list: Optional[list[float]] = None,
        tests_list: Optional[list[float]] = None,
        total_list: Optional[list[float]] = None,
        step: Optional[int] = None,
        commit: bool = False,
        prefix: str = "ce_reward",
    ) -> None:
        """Convenience to log per-batch mean of each level.

        Provide either a dict with lists under keys {ceb, syntax, tests, total}
        or pass individual lists.
        """
        import math

        def _mean(xs: Optional[list[float]]) -> float:
            if not xs:
                return 0.0
            vals = [float(x) for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
            return float(sum(vals) / len(vals)) if vals else 0.0

        if batch_levels is not None:
            cover_list = batch_levels.get("cover") or batch_levels.get("ceb")
            overlap_list = batch_levels.get("overlap") or batch_levels.get("syntax")
            balance_list = batch_levels.get("balance") or batch_levels.get("tests")
            total_list = batch_levels.get("total")

        RewardLogger.log_ce_levels(
            cover=_mean(cover_list if cover_list is not None else ceb_list),
            overlap=_mean(overlap_list if overlap_list is not None else syntax_list),
            balance=_mean(balance_list if balance_list is not None else tests_list),
            total=_mean(total_list) if total_list is not None else None,
            step=step,
            commit=commit,
            prefix=f"{prefix}_mean",
        )
