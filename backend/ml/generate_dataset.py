import csv
from pathlib import Path

DATASET_PATH = Path("data/raw/code_samples.csv")

# labels: 1-risky, 0-not risky

samples=[

    # dynamic execution
    ("result=eval(user_input)",1,"dynamic_execution"),
    ("answer=eval(expression)",1,"dynamic_execution"),
    ("output=eval(request_data)",1,"dynamic_execution"),
    ("value=int(user_input)",0,"dynamic_execution"),
    ("result=float(expression)",0,"dynamic_execution"),
    ("answer=str(request_data)",0,"dynamic_execution"),

    #hardcoded credentials
    ('password="secret"',1,"credentials"),
    ('secret="private_key"',1,"credentials"),
    ('passwd="admin123"',1,"credentials"),
    ('password=os.getenv("PASSWORD")',0,"credentials"),
    ('secret=os.environ["APP_SECRET"]',0,"credentials"),
    ('passwd=getpass.getpass()',0,"credentials"),

    # exception handling
    ("try:\n    execute()\nexcept:\n    pass",1,"exceptions"),
    ("try:\n    save()\nexcept:\n    log_error()",1,"exceptions"),
    ("try:\n    load()\nexcept:\n    return None",1,"exceptions"),
    ("try:\n    execute()\nexcept ValueError:\n    pass",0,"exceptions"),
    ("try:\n    save()\nexcept OSError:\n    log_error()",0,"exceptions"),
    ("try:\n    load()\nexcept KeyError:\n    return None",0,"exceptions"),

    #subprocess
    ('subprocess.run(command, shell=True)',1,"subprocess"),
    ('subprocess.call(command, shell=True)',1,"subprocess"),
    ('subprocess.Popen(args, shell=True)',1,"subprocess"),
    ('subprocess.run(["echo","hello"], shell=False)',0,"subprocess"),
    ('subprocess.call(["ls","-l"], shell=False)',0,"subprocess"),
    ('subprocess.Popen(["python","--version"], shell=False)',0,"subprocess"),


]

def generate_dataset(path: Path=DATASET_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["code","label","family","source"])
        for code, label, family in samples:
            writer.writerow([code,label,family,"manual_dataset_v1"])
        print(f"Generated {len(samples)} samples, path: {path}")


if __name__ == "__main__":
    generate_dataset()