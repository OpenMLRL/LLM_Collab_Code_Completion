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
    # Build a set-style representation of the target methods to inline via {curly braces}
    v_braced = "{" + ", ".join(methods) + "}" if methods else "{}"
    n = int(max(1, num_agents))
    total_methods = len(methods)
    target_count = (total_methods + n - 1) // n if total_methods > 0 else 0

    instr = textwrap.dedent(
        f"""
        You are one of {n} collaborating agents tasked with implementing the Python class '{class_name}'.

        Below is the full class skeleton and the set {v_braced} of target methods that require implementation.

        Target methods (Total of {total_methods}):
        {methods_text}

        Important output rules:
        - You must only generate pure Python code without any other words (your output must be executable Python code).
        - Please place the code within the code block. (```python)
        - Do NOT include any text before or after the code (no explanations, no comments outside the code).
        - Choose a **non-empty, proper subset** of {v_braced}, aiming for roughly {target_count} methods to complete. (This is very important!)
        
        SKELETON START
        {skeleton.strip()}
        SKELETON END

        As a final reminder, please select a **non-empty, proper subset** of {v_braced} to implement.

        We recommend choosing a consecutive block of methods that either starts at the beginning of {v_braced} or ends at its last method (DO NOT limit yourself to only the beginning).

        Take particular care not to select all methods for implementation!
        """
    ).strip()

    return instr
