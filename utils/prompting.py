from __future__ import annotations

import textwrap
from typing import List


def build_agent_prompt(skeleton: str, class_name: str, assigned_methods: List[str]) -> str:
    """Construct an agent prompt that includes the full class skeleton and specifies
    which methods this agent must implement.

    Output constraints:
    - Agent must output ONLY Python function definitions for the assigned methods.
    - No markdown/code fences, no extra commentary.
    - One or more def blocks, exactly matching the assigned method names.
    """
    assigned_methods = list(assigned_methods or [])
    assigned_text = (
        "\n".join(f"- {m}" for m in assigned_methods) if assigned_methods else "(none)"
    )

    instr = textwrap.dedent(
        f"""
        You are collaborating to complete the Python class '{class_name}'.

        Below is the full class skeleton. Your responsibility is to implement ONLY the following methods:
        {assigned_text}

        Important output rules:
        - Output ONLY Python function definitions for your assigned methods.
        - Do NOT include the class header or any imports.
        - Do NOT include markdown code fences or any explanatory text.
        - Each function name must match exactly one of your assigned methods.
        - If you were assigned no methods, output an empty response.

        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()

    return instr


def build_take_job_prompt(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    num_agents: int,
) -> str:
    """Construct a prompt for TAKE_JOB strategy where agents self-select methods.

    Key differences from build_agent_prompt:
    - No pre-assigned methods. The agent must choose a subset from `method_names`.
    - Inform the agent of the total number of collaborating agents.
    - Output must include ONLY Python function definitions for the chosen subset,
      using names strictly from the provided list.
    """
    methods = list(method_names or [])
    methods_text = "\n".join(f"- {m}" for m in methods) if methods else "(none)"
    n = int(max(1, num_agents))

    instr = textwrap.dedent(
        f"""
        You are one of {n} collaborating agents working to complete the Python class '{class_name}'.

        Below is the full class skeleton, and the list of target methods V that require implementation.
        You must choose a reasonable subset of methods from V to implement yourself. Coordinate implicitly
        by aiming for balanced workload (roughly |V|/{n} methods per agent) and minimal overlap with others.

        Target methods (V):
        {methods_text}

        Important output rules:
        - Output ONLY Python function definitions for the methods you choose from V.
        - The Python code SHOULD BE fenced in ``` block.
        - Do NOT include the class header or any imports.
        - Do NOT include any explanatory text.
        - Each function name must be strictly from the listed target methods.

        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()

    return instr
