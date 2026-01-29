from __future__ import annotations

"""
Runtime patches to adapt CoMLRL MAGRPOTrainer behavior for memory efficiency and
single-agent (GRPO) compatibility without modifying external libraries.

Functions:
- patch_trainer_generation_for_memory(): reduce VRAM usage during generation (MAGRPO).
- patch_maac_generation_for_memory(): reduce VRAM usage during MAAC generation.
- patch_iac_generation_for_memory(): reduce VRAM usage during IAC generation.
- patch_single_agent_returns(): provide GRPO flow when num_agents==1 and num_turns==1.
- apply_default_patches(cfg=None): apply both by default; can be gated by cfg['patches'].
"""

from typing import Any, Dict

from comlrl.trainers.magrpo import MAGRPOTrainer  # type: ignore


def _run_with_generation_patches(actor_model, fn):
    """Run a callable with a temporary generate() wrapper to reduce VRAM."""
    try:
        orig_generate = actor_model.generate
    except Exception:
        return fn()

    def generate_wrapper(*args, **kwargs):
        kwargs.setdefault("output_scores", False)
        kwargs.setdefault("use_cache", False)
        return orig_generate(*args, **kwargs)

    try:
        actor_model.generate = generate_wrapper
        return fn()
    finally:
        try:
            actor_model.generate = orig_generate
        except Exception:
            pass


def patch_trainer_generation_for_memory() -> None:
    """Monkey-patch MAGRPOTrainer._generate_completions to lower VRAM.

    - Force output_scores=False (avoid storing per-step logits)
    - Force use_cache=False (avoid KV cache during generation)
    - Wrap generation under torch.no_grad()
    """
    try:
        orig = MAGRPOTrainer._generate_completions  # type: ignore[attr-defined]
    except Exception:
        return

    def wrapped(self, agent, batch_items, agent_idx=0, num_return_sequences=1, max_new_tokens=None, **kwargs):
        try:
            kwargs.setdefault("output_scores", False)
            kwargs.setdefault("use_cache", False)
            import torch as _torch  # local import to avoid hard dependency at import time
            # Resolve max_new_tokens from trainer args when not explicitly provided
            eff_max_new = max_new_tokens
            if eff_max_new is None:
                try:
                    eff_max_new = int(getattr(self.args, "max_new_tokens", 512))
                except Exception:
                    eff_max_new = 512
            with _torch.no_grad():
                return orig(
                    self,
                    agent,
                    batch_items,
                    agent_idx=agent_idx,
                    num_return_sequences=num_return_sequences,
                    max_new_tokens=eff_max_new,
                    **kwargs,
                )
        except Exception:
            return orig(
                self,
                agent,
                batch_items,
                agent_idx=agent_idx,
                num_return_sequences=num_return_sequences,
                max_new_tokens=(max_new_tokens if max_new_tokens is not None else getattr(self.args, "max_new_tokens", 512)),
                **kwargs,
            )

    try:
        MAGRPOTrainer._generate_completions = wrapped  # type: ignore[attr-defined]
    except Exception:
        pass


def patch_maac_generation_for_memory() -> None:
    """Monkey-patch MAACTrainer._generate to lower VRAM during rollout."""
    try:
        from comlrl.trainers.maac import MAACTrainer  # type: ignore
        orig = MAACTrainer._generate  # type: ignore[attr-defined]
    except Exception:
        return

    def wrapped(self, actor_model, prompt):
        try:
            import torch as _torch  # local import to avoid hard dependency at import time
            with _torch.no_grad():
                return _run_with_generation_patches(
                    actor_model,
                    lambda: orig(self, actor_model, prompt),
                )
        except Exception:
            return orig(self, actor_model, prompt)

    try:
        MAACTrainer._generate = wrapped  # type: ignore[attr-defined]
    except Exception:
        pass


def patch_iac_generation_for_memory() -> None:
    """Monkey-patch IACTrainer._generate_rollout to lower VRAM during rollout."""
    try:
        from comlrl.trainers.iac import IACTrainer  # type: ignore
        orig = IACTrainer._generate_rollout  # type: ignore[attr-defined]
    except Exception:
        return

    def wrapped(self, actor_model, prompt, agent_idx, num_ret):
        try:
            import torch as _torch  # local import to avoid hard dependency at import time
            with _torch.no_grad():
                return _run_with_generation_patches(
                    actor_model,
                    lambda: orig(self, actor_model, prompt, agent_idx, num_ret),
                )
        except Exception:
            return orig(self, actor_model, prompt, agent_idx, num_ret)

    try:
        IACTrainer._generate_rollout = wrapped  # type: ignore[attr-defined]
    except Exception:
        pass


def patch_single_agent_returns() -> None:
    """Monkey-patch MAGRPOTrainer._train_step_returns for single-agent GRPO flow.

    When num_agents==1 and num_turns==1:
    - generate K completions with agent 0
    - compute rewards via existing reward function
    - use rewards as returns (single-turn)
    - compute loss with gradients and step optimizer for agent 0
    """
    try:
        orig = MAGRPOTrainer._train_step_returns  # type: ignore[attr-defined]
    except Exception:
        return

    def wrapped(self, batch_item, epoch_turn_rewards, epoch_turn_returns, **kwargs):
        try:
            n_turns = int(getattr(self.args, "num_turns", 1))
            if self.num_agents == 1 and n_turns == 1:
                import numpy as _np  # type: ignore

                num_gens = int(getattr(self.args, "num_generations", 2))
                comps = self._generate_completions_with_external_prompts(
                    self.agents[0],
                    [batch_item],
                    agent_idx=0,
                    num_return_sequences=num_gens,
                    max_new_tokens=getattr(self.args, "max_new_tokens", 128),
                    external_prompts=None,
                    **kwargs,
                )
                completions0 = comps.get("completions", [[]])[0]
                prompts0 = comps.get("prompts", [""])[0]
                rewards_vec = self._compute_rewards([prompts0], [completions0], batch_items=[batch_item])
                returns_vec = list(map(float, rewards_vec))

                self.optimizers[0].zero_grad()
                agent_loss = self._compute_loss_with_gradients(self.agents[0], comps, returns_vec)
                agent_loss.backward()
                self.optimizers[0].step()

                if epoch_turn_rewards and len(epoch_turn_rewards) > 0:
                    epoch_turn_rewards[0].append(float(_np.mean(rewards_vec)) if rewards_vec else 0.0)
                if epoch_turn_returns and len(epoch_turn_returns) > 0:
                    epoch_turn_returns[0].append(float(_np.mean(returns_vec)) if returns_vec else 0.0)

                batch_loss = float(_np.mean(_np.abs(returns_vec or [0.0])))
                stats = {
                    "batch_mean_reward": float(_np.mean(rewards_vec)) if rewards_vec else 0.0,
                    "batch_expected_return": float(_np.mean(returns_vec)) if returns_vec else 0.0,
                }
                return batch_loss, {0: stats}
        except Exception:
            # fall back to original behavior
            pass
        return orig(self, batch_item, epoch_turn_rewards, epoch_turn_returns, **kwargs)

    try:
        MAGRPOTrainer._train_step_returns = wrapped  # type: ignore[attr-defined]
    except Exception:
        pass


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
