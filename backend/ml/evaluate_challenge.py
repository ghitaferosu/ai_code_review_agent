from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,recall_score,f1_score,confusion_matrix
from backend.ml.dataset_loader import load_dataset
from backend.ml.hybrid_model import create_models

ROOT=Path(__file__).resolve().parents[2]
TRAIN_PATH=ROOT/"data/raw/code_samples.csv"
CHALLENGE_PATH=ROOT/"data/evaluation/challenge_v2.csv"

def evaluate_challenge():
    training=load_dataset(TRAIN_PATH)
    challenge=pd.read_csv(CHALLENGE_PATH)
    overlap=set(training["code"]) & set(challenge["code"])
    if overlap:
        raise ValueError("duplicates found in training and challenge")
    X_train=training["code"]
    y_train=training["label"]

    X_test=challenge["code"]
    y_test=challenge["label"]

    for name, model in create_models().items():
        model.fit(X_train,y_train)
        predictions=model.predict(X_test)
        print(f"\nname:{name}\n")
        print("accuracy:",round(accuracy_score(y_test,predictions),3))
        print("precision:",round(precision_score(y_test,predictions,zero_division=0),3))
        print("recall:",round(recall_score(y_test,predictions,zero_division=0),3))
        print("f1:",round(f1_score(y_test,predictions,zero_division=0),3))
        print("confusion matrix:",confusion_matrix(y_test,predictions,labels=[0,1]))

        for example_id,actual,predicted in zip(challenge["id"],y_test,predictions):
            status=("correct" if actual==predicted else "incorrect")
            print(f"{example_id}:actual={actual}\tpredicted={predicted}\tstatus={status}")



if __name__=="__main__":
    evaluate_challenge()
