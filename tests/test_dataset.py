
import pandas as pd
import pytest

from backend.ml.dataset_loader import load_dataset
from backend.ml.generate_dataset import generate_dataset


def test_dataset_has_24_samples(tmp_path):
    path = tmp_path / "samples.csv"
    generate_dataset(path)

    df = load_dataset(path)

    assert len(df) == 24


def test_dataset_is_balanced(tmp_path):
    path = tmp_path / "samples.csv"
    generate_dataset(path)

    df = load_dataset(path)

    counts = df["label"].value_counts()

    assert counts[0] == 12
    assert counts[1] == 12


def test_dataset_contains_four_families(tmp_path):
    path = tmp_path / "samples.csv"
    generate_dataset(path)

    df = load_dataset(path)

    assert df["family"].nunique() == 4


def test_invalid_label_is_rejected(tmp_path):
    path = tmp_path / "invalid.csv"

    pd.DataFrame([{
        "code": "x = 1",
        "label": 5,
        "family": "test",
        "source": "manual"
    }]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Invalid label"):
        load_dataset(path)


def test_duplicate_code_is_rejected(tmp_path):
    path = tmp_path / "duplicates.csv"

    pd.DataFrame([
        {
            "code": "x = 1",
            "label": 0,
            "family": "test",
            "source": "manual"
        },
        {
            "code": "x = 1",
            "label": 1,
            "family": "test",
            "source": "manual"
        }
    ]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Duplicate"):
        load_dataset(path)


def test_invalid_python_is_rejected(tmp_path):
    path = tmp_path / "invalid_python.csv"

    pd.DataFrame([{
        "code": "def broken(",
        "label": 1,
        "family": "test",
        "source": "manual"
    }]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Syntax"):
        load_dataset(path)
