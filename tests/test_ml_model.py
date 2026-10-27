
import joblib

from backend.ml.train_model import create_model


def test_model_can_train():
    X = [
        "result = eval(user_input)",
        "value = int(user_input)",
        'password = "abc123"',
        'password = os.getenv("PASSWORD")',
    ]

    y = [1, 0, 1, 0]

    model = create_model()
    model.fit(X, y)

    assert len(model.classes_) == 2


def test_prediction_is_binary():
    X = [
        "result = eval(user_input)",
        "value = int(user_input)",
        'password = "abc123"',
        'password = os.getenv("PASSWORD")',
    ]

    y = [1, 0, 1, 0]

    model = create_model()
    model.fit(X, y)

    prediction = model.predict(
        ["result = eval(expression)"]
    )[0]

    assert int(prediction) in (0, 1)


def test_model_can_be_saved_and_loaded(tmp_path):
    X = [
        "eval(user_input)",
        "int(user_input)",
        'password = "abc"',
        'password = os.getenv("PASSWORD")',
    ]

    y = [1, 0, 1, 0]

    model = create_model()
    model.fit(X, y)

    model_path = tmp_path / "model.joblib"
    joblib.dump(model, model_path)

    loaded_model = joblib.load(model_path)

    original_prediction = model.predict(
        ["eval(data)"]
    )

    loaded_prediction = loaded_model.predict(
        ["eval(data)"]
    )

    assert (
        original_prediction.tolist()
        == loaded_prediction.tolist()
    )


def test_probability_is_between_zero_and_one():
    model = create_model()

    model.fit(
        ["eval(x)", "int(x)", 'password = "abc"', "x = 1"],
        [1, 0, 1, 0]
    )

    probabilities = model.predict_proba(
        ["eval(user_input)"]
    )[0]

    assert all(
        0.0 <= probability <= 1.0
        for probability in probabilities
    )

    assert abs(sum(probabilities) - 1.0) < 1e-9
