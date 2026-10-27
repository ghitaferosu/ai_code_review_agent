# AI Code Review Agent

An AI-powered code review system that combines LLM agents and ML to analyze GitHub pull requests.

## Future tasks

- GitHub Pull Request integration
- AI-powered code analysis
- Automated issue detection
- ML-based review prioritization
- Interactive React dashboard


## Tech Stack

- Python
- FastAPI
- React + TypeScript
- LangGraph
- scikit-learn
- PostgreSQL

## Current Status

Phase 1: Backend initialization.


## Getting Started

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the backend:

```bash
python -m uvicorn backend.main:app --reload
```

API documentation:
http://127.0.0.1:8000/docs

### FIRST EXPERIMENT

* **Baseline**: TF-IDF + Logistic Regression
* **Accuracy**: 33.3% (on 6 synthetic samples)
* **Note**: preliminary results only; not representative of real-word vulnerability detection