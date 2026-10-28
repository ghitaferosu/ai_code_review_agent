from pathlib import Path

from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split

from backend.ml.ast_features import extract_ast_features
from backend.ml.dataset_loader import load_dataset
from backend.ml.hybrid_model import create_models

from backend.ml.ast_features import FEATURES

PATH=Path(__file__).resolve().parents[2]
DATASET= PATH / "data/raw/code_samples.csv"

def compare_models():
    df=load_dataset(DATASET)
    X_train, X_test, y_train, y_test = train_test_split(
        df["code"],
        df["label"],
        test_size=0.25,
        random_state=42,
        stratify=df["label"]
    )

    print("training samples",len(X_train))
    print("testing samples",len(X_test))

    for name, model in create_models().items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        print(f"\n{name}")
        print("\naccuracy:",round(accuracy_score(y_test, predictions),3))
        print("\nf1 score:",round(f1_score(y_test, predictions,pos_label=1,zero_division=0),3))
        print("\nconfusion matrix:\n",confusion_matrix(y_test, predictions,labels=[0,1]))

        for code, actual, predicted in zip(X_test,y_test,predictions):
            print(f"\nactual={actual},predicted={predicted}, code={code}")

def inspect_ast_features():
    examples = [
        "subprocess.Popen(args, shell=True)",
        "try:\n    save()\nexcept:\n    log_error()",
        "output = eval(request_data)",
        "try:\n    save()\nexcept OSError:\n    log_error()",
    ]

    for code in examples:
        values = extract_ast_features(code)

        features = dict(zip(FEATURES, values))

        print("\nCode:", repr(code))
        print("AST features:")

        for name, value in features.items():
            if value != 0:
                print(f"  {name}: {value}")

if __name__ == "__main__":
    compare_models()
    inspect_ast_features()