
from backend.services.static_analyzer import analyze_python_code


def test_eval_detection():
    code = "result = eval(user_input)"
    issues = analyze_python_code(code)

    assert len(issues) == 1
    assert issues[0]["category"] == "security"
    assert issues[0]["line"] == 1


def test_bare_except_detection():
    code = """
try:
    x = 1 / 0
except:
    pass
"""
    issues = analyze_python_code(code)

    assert len(issues) == 1
    assert issues[0]["category"] == "maintainability"
    assert issues[0]["line"] == 4


def test_hardcoded_password():
    code = 'password = "secret123"'
    issues = analyze_python_code(code)

    assert len(issues) == 1
    assert issues[0]["description"] == "Possible hardcoded credential"


def test_subprocess_shell():
    code = """
import subprocess
subprocess.run("echo hello", shell=True)
"""
    issues = analyze_python_code(code)

    assert len(issues) == 1
    assert "shell=True" in issues[0]["description"]


def test_safe_code():
    code = """
def add(a, b):
    return a + b
"""
    issues = analyze_python_code(code)

    assert issues == []


def test_invalid_syntax():
    code = "def broken("
    issues = analyze_python_code(code)

    assert len(issues) == 1
    assert issues[0]["category"] == "syntax"

def test_annotated_password():
    code = 'password: str = "secret123"'

    issues = analyze_python_code(code)

    assert len(issues) == 1
    assert issues[0]["category"] == "security"
    assert issues[0]["line"] == 1