
import ast


def analyze_python_code(code: str) -> list[dict]:
    issues = []

    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return [{
            "line": error.lineno or 0,
            "category": "syntax",
            "severity": "high",
            "description": "Invalid Python syntax"
        }]

    for node in ast.walk(tree):

        # detect direct eval() calls
        if isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "eval"
            ):
                issues.append({
                    "line": node.lineno,
                    "category": "security",
                    "severity": "high",
                    "description": "Potentially unsafe eval() call"
                })

            # detect subprocess calls with shell=True
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr in ("run", "call", "Popen")
            ):
                for keyword in node.keywords:
                    if (
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        issues.append({
                            "line": node.lineno,
                            "category": "security",
                            "severity": "high",
                            "description": "subprocess uses shell=True"
                        })

        # detect bare except
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append({
                    "line": node.lineno,
                    "category": "maintainability",
                    "severity": "medium",
                    "description": "Bare except catches all exceptions"
                })

        # detect literal password assignments
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue

                if (
                    target.id.lower() in ("password", "passwd", "secret")
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                    and node.value.value
                ):
                    issues.append({
                        "line": node.lineno,
                        "category": "security",
                        "severity": "high",
                        "description": "Possible hardcoded credential"
                    })
        # detect annotated hardcoded credentials
        if isinstance(node, ast.AnnAssign):
            target = node.target
            value = node.value

            if (
                    isinstance(target, ast.Name)
                    and target.id.lower() in ("password", "passwd", "secret")
                    and isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                    and value.value
            ):
                issues.append({
                    "line": node.lineno,
                    "category": "security",
                    "severity": "high",
                    "description": "Possible hardcoded credential"
                })

    return sorted(issues, key=lambda issue: issue["line"])
