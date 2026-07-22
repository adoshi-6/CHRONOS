"""
CHRONOS LaTeX Math Solver & Derivation Engine (katex_math.py)
------------------------------------------------------------
Provides 100% deterministic symbolic math solving, calculus derivations,
algebraic step-by-step solutions, and KaTeX LaTeX rendering.
"""

import os
import json

class KaTeXMathEngine:
    """Symbolic math engine powered by SymPy with LaTeX output."""

    def __init__(self):
        self.sympy_available = False
        try:
            import sympy as sp
            self.sp = sp
            self.sympy_available = True
        except ImportError:
            self.sp = None

    def solve_expression(self, expr_str, var_str="x"):
        """Solves algebraic equations or simplifies expressions."""
        if not self.sympy_available:
            return {"success": False, "error": "SymPy symbolic math library not loaded."}
        try:
            sp = self.sp
            x = sp.Symbol(var_str)
            if "=" in expr_str:
                lhs, rhs = expr_str.split("=")
                eq = sp.Eq(sp.sympify(lhs.strip()), sp.sympify(rhs.strip()))
                solution = sp.solve(eq, x)
                latex_eq = sp.latex(eq)
                latex_sol = sp.latex(solution)
                return {
                    "success": True,
                    "type": "Algebraic Equation",
                    "original": expr_str,
                    "latex_equation": f"$${latex_eq}$$",
                    "latex_solution": f"$${var_str} = {latex_sol}$$",
                    "solution_raw": str(solution)
                }
            else:
                parsed_expr = sp.sympify(expr_str)
                simplified = sp.simplify(parsed_expr)
                return {
                    "success": True,
                    "type": "Expression Simplification",
                    "original": expr_str,
                    "latex_equation": f"$${sp.latex(parsed_expr)}$$",
                    "latex_solution": f"$$= {sp.latex(simplified)}$$",
                    "solution_raw": str(simplified)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def differentiate(self, expr_str, var_str="x"):
        """Computes exact derivative d/dx."""
        if not self.sympy_available:
            return {"success": False, "error": "SymPy symbolic math library not loaded."}
        try:
            sp = self.sp
            var = sp.Symbol(var_str)
            expr = sp.sympify(expr_str)
            derivative = sp.diff(expr, var)

            return {
                "success": True,
                "type": "Symbolic Differentiation",
                "original": f"d/d{var_str} ({expr_str})",
                "latex_input": f"$$\\frac{{d}}{{d{var_str}}} \\left( {sp.latex(expr)} \\right)$$",
                "latex_result": f"$$= {sp.latex(derivative)}$$",
                "result_raw": str(derivative)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def integrate_expr(self, expr_str, var_str="x", lower=None, upper=None):
        """Computes definite or indefinite integrals."""
        if not self.sympy_available:
            return {"success": False, "error": "SymPy symbolic math library not loaded."}
        try:
            sp = self.sp
            var = sp.Symbol(var_str)
            expr = sp.sympify(expr_str)

            if lower is not None and upper is not None:
                low_val = sp.sympify(lower)
                up_val = sp.sympify(upper)
                result = sp.integrate(expr, (var, low_val, up_val))
                latex_in = f"$$\\int_{{{sp.latex(low_val)}}}^{{{sp.latex(up_val)}}} {sp.latex(expr)} \\, d{var_str}$$"
            else:
                result = sp.integrate(expr, var)
                latex_in = f"$$\\int {sp.latex(expr)} \\, d{var_str}$$"

            return {
                "success": True,
                "type": "Symbolic Integration",
                "original": expr_str,
                "latex_input": latex_in,
                "latex_result": f"$$= {sp.latex(result)} + C$$" if lower is None else f"$$= {sp.latex(result)}$$",
                "result_raw": str(result)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton Instance
math_engine = KaTeXMathEngine()


if __name__ == "__main__":
    print("\n--- CHRONOS LaTeX Math Engine Diagnostics ---")
    diff_res = math_engine.differentiate("x**3 + sin(x)")
    print(f"Derivative Result: {diff_res.get('latex_input')} -> {diff_res.get('latex_result')}")
    integ_res = math_engine.integrate_expr("x**2 * exp(x)")
    print(f"Integral Result: {integ_res.get('latex_input')} -> {integ_res.get('latex_result')}")
    solve_res = math_engine.solve_expression("x**2 - 5*x + 6 = 0")
    print(f"Equation Solution: {solve_res.get('latex_equation')} -> {solve_res.get('latex_solution')}")
