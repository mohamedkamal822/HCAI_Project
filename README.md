# Ishara — Egyptian Sign Language Learning Assistant

**Team:** CoMind
**Project:** HCAI human–AI interaction term project
**Tagline:** Breaking Barriers, Expanding Access.

Ishara helps Arabic-speaking beginners explore Egyptian Sign Language through a searchable library of sign videos and a short interactive quiz. Search results come from the team's sign catalog; Gemini can provide a short, learning-focused response only after a verified sign is found.

## Features

- Search using Arabic, English, Franco-Arabic, and reviewed aliases.
- Display catalog-backed sign labels, explanations, and local videos.
- Apply the full R0–R7 decision flow: help, exact labels, reviewed aliases, related candidates, no match, out-of-scope input, system errors, and safety handover.
- Show a decision trace through the “Why this result?” control.
- Practice with a randomized sign-video quiz, score progress, and retry.
- Offer recovery actions and optional handover to a configured instructor or official resource.
- Use Gemini through the FastAPI backend; generated text does not select signs or videos.

Related suggestions use normalized character similarity with threshold `0.70`; this is not semantic similarity. A related candidate is never presented as the answer to the searched term. Franco labels belong to R1; team-reviewed aliases belong to R2.

## Architecture

The bilingual browser interface (`frontend/index.html`, `style.css`, and `script.js`) sends chat, alternatives, feedback, and quiz requests to the FastAPI backend (`backend/`). The backend validates and normalizes input, applies deterministic safeguards and matching rules against `backend/signs.json` plus reviewed data in `backend/aliases.json`, serves videos from `dataset/`, and records bounded in-memory traces plus JSONL audit records. Gemini can rephrase R1–R4 responses using verified facts; it cannot choose a sign or video. A validated template remains available if Gemini is unavailable or returns off-topic text.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the system diagram and [WEEK5_DELIVERABLES.md](WEEK5_DELIVERABLES.md) for the conversation flow, Golden Rules checklist, model-demo status, and prompt log.

## Project Structure

```text
HCAI_Project/
├── ARCHITECTURE.md
├── WEEK5_DELIVERABLES.md
├── README.md
└── ISHARA/
    ├── .env.example
    ├── requirements.txt
    ├── backend/
    │   ├── main.py
    │   ├── signs.json
    │   ├── aliases.json
    │   ├── evaluation_test_set.csv
    │   ├── run_evaluation.py
    │   └── app/
    │       ├── api/          # FastAPI routes and request schemas
    │       ├── core/         # Configuration
    │       ├── domain/       # Sign catalog and matching rules
    │       ├── llm/          # Gemini client and prompts
    │       └── services/     # Conversation flow, traces, and JSONL audit logs
    ├── frontend/
    │   ├── index.html
    │   ├── style.css
    │   └── script.js
    └── dataset/               # Local sign videos
```

## Getting Started

### Requirements

- Python 3.11 or newer
- A Google AI Studio API key for Gemini-generated replies (optional for catalog search and quiz)

### Install

From the repository root:

```powershell
cd ISHARA
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY` to a valid key. If the key was rotated after exposure, set `GEMINI_KEY_ROTATED_AT` to the rotation date in `YYYY-MM-DD` format. Do not commit `.env` or share the key. The default model is `gemini-3.5-flash-lite`; `GEMINI_MODEL` can override it with a model available to your AI Studio key. Set `HUMAN_HANDOVER_URL` to a verified instructor or official resource if you want the handover action to open a destination.

### Start the backend

Run from the `ISHARA` directory:

```powershell
python -m uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

### Start the frontend

In a second terminal, from the `ISHARA` directory:

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500` while the backend is running.

## API Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/chat` | Search the sign catalog and return the result, trace ID, and optional grounded model reply. |
| `POST` | `/alternatives` | Ask for the next candidate without repeating suggestions already shown. |
| `GET` | `/signs` | Browse the catalog. |
| `GET` | `/quiz` | Get randomized quiz questions and distinct distractors from the full catalog. |
| `GET` | `/trace/{trace_id}` | Retrieve the decision trace for a response. |
| `POST` | `/feedback` | Submit feedback on a result; feedback is appended to the JSONL audit log. |
| `GET` | `/models` | List Gemini models available to the configured key. |
| `GET` | `/videos/{path}` | Serve a catalog video. |

## Evaluation

The 40-case prompt set and runner are in `ISHARA/backend/evaluation_test_set.csv` and `ISHARA/backend/run_evaluation.py`.

Run the evaluator from the `ISHARA` directory:

```powershell
python backend\run_evaluation.py
```

Or, from the `ISHARA/backend` directory:

```powershell
python run_evaluation.py
```

Without `--url`, the runner uses FastAPI's in-process `TestClient`. To evaluate a backend that is already running, pass its URL:

```powershell
python backend\run_evaluation.py --url http://127.0.0.1:8000
```

Each run writes detailed JSONL results and a JSON summary to `ISHARA/backend/evaluation_outputs/`. These generated reports are ignored by Git. The backend's JSONL audit logs are stored outside the source tree under the operating system's temporary `ishara/logs/` directory by default; set `ISHARA_DATA_DIR` to choose a persistent data directory outside the project.

## Scope and Limitations

Ishara is a learning prototype, not an authoritative translation service. Its verified results are limited to the included catalog, and related suggestions are approximate string matches. For uncertain signs, consult a qualified Egyptian Sign Language instructor. The handover link is optional and must be configured by the project team.

## Team

**CoMind** — Human-AI Interaction Course Project
