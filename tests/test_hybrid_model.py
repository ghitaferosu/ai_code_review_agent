
import numpy as np

from backend.ml.ast_features import (
    FEATURES,
    extract_ast_features,
    transform_ast_features
)
from backend.ml.hybrid_model import create_models


def test_ast_detects_eval():
    features = extract_ast_features(
        "result = eval(user_input)"
    )

    index = FEATURES.index("eval_calls")

    assert features[index] == 1


def test_ast_distinguishes_except():
    risky = extract_ast_features(
        "try:\n    run()\nexcept:\n    pass"
    )

    safe = extract_ast_features(
        "try:\n    run()\nexcept ValueError:\n    pass"
    )

    index = FEATURES.index("bare_except")

    assert risky[index] == 1
    assert safe[index] == 0


def test_ast_features_shape():
    codes = [
        "x = 1",
        "result = eval(data)"
    ]

    features = transform_ast_features(codes)

    assert features.shape == (2, len(FEATURES))
    assert np.isfinite(features).all()


def test_all_models_can_train():
    X = [
        "result = eval(user_input)",
        "value = int(user_input)",
        'password = "abc123"',
        'password = os.getenv("PASSWORD")',
        "try:\n    x()\nexcept:\n    pass",
        "try:\n    x()\nexcept ValueError:\n    pass"
    ]

    y = [1, 0, 1, 0, 1, 0]

    for name, model in create_models().items():
        model.fit(X, y)

        predictions = model.predict(X)

        assert len(predictions) == len(X), name
        assert set(predictions).issubset({0, 1}), name


def test_ast_detects_exec():
    code = "exec(user_code)"

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["exec_calls"] == 1


def test_ast_detects_broad_except():
    code = """
try:
    process()
except BaseException:
    pass
"""

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["except_handlers"] == 1
    assert features["broad_except"] == 1
    assert features["bare_except"] == 0


def test_ast_specific_except_is_not_broad():
    code = """
try:
    process()
except ValueError:
    handle()
"""

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["except_handlers"] == 1
    assert features["broad_except"] == 0


def test_ast_detects_subprocess_alias():
    code = """
import subprocess as sp
sp.run(command, shell=True)
"""

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["shell_true"] == 1


def test_ast_subprocess_alias_without_shell():
    code = """
import subprocess as sp
sp.run(["ls", "-l"])
"""

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["shell_true"] == 0


def test_ast_detects_hardcoded_api_key():
    code = 'api_key = "secret123"'

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["api_key_literal"] == 1


def test_ast_ignores_environment_api_key():
    code = 'api_key = os.getenv("API_KEY")'

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["api_key_literal"] == 0

def test_ast_detects_indirect_eval():
    code = """
dangerous = eval
result = dangerous(user_input)
"""

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["indirect_eval"] == 1


def test_ast_normal_function_is_not_indirect_eval():
    code = """
def safe_function(value):
    return value

result = safe_function(user_input)
"""

    values = extract_ast_features(code)
    features = dict(zip(FEATURES, values))

    assert features["indirect_eval"] == 0
