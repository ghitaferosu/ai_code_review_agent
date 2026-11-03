import ast

FEATURES=["calls","assignments","except_handlers","functions","conditions","eval_calls","bare_except","shell_true","literal_credentials","exec_calls","broad_except",
          "subprocess_alias_shell","indirect_eval","api_key_literal"]

def extract_ast_features(code):
    tree=ast.parse(code)

    eval_aliases = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if (
                    isinstance(node.value, ast.Name)
                    and node.value.id == "eval"
            ):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        eval_aliases.add(target.id)

    subprocess_names = {"subprocess"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    subprocess_names.add(
                        alias.asname or "subprocess"
                    )

    features={name: 0 for name in FEATURES}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            features["calls"]+=1

            if isinstance(node.func, ast.Name) and node.func.id in eval_aliases:
                features["indirect_eval"] += 1

            if isinstance(node.func, ast.Name) and node.func.id == "exec":
                features["exec_calls"] += 1
            if(
                isinstance(node.func, ast.Name)
                and node.func.id == "eval"
            ):
                features["eval_calls"]+=1
            if(
                isinstance(node.func, ast.Attribute)
                and node.func.attr in ("run","call","Popen")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in subprocess_names
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
                    if isinstance(target, ast.Name):
                        variable_name = target.id.lower()
                        if (
                                variable_name in ("api_key", "apikey", "api_token")
                                and isinstance(node.value, ast.Constant)
                                and isinstance(node.value.value, str)
                                and bool(node.value.value)
                        ):
                            features["api_key_literal"] += 1

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
            features["except_handlers"] += 1
            if node.type is None:
                features["bare_except"] += 1
            elif isinstance(node.type, ast.Name) and node.type.id == "BaseException":
                features["broad_except"] += 1

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