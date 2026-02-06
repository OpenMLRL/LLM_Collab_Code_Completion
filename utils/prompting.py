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


