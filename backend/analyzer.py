import ast
import re


def analyze_code(code: str) -> dict:
    """
    Analyze Python code for common style and quality issues.

    Returns a dict with:
      - score (int): Quality score out of 100 (never below 0)
      - issues (list[str]): Deduplicated list of issues found
    """
    issues = []
    score = 100

    if not code or not code.strip():
        return {"score": 0, "issues": ["No code provided"]}

    # --- Syntax check ---
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"score": 0, "issues": [f"Syntax error: {e.msg} (line {e.lineno})"]}

    lines = code.splitlines()
    non_blank_lines = [l for l in lines if l.strip()]

    # --- Length check ---
    if len(non_blank_lines) > 50:
        issues.append("File is too long (>50 non-blank lines); consider splitting into modules")
        score -= 10

    # --- Line length check (report once with count) ---
    long_lines = [i + 1 for i, l in enumerate(lines) if len(l) > 79]
    if long_lines:
        plural = "s" if len(long_lines) > 1 else ""
        issues.append(
            f"Line{plural} exceed 79 characters (PEP 8): line{plural} {', '.join(map(str, long_lines))}"
        )
        score -= min(len(long_lines) * 2, 10)  # cap penalty at -10

    # --- Print statements ---
    if re.search(r'\bprint\s*\(', code):
        issues.append("Avoid print() statements in production code; use logging instead")
        score -= 5

    # --- Missing module-level docstring ---
    has_module_doc = (
        isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ) if tree.body else False
    if not has_module_doc:
        issues.append("Missing module-level docstring")
        score -= 5

    # --- Functions without docstrings ---
    funcs_without_docs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)):
                funcs_without_docs.append(node.name)
    if funcs_without_docs:
        issues.append(
            f"Function(s) missing docstrings: {', '.join(funcs_without_docs)}"
        )
        score -= min(len(funcs_without_docs) * 3, 10)

    # --- Bare except clauses ---
    bare_excepts = [
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler) and node.type is None
    ]
    if bare_excepts:
        issues.append(
            f"Bare 'except:' clauses found (line(s) {', '.join(map(str, bare_excepts))}); catch specific exceptions"
        )
        score -= 5

    # --- Use of eval/exec ---
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = (func.id if isinstance(func, ast.Name) else
                    func.attr if isinstance(func, ast.Attribute) else None)
            if name in ("eval", "exec"):
                issues.append(f"Avoid using '{name}()'; it's a security risk")
                score -= 10
                break

    # --- TODO / FIXME / HACK comments ---
    todo_lines = [
        i + 1 for i, l in enumerate(lines)
        if re.search(r'#\s*(TODO|FIXME|HACK|XXX)', l, re.IGNORECASE)
    ]
    if todo_lines:
        issues.append(
            f"Unresolved TODO/FIXME/HACK comments on line(s): {', '.join(map(str, todo_lines))}"
        )
        score -= 3

    score = max(score, 0)  # never go below 0

    return {
        "score": score,
        "issues": issues if issues else ["No issues found — great code!"],
    }
