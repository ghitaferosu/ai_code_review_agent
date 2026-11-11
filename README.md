# AI Code Review Agent

A Python-based code review project that analyzes GitHub pull requests using **static analysis** and experiments with **machine learning** for code-risk classification.

**Status:** Work in progress — static analysis, experimental ML inference, hybrid code analysis, and GitHub pull-request hybrid review are implemented in FastAPI (through Lesson 8 of the 12-lesson plan). This is an educational/portfolio project, **not a production security scanner**.

## What works today

- **FastAPI backend** with interactive OpenAPI documentation.
- **GitHub Pull Request integration**: retrieve changed files from a PR.
- **Python static analysis**: detect selected code patterns such as direct `eval()`, bare `except:`, hardcoded credential-like assignments, and `subprocess` calls with `shell=True`.
- **PR-level static review**: fetch changed Python files at the PR head commit, analyze their full content, and report issues with filenames.
- **Offline ML experiments** comparing character-level TF-IDF + Logistic Regression, AST features + Logistic Regression, and a hybrid TF-IDF + AST model.
- **Experimental ML inference API** (`POST /analysis/ml`) using a locally exported TF-IDF + Logistic Regression model trained on synthetic Dataset V3.
- **Hybrid source analysis** (`POST /analysis/hybrid`): combines static findings and ML classification, with an agreement indicator and readable summary.
- **Hybrid GitHub PR review** (`POST /reviews/hybrid`): analyzes each changed, non-deleted Python file and returns per-file findings, ML predictions, and totals.
- **Synthetic datasets and automated tests** for feature extraction, dataset validation, model comparisons, and API behavior.

> The static analyzer implements a limited set of heuristics. A clean result does **not** prove that code is secure. ML labels indicate selected risk patterns, not a complete vulnerability assessment.

## Tech stack

- Python
- FastAPI and Pydantic
- httpx and the GitHub REST API
- Python `ast`
- pandas and NumPy
- scikit-learn: `TfidfVectorizer`, `FunctionTransformer`, `FeatureUnion`, `LogisticRegression`
- pytest
- joblib for local model serialization

**Future work:** stronger independent evaluation, risk prioritization, diff-line filtering, optional local code LLM, and a frontend/dashboard.

## Architecture

```text
Python snippet --------------------------+
                                          |
GitHub pull request -> GitHub REST API    |
                        |                 |
                        v                 |
               Changed Python files      |
                        |                 |
                        +-----------------+
                                          |
                      +-------------------+------------------+
                      |                                      |
                      v                                      v
             Static analyzer                         TF-IDF V3 classifier
             (Python AST rules)                      (Logistic Regression)
                      |                                      |
                      +-------------------+------------------+
                                          |
                                          v
                              Hybrid analysis report
                         (findings + ML + agreement)
```

The API also retains dedicated static-analysis and ML-analysis endpoints. The deployed ML inference path uses **TF-IDF V3**, not the separately evaluated AST-feature or feature-union hybrid ML estimators. Here, *hybrid review* means combining rule-based static findings and an ML prediction in the response.

```text
backend/
  main.py                         # FastAPI endpoints
  services/
    static_analyzer.py            # AST-based rules
    ml_service.py                 # Load and run exported ML model
    hybrid_review_service.py      # Combine static and ML outputs
    pr_review_service.py          # Static GitHub PR review
    hybrid_pr_review_service.py   # Hybrid GitHub PR review
  models/
    analysis_models.py            # Static-analysis schemas
    ml_models.py                  # ML request/response schemas
    hybrid_models.py              # Hybrid request/response schemas
  ml/
    export_model.py               # Train/export local V3 inference artifact
```

## Getting started

Use Python with a virtual environment.

```bash
git clone https://github.com/ghitaferosu/ai_code_review_agent.git
cd ai_code_review_agent

python -m venv .venv
```

Activate the environment:

- **Windows PowerShell:** `\.venv\Scripts\Activate.ps1`
- **macOS/Linux:** `source .venv/bin/activate`

Install requirements:

```bash
python -m pip install -r requirements.txt
```

Generate Dataset V3 (if it is not present) and export the local inference model:

```bash
python -m backend.ml.generate_dataset_v3
python -m backend.ml.export_model
```

The exporter trains the **TF-IDF V3 pipeline on the 40 synthetic V3 samples** and writes `models/code_risk_v3.joblib`. This generated file is excluded from Git. It must be present locally to use `/analysis/ml`, `/analysis/hybrid`, or `/reviews/hybrid`; without it, those endpoints can return HTTP 503. The demonstration model has not been validated as a real-world security scanner.

Start the API from the repository root:

```bash
python -m uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for Swagger UI.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check backend health |
| `POST` | `/reviews` | Placeholder review request (returns `pending`) |
| `GET` | `/github/{owner}/{repo}/pulls/{pull_number}/files` | List changed files in a GitHub PR |
| `POST` | `/analysis/python` | Analyze supplied Python source with static rules |
| `POST` | `/reviews/static` | Analyze Python files changed in a GitHub PR |
| `POST` | `/analysis/ml` | Experimental TF-IDF V3 prediction on Python source |
| `POST` | `/analysis/hybrid` | Combine AST findings and ML prediction on Python source |
| `POST` | `/reviews/hybrid` | Hybrid review of changed Python files in a GitHub PR |

### Analyze Python source

```bash
curl -X POST http://127.0.0.1:8000/analysis/python \
  -H "Content-Type: application/json" \
  -d '{"code": "result = eval(user_input)"}'
```

### Analyze a pull request

```bash
curl -X POST http://127.0.0.1:8000/reviews/static \
  -H "Content-Type: application/json" \
  -d '{"repository": "fastapi/fastapi", "pull_request_number": 1}'
```

### Experimental ML inference

```bash
curl -X POST http://127.0.0.1:8000/analysis/ml \
  -H "Content-Type: application/json" \
  -d '{"code": "result = eval(user_input)"}'
```

Response fields: `prediction` (0 or 1), `label` (`not_risky` or `risky`), `risk_probability` (the model's score for class 1), and `model` (`tfidf_v3`). **The score is not a calibrated real-world vulnerability probability.**

### Hybrid analysis of a Python snippet

```bash
curl -X POST http://127.0.0.1:8000/analysis/hybrid \
  -H "Content-Type: application/json" \
  -d '{"code": "password = \"demo_value\"\nresult = eval(user_input)"}'
```

Returns `static_analysis` (language, issue count and issue list), `ml_analysis`, `agreement`, and `summary`. The `agreement` boolean compares whether **any** static issue was found to whether ML predicts class 1. It is *not* a correctness or confidence measure, and even maintainability findings count toward this simple comparison.

### Hybrid review of a GitHub pull request

```bash
curl -X POST http://127.0.0.1:8000/reviews/hybrid \
  -H "Content-Type: application/json" \
  -d '{"repository": "OWNER/REPO", "pull_request_number": 1}'
```

Replace `OWNER/REPO` and the PR number with an accessible repository and pull request. The response includes `repository`, `pull_request_number`, `commit_sha`, `analyzed_files`, `issues_count`, and `files`. Each file entry contains a filename and its static/ML hybrid report. A PR with no matching Python files returns `files: []` and zero counts.

The PR-level implementations analyze the **full content of changed, non-deleted Python files** at the PR head commit, not only added lines in the diff. They limit each review to **10 Python files** and **100,000 characters per file**. Findings can therefore refer to pre-existing lines. GitHub API access, rate limits, and repository permissions can affect requests.

Invalid Python syntax returns HTTP 422 for snippet ML/hybrid endpoints. Model-file access errors can return HTTP 503; PR review also reports validation and GitHub API failures.

## Machine learning experiments

All metrics below are from **small synthetic datasets** and should be interpreted as development results, **not** as reliable estimates of real-world vulnerability detection.

### Initial baseline — Dataset V1

Character-level TF-IDF (2–5 character n-grams) with Logistic Regression. A 24-example dataset was split into 18 training and 6 test examples.

| Model | Accuracy | Risky-class F1 |
| --- | ---: | ---: |
| Majority-class dummy baseline | 50.0% | — |
| TF-IDF + Logistic Regression | 33.3% | 0.333 |

### First AST and hybrid comparison — V1 holdout

After correcting AST feature extraction:

| Model | Accuracy | Risky-class F1 |
| --- | ---: | ---: |
| TF-IDF | 33.3% | 0.333 |
| AST | 100.0% | 1.000 |
| Hybrid | 100.0% | 1.000 |

The holdout contains only **6 examples** and overlaps conceptually with the hand-designed AST rules.

### Challenge V2 — 10 additional synthetic examples

An exploratory challenge set using indirect calls, import aliases, hardcoded API-key patterns, broad exception handling, and dynamic execution:

| Model | Accuracy | Precision (risky) | Recall (risky) | F1 (risky) |
| --- | ---: | ---: | ---: | ---: |
| TF-IDF | 90.0% | 1.000 | 0.800 | 0.889 |
| AST | 50.0% | 0.000 | 0.000 | 0.000 |
| Hybrid | 60.0% | 1.000 | 0.200 | 0.333 |

These results motivated improvements to the AST feature extractor. **Challenge V2 was used for error analysis and is no longer an untouched final test set.**

### Dataset V3 — grouped validation

A new **40-example synthetic dataset** uses 20 contrastive pairs, with each pair assigned a `group_id`. `GroupShuffleSplit` kept groups separate: **30 training / 10 validation** examples (15 / 5 groups).

| Model | Accuracy | Risky-class F1 |
| --- | ---: | ---: |
| TF-IDF | 100.0% | 1.000 |
| AST | 80.0% | 0.800 |
| Hybrid | 80.0% | 0.800 |

Both AST and Hybrid made two errors on that validation split: an environment-loaded password was flagged, and a `BaseException` handler was missed. Coefficient and decision-score inspection helped explain the errors.

**Limitations:** Tiny, manually generated datasets; template similarity across groups; hand-engineered features reflecting known target patterns; and repeated development-time inspection. A larger, truly independent evaluation is required before making performance claims. Higher scores do **not** establish security effectiveness.

## Reproduce experiments

Run these commands from the repository root (after installing dependencies):

```bash
# Initial TF-IDF baseline
python -m backend.ml.train_model

# V1 comparison: TF-IDF vs AST vs Hybrid
python -m backend.ml.compare_models

# Generate and evaluate challenge cases
python -m backend.ml.generate_challenge
python -m backend.ml.evaluate_challenge

# Generate Dataset V3 and run grouped validation
python -m backend.ml.generate_dataset_v3
python -m backend.ml.train_v3
```

To run the test suite:

```bash
python -m pytest -v
```

Generated model files may be excluded from version control. Only load `joblib` artifacts from sources you trust.

## Roadmap

- [x] FastAPI foundation and health endpoint
- [x] GitHub PR file retrieval
- [x] Python AST static analyzer and PR-level static review
- [x] Initial labeled synthetic dataset and TF-IDF baseline
- [x] AST and hybrid ML experiments, error analysis, grouped Dataset V3
- [ ] Train and select a model using a stronger evaluation protocol and independent test data
- [x] Expose experimental TF-IDF V3 ML inference through FastAPI
- [x] Combine static findings and ML signals in a hybrid snippet report
- [x] Extend hybrid analysis to GitHub pull requests (Lesson 8)
- [ ] Add risk scoring and prioritization (Lesson 9)
- [ ] Improve coverage, error handling, tests, and documentation
- [ ] Optional: local open-weight code LLM and user interface

## Responsible use

This project is for learning and experimentation. Its findings can contain false positives and false negatives. Do not use its output as a substitute for professional security review, comprehensive static-analysis tooling, or testing.
