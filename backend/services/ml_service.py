from functools import lru_cache
from pathlib import Path
import joblib
import ast

ROOT=Path(__file__).resolve().parents[2]
MODEL_PATH=ROOT/"models/code_risk_v3.joblib"

@lru_cache(maxsize=1)
def load_model():
    return joblib.load(MODEL_PATH)

def predict(code):
    model = load_model()
    prediction = model.predict([code])[0]
    probabilities=model.predict_proba([code])[0]
    classes=list(model.classes_)
    risky_index=classes.index(1)
    risk_probability=probabilities[risky_index]
    return {
        "prediction": prediction,
        "label":(
            "risky" if prediction==1 else "not risky"
        ),
        "risk_probability": round(risk_probability,3),
        "model":"tfidf_v3"
    }
