# Ishara — Egyptian Sign Language Learning Assistant

**Team:** CoMind
**Project:** HCAI human–AI interaction term project
**Tagline:** Breaking Barriers, Expanding Access.

Ishara helps Arabic-speaking beginners explore Egyptian Sign Language through a searchable library of sign videos and a short interactive quiz. Search results come from the team's sign catalog; Gemini can provide a short, learning-focused response only after a verified sign is found.

## Features

- Search using Arabic, English, Franco-Arabic, and reviewed aliases.
- Display catalog-backed sign labels, explanations, and local videos.
- Distinguish exact matches, reviewed alternatives, related candidates, out-of-scope input, and system errors (R1–R6).
- Show a decision trace through the “Why this result?” control.
- Practice with a randomized sign-video quiz, score progress, and retry.
- Offer recovery actions and optional handover to a configured instructor or official resource.
- Use Gemini through the FastAPI backend; generated text does not select signs or videos.

Related suggestions use normalized character similarity with threshold `0.72`; this is not semantic similarity. A related candidate is never presented as the answer to the searched term.

## Architecture

The browser interface (`frontend/`) sends chat and quiz requests to the FastAPI backend (`backend/`). The backend validates input, matches against `backend/signs.json`, serves videos from `dataset_selected_h264/`, records decision traces, and calls Gemini only for verified matches. Model replies pass relevance and format checks; if Gemini is unavailable or its reply fails validation, the verified catalog result remains available without generated text.

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
    │   └── app/
    │       ├── api/          # FastAPI routes and request schemas
    │       ├── core/         # Configuration
    │       ├── domain/       # Sign catalog and matching rules
    │       ├── llm/          # Gemini client and prompts
    │       └── services/     # Decision trace storage
    ├── frontend/
    │   ├── index.html
    │   ├── style.css
    │   └── script.js
    └── dataset_selected_h264/ # Local sign videos
```

## Getting Started

### Requirements

- Python 3.10 or newer
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
| `GET` | `/quiz` | Get quiz questions and video paths. |
| `GET` | `/trace/{trace_id}` | Retrieve the decision trace for a response. |
| `POST` | `/feedback` | Submit feedback on a result. |
| `GET` | `/models` | List Gemini models available to the configured key. |
| `GET` | `/videos/{path}` | Serve a catalog video. |

## Scope and Limitations

Ishara is a learning prototype, not an authoritative translation service. Its verified results are limited to the included catalog, and related suggestions are approximate string matches. For uncertain signs, consult a qualified Egyptian Sign Language instructor. The handover link is optional and must be configured by the project team.

## Team

**CoMind** — Human-AI Interaction Course Project
