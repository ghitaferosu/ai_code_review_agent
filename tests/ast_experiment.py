import ast

code = """
x=10
print(x)
"""

tree=ast.parse(code)
print(ast.dump(tree,indent=4))