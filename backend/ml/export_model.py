from pathlib import Path
import joblib
import pandas as pd
from backend.ml.hybrid_model import create_models


ROOT=Path(__file__).resolve().parents[2]
DATA_PATH=ROOT / "data/processed/code_samples_v3.csv"
MODEL_PATH=ROOT / "models/code_risk_v3.joblib"


def export_model():
    df=pd.read_csv(DATA_PATH)
    X=df["code"]
    y=df["label"]

    models=create_models()
    model=models["tfidf"]

    model.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print("Model saved")
    print("Training samples",len(df))
    print("model type: tfidf+logistic regression")


if __name__=="__main__":
    export_model()