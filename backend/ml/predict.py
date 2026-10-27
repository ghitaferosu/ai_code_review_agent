from pathlib import Path
import joblib

MODEL_PATH=Path("models/code_risk_model.joblib")

def predict_code_risk(code):
    model = joblib.load(MODEL_PATH)
    prediction=int(model.predict([code])[0])
    probabilities=model.predict_proba([code])[0]
    classes=list(model.classes_)
    risky_index=classes.index(1)
    risk_probability=float(probabilities[risky_index])
    return {
        "prediction": prediction,
        "label":(
            "risky" if prediction == 1 else "not risky"
        ),
        "risk_probability": round(risk_probability, 4)
    }

if __name__=="__main__":
    examples=[
        "result=eval(user_input)",
        "result=int(user_input)",
        'password="hardcoded"',
        'password=os.getenv("APP_PASSWORD")',
        'eval("2+2")',
        'print("Never use eval(user_input)")',
        'subprocess.run(["echo","hello world"])'
    ]
    for code in examples:
        print("Code:",code)
        print(predict_code_risk(code))