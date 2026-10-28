
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
