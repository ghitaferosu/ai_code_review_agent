
import ast
import pandas as pd

from backend.ml.train_v3 import DATA_PATH


def test_dataset_v3_size():
    df = pd.read_csv(DATA_PATH)

    assert len(df) == 40
    assert df["group_id"].nunique() == 20


def test_dataset_v3_labels():
    df = pd.read_csv(DATA_PATH)

    counts = df["label"].value_counts().to_dict()

    assert counts == {0: 20, 1: 20}


def test_dataset_v3_valid_syntax():
    df = pd.read_csv(DATA_PATH)

    for code in df["code"]:
        ast.parse(code)


def test_dataset_v3_pairs():
    df = pd.read_csv(DATA_PATH)

    for _, group in df.groupby("group_id"):
        assert len(group) == 2
        assert set(group["label"]) == {0, 1}


def test_dataset_v3_unique_code():
    df = pd.read_csv(DATA_PATH)

    assert df["code"].is_unique
