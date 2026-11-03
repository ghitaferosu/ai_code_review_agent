from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA_PATH=ROOT / "data/processed/code_samples_v3.csv"
import pandas as pd
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.metrics import accuracy_score,f1_score,confusion_matrix,classification_report
from backend.ml.hybrid_model import create_models

def train_v3():
    df=pd.read_csv(DATA_PATH)
    splitter=GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_idx,val_idx=next(splitter.split(df["code"],df["label"],groups=df["group_id"]))
    train=df.iloc[train_idx]
    validation=df.iloc[val_idx]

    #guard against group leakage
    train_groups=set(train["group_id"])
    val_groups=set(validation["group_id"])

    assert train_groups.isdisjoint(val_groups)

    print("training",len(train))
    print("validation",len(validation))
    print("train groups",len(train_groups))
    print("validation groups",len(val_groups))

    for name,model in create_models().items():
        model.fit(train["code"],train["label"])

        from backend.ml.ast_features import FEATURES

        if name.lower() == "ast":
            classifier = model.named_steps["classifier"]

            print("\nast feature weights")

            for feature, weight in sorted(
                    zip(FEATURES, classifier.coef_[0]),
                    key=lambda item: abs(item[1]),
                    reverse=True
            ):
                print(f"{feature}: {weight:.4f}")

            from backend.ml.ast_features import (
                FEATURES,
                transform_ast_features
            )

            if name.lower() == "ast":
                classifier = model.named_steps["classifier"]

                examples = [
                    'password = os.environ["PASSWORD"]',
                    'try:\n    fetch()\nexcept BaseException:\n    log()',
                ]

                feature_vectors = transform_ast_features(examples)

                print("\nast decision explanations")
                print("Intercept:", round(classifier.intercept_[0], 4))

                for code, vector in zip(examples, feature_vectors):
                    score = classifier.decision_function(
                        vector.reshape(1, -1)
                    )[0]

                    print("\nCode:", repr(code))
                    print("Decision score:", round(score, 4))

                    print("Feature contributions:")

                    for feature, value, weight in zip(
                            FEATURES,
                            vector,
                            classifier.coef_[0]
                    ):
                        contribution = value * weight

                        if value != 0:
                            print(
                                f"  {feature}: "
                                f"{value} x {weight:.4f} "
                                f"= {contribution:.4f}"
                            )

        predictions=model.predict(validation["code"])
        print("\nname:",name)
        print("accuracy",round(accuracy_score(validation["label"],predictions),3))
        print("f1_score",round(f1_score(validation["label"],predictions,zero_division=0),3))
        print("confusion_matrix",confusion_matrix(validation["label"],predictions,labels=[0,1]))

        for actual, predicted,code in zip(validation["label"],predictions,validation["code"]):
            if actual!=predicted:
                print("wrong",repr(code))


if __name__=="__main__":
    train_v3()