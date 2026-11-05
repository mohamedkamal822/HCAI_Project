# HCAI_Project
# Ishara – Egyptian Sign Language Learning Chatbot

**Team:** CoMind

**Tagline:** Breaking Barriers, Expanding Access.

## About the Project

Ishara is an educational chatbot designed to help Arabic-speaking beginners learn Egyptian Sign Language (ESL) through verified sign language video demonstrations.

The project aims to make learning sign language more accessible and interactive by allowing users to search for words and phrases in either Arabic or English and explore their corresponding signs.

## Key Features

- **Word Search:** Users can enter words in Arabic or English.
- **Verified Sign Demonstrations:** Displays corresponding sign language videos from a predefined dataset.
- **Reliable Results:** Only verified signs available in the dataset are displayed.
- **Fallback Handling:** If an exact match is not found, the system informs the user that no verified result is currently available.

## How It Works

1. The user enters a word or phrase through the chatbot interface.
2. The frontend sends the input to the backend.
3. The backend searches the available sign database.
4. If a matching verified sign is found, its video is returned and displayed.
5. If no match exists, the chatbot provides an appropriate fallback response.

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **Data Storage:** JSON-based sign index
- **Dataset:** Egyptian Sign Language video collection

## Project Structure

```text
HCAI_Project/
├── README.md
├── Milestone_1.pdf
├── Week 3 Users and data.pdf
├── Week 4 Objectives and Ladder.pdf
├── CoMind week5.pdf
│
└── ISHARA/
    ├── backend/
    │   ├── main.py
    │   ├── signs.json
    │   ├── build_signs_index.py
    │   ├── prepare_dataset.py
    │   └── app/
    │       ├── api/
    │       │   ├── routes.py
    │       │   └── schemas.py
    │       ├── core/config.py
    │       ├── domain/catalog.py
    │       ├── llm/
    │       │   ├── gemini.py
    │       │   ├── prompts.py
    │       │   └── README.md
    │       └── services/traces.py
    │
    ├── frontend/
    │   └── index.html
    │
    ├── dataset_selected_h264/
    │
    └── convert_videos.py
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/mohamedkamal822/HCAI_Project.git
cd HCAI_Project/ISHARA
```

### 2. Create and Activate a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the model and handover resource

Copy `ISHARA/.env.example` to `ISHARA/.env`, then set a new Google AI Studio Gemini API key. Do not commit `.env`.

After revoking any exposed key and adding its replacement, set `GEMINI_KEY_ROTATED_AT` to the date of rotation. The backend refuses model calls until this confirmation is present.

Optionally set `HUMAN_HANDOVER_URL` to a verified Egyptian Sign Language instructor or official support resource before the presentation.

The default model is `gemini-3.5-flash-lite`; `GEMINI_MODEL` in `.env` can override it. Choose a model returned by `GET /models`.

### 5. Build the Sign Index

```bash
python backend/build_signs_index.py
```

### 6. Run the Backend

```bash
python -m uvicorn backend.main:app --reload
```

The backend will be available at:

`http://127.0.0.1:8000`

### 7. Open the Frontend

Open `frontend/index.html` in your browser.

*Note: The frontend and backend must be configured to communicate with each other for the application to work correctly.*

## Project Scope

Ishara currently focuses on searching a predefined collection of verified Egyptian Sign Language signs. Its results are limited to the available dataset, ensuring that the system does not present unsupported or unverified translations.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the trace-first system architecture and Explainability flow.

Week 5 check-in materials, including the conversation flow, Golden Rules checklist, and Appendix A prompt log, are in [WEEK5_DELIVERABLES.md](WEEK5_DELIVERABLES.md).

## Team

**CoMind** – Human-AI Interaction Course Project
