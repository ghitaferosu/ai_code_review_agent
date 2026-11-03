import ast
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT / 'data' / 'processed' / 'code_samples_v3.csv'

PAIRS={
"dynamic_execution": [
        ("exec(payload)", "print(payload)"),
        ("exec(source)", "compile(source, '<src>', 'exec')"),
        ("fn = eval\nfn(data)", "fn = int\nfn(data)"),
        ("runner = eval\nrunner(text)", "runner = str\nrunner(text)")
    ],
"subprocess": [
        (
            "import subprocess as sp\nsp.run(cmd, shell=True)",
            "import subprocess as sp\nsp.run(cmd, shell=False)",
        ),
        (
            "import subprocess\nsubprocess.Popen(cmd, shell=True)",
            "import subprocess\nsubprocess.Popen(['ls', '-l'])",
        ),
        (
            "import subprocess as proc\nproc.call(cmd, shell=True)",
            "import subprocess as proc\nproc.call(['pwd'])",
        ),
        (
            "import subprocess\nsubprocess.run(task, shell=True)",
            "import subprocess\nsubprocess.run(['echo', 'ok'])",
        )
    ],
    "credentials": [
        (
            'api_key = "example-secret-001"',
            'api_key = os.getenv("API_KEY")',
        ),
        (
            'password = "example-pass-002"',
            'password = os.environ["PASSWORD"]',
        ),
        (
            'secret = "example-token-003"',
            'secret = getpass.getpass()',
        ),
        (
            'api_token = "example-key-004"',
            'api_token = os.getenv("API_TOKEN")',
        )
    ],
    "exceptions": [
        (
            "try:\n    work()\nexcept:\n    pass",
            "try:\n    work()\nexcept ValueError:\n    pass",
        ),
        (
            "try:\n    save()\nexcept BaseException:\n    pass",
            "try:\n    save()\nexcept OSError:\n    handle()",
        ),
        (
            "try:\n    process()\nexcept:\n    log()",
            "try:\n    process()\nexcept TypeError:\n    log()",
        ),
        (
            "try:\n    fetch()\nexcept BaseException:\n    log()",
            "try:\n    fetch()\nexcept TimeoutError:\n    log()",
        )
    ],
    "eval_calls": [
        (
            "result = eval(request_data)",
            "result = int(request_data)",
        ),
        (
            "value = eval(text)",
            "value = str(text)",
        ),
        (
            "parsed = eval(payload)",
            "import json\nparsed = json.loads(payload)",
        ),
        (
            "answer = eval(expression)",
            "answer = float(expression)",
        )
    ]
}

def generate_dataset():
    rows = []
    for family, pairs in PAIRS.items():
        for pair_number, (risky, safe) in enumerate(
                pairs, start=1
        ):
            group_id = f"{family}_{pair_number}"

            for label, code in [(1, risky), (0, safe)]:
                ast.parse(code)

                rows.append({
                    "id": f"V3_{len(rows) + 1:03d}",
                    "code": code,
                    "label": label,
                    "family": family,
                    "group_id": group_id,
                    "source": "synthetic_manual_v3",
                })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id", "code", "label",
                "family", "group_id", "source"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Dataset V3 generated:", OUTPUT)
    print("Total samples:", len(rows))
    print("Risky:", sum(row["label"] == 1 for row in rows))
    print("Not risky:", sum(row["label"] == 0 for row in rows))
    print("Groups:", len(set(row["group_id"] for row in rows)))


if __name__ == "__main__":
    generate_dataset()
