import ast
from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS={"code","label","family","source"}

def load_dataset(path):
    df=pd.read_csv(path,keep_default_na=False)
    missing_columns=REQUIRED_COLUMNS - set(df.columns)

    # validation
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    if df.empty:
        raise ValueError("Empty dataset")

    if not df["code"].map(
        lambda value: isinstance(value, str)
        and bool(value.strip())
    ).all():
        raise ValueError("Empty or invalid code examples")

    if not df["label"].isin([0,1]).all():
        raise ValueError("Invalid label")

    if not df["family"].map(
        lambda value: isinstance(value, str)
        and bool(value.strip())
    ).all():
        raise ValueError("Invalid family")

    if not df["source"].map(
        lambda value: isinstance(value, str)
        and bool(value.strip())
    ).all():
        raise ValueError("Invalid source")

    for index, code in enumerate(df["code"]):
        try:
            ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error at row {index+2}") from e

    if df["code"].duplicated().any():
        raise ValueError(f"Duplicate codes in dataset")

    return df