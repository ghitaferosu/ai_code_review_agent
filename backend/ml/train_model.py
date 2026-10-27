from pathlib import Path
import joblib
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, classification_report)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from backend.ml.dataset_loader import load_dataset

DATASET_PATH = Path('../../data/raw/code_samples.csv')
MODEL_PATH = Path('models/code_risk_model.joblib')


def create_model():
    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                analyzer='char',
                ngram_range=(2,5),
                lowercase=False,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=42,
            ),
        ),
    ])

def train_model():
    df=load_dataset(DATASET_PATH)
    X=df["code"]
    y=df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    model = create_model()

    # learn vocabulary and classifier params using training data only for now
    model.fit(X_train, y_train)

    # make predictions
    predictions = model.predict(X_test)

    print("\n ml model eval")
    print("train samples:",len(X_train))
    print("test samples:",len(X_test))

    print("\n accuracy:", accuracy_score(y_test, predictions),3)
    print("\n classification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["risky","not risky"],
            zero_division=0
        )
    )
    print("\n confusion matrix:")
    print(confusion_matrix(y_test, predictions,labels=[0,1]))

    # baseline: always predict the most frequent class
    baseline=DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train.to_frame(), y_train)

    baseline_predictions=baseline.predict(X_test.to_frame())

    print("\n baseline accuracy:",baseline.score(y_test, baseline_predictions),3)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print(f"\n model saved to {MODEL_PATH}")

    return model

if __name__ == "__main__":
    train_model()