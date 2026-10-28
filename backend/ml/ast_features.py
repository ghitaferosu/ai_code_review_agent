import ast

FEATURES=["calls","assignments","except_handlers","functions","conditions","eval_calls","bare_except","shell_true","literal_credentials"]

def extract_ast_features(code):
    tree=ast.parse(code)
    features={name: 0 for name in FEATURES}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            features["calls"]+=1
            if(
                isinstance(node.func, ast.Name)
                and node.func.id == "eval"
            ):
                features["eval_calls"]+=1
            if(
                isinstance(node.func, ast.Attribute)
                and node.func.attr in ("run","call","Popen")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
            ):
                for keyword in node.keywords:
                    if(
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        features["shell_true"]+=1
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
                features["assignments"]+=1
                targets=(
                    node.targets
                    if isinstance(node, ast.Assign)
                    else [node.target]
                )
                for target in targets:
                    if(
                        isinstance(target, ast.Name)
                        and target.id.lower() in (
                        "password","passwd","secret"
                    )
                        and isinstance(node.value, ast.Constant)
                        and isinstance(node.value.value, str)
                        and bool(node.value.value)
                    ):
                        features["literal_credentials"]+=1
        if isinstance(node, ast.ExceptHandler):
                features["except_handlers"]+=1

                if node.type is None:
                    features["bare_except"]+=1
        if isinstance(node, (ast.FunctionDef,ast.AsyncFunctionDef)):
                features["functions"]+=1

        if isinstance(node, ast.If):
                features["conditions"]+=1

    return [float(features[name]) for name in FEATURES]


import numpy as np

def transform_ast_features(codes):
    rows=[
        extract_ast_features(code)
        for code in codes
    ]
    return np.asarray(rows,dtype=float).reshape(-1,len(FEATURES))