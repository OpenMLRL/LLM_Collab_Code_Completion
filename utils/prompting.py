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

        Below is the full class skeleton and the set {v_braced} of target methods that require implementation. Choose a **non-empty, proper subset** of {v_braced} (i.e., not all of {v_braced}), aiming for roughly {target_count} or {max(1, target_count-1)} methods to balance workload and avoid overlap.

        Target methods (Total of {total_methods}):
        {methods_text}

        Important output rules:
        - Output **only** the chosen methods as Python function definitions **with full bodies**.
        - Put **all** functions in **one** fenced code block: ``` ... ```
        - **Do not** output the class header, any imports, or any text outside the code block.
        - **Do not** include any comments or docstrings in the code (no `# ...` comments and no `\"\"\"...\"\"\"` or `'''...'''` docstrings).
        - Use the **exact** signatures from the skeleton: names, parameters, defaults, type hints, and any decorators (@staticmethod/@classmethod).
        - Implement real, runnable logic; **no** `pass`, `...`, `TODO`, or placeholder returns.
        - Function names must be **only** from {v_braced}; prefer the order they appear in {v_braced}.
        - Any helper logic must live **inside** the selected methods; do not add new top-level functions/classes/fields.

        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()

    return instr
