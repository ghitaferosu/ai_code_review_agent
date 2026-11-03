from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT / 'data/evaluation/challenge_v2.csv'

CASES=[
    ("dynamic_eval",1,"fn=eval\nresult=fn(data)"),
    ("dynamic_eval",0,"import json\nresult=json.loads(data)"),
    ("shell_alias",1,"import subprocess as sp\nsp.run(command,shell=True)"),
    ("shell_alias",0,'import subprocess as sp\nsp.run(["ls","-l"])'),
    ("credentials",1,'api_key="secret123"'),
    ("credentials",0,'api_key=os.getenv("API_KEY")'),
    ("exceptions",1,"try:\n    process()\nexcept BaseException:\n    pass"),
    ("exceptions",0,"try:\n    process()\nexcept ValueError:\n    handle()"),
    ("dynamic_exec",1,"exec(user_code)"),
    ("dynamic_exec",0,"print(user_code)")
]

def generate_challenge():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=["id","family","code","label"])
        writer.writeheader()
        for index, (family,label,code) in enumerate(CASES,start=1):
            writer.writerow({
                "id":f"C{index:03d}",
                "family":family,
                "code":code,
                "label":label
            })

    print("DONE")
    print("total examples:",len(CASES))


if __name__ == "__main__":
    generate_challenge()