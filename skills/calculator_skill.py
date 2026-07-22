"""
CHRONOS Seed Skill: Calculator & Math Evaluator (calculator_skill.py)
"""

SKILL_NAME = "Calculator"
SKILL_DESCRIPTION = "Evaluates mathematical expressions safely."
SKILL_TRIGGERS = ["calculate", "math", "add", "subtract", "multiply", "divide", "square root"]

def run_skill(query="", **kwargs):
    """Executes safe math evaluation."""
    import re, math

    # Clean query to extract math expression
    clean_expr = re.sub(r"[^\d\+\-\*\/\(\)\.\s\^]", "", query).strip()
    clean_expr = clean_expr.replace("^", "**")

    if not clean_expr:
        return "No valid mathematical expression provided."

    allowed_names = {"math": math, "sqrt": math.sqrt, "pi": math.pi, "pow": math.pow, "abs": abs}
    try:
        code = compile(clean_expr, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"Use of '{name}' is not allowed for security.")
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return f"Calculation Result: {clean_expr} = {result}"
    except Exception as e:
        return f"Math Evaluation Error: {e}"
