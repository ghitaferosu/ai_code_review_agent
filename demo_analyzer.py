from backend.services.static_analyzer import analyze_python_code

code="""
import subprocess
password = "12345"
user_input=input("Enter expr:")
result=eval(user_input)
try:
    subprocess.run("echo Hello",shell=True)
except:
    pass
"""

issues=analyze_python_code(code)

for issue in issues:
    print(f"Line: {issue['line']}",
          f"Severity: {issue['severity']}",
          f"Description: {issue['description']}" )