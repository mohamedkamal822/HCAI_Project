# CoMind · Ishara — Egyptian Sign Language learning chatbot

CoMind (product name **Ishara**) helps Arabic-speaking beginners learn Egyptian Sign Language (ESL).
A learner types a word in Arabic or English. The backend finds the verified video in a fixed dataset,
labels the result (exact match, related, or no verified match), and explains **why** through a
decision trace. HAI principle: **Explainability**.

## What is in this repository

```
backend/
  main.py            FastAPI app: /chat, /alternatives, /trace/{id}, /feedback, /signs, /quiz
  engine.py          Decision engine: normalization, rules R0–R7, decision trace, template replies
  llm.py             Qwen2.5-7B-Instruct (Hugging Face) rewording + validator + template fallback
  signs.json         Index: one entry per word (56), built by build_signs_index.py
  aliases.json       Team-reviewed alternative words, look-alike words, and notes
  build_signs_index.py, prepare_dataset.py   Dataset preparation scripts
  .env.example       Copy to .env and add your HF_TOKEN (never commit .env)
frontend/
  index.html         Accessible chat + quiz interface (HTML, CSS, JavaScript)
eval/
  test_set.csv       40 labelled test prompts (normal, edge case, out of scope, unsafe)
  run_eval.py        Runs the test set through the backend, saves outputs, computes metrics
convert_videos.py    Converts the selected videos to H.264 with ffmpeg
```

The dataset videos are **not** in the repository (license not stated on Kaggle). Download them yourself (step 2).

## How to run

1. **Install Python 3.10+**, then from the project folder:
   ```bash
   pip install -r requirements.txt
   ```
2. **Get the videos.** Download the *Egyptian Sign Language Recognition* dataset from Kaggle
   (https://www.kaggle.com/datasets/abdullahsherdy/egyptian-sign-language-recognition) into
   `dataset - rebirth copy/`, then run:
   ```bash
   python backend/prepare_dataset.py     # picks one video per word -> dataset_selected/
   python convert_videos.py              # H.264 for browsers -> dataset_selected_h264/
   python backend/build_signs_index.py   # rebuilds backend/signs.json
   ```
   (In `convert_videos.py`, set `FFMPEG` to your ffmpeg path.)
3. **Optional: turn on the language model.** Copy `backend/.env.example` to `backend/.env` and put your
   Hugging Face token in `HF_TOKEN`. Without a token the chatbot still works and uses fixed template replies;
   the "Why this result?" panel says which one wrote the reply.
4. **Start the backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
   Check http://127.0.0.1:8000/ — it shows the number of signs and whether the model is on.
5. **Open the interface:** http://127.0.0.1:8000/app/ (or open `frontend/index.html` with VS Code Live Server).
6. **Run the evaluation:**
   ```bash
   cd eval
   python run_eval.py
   ```
   Results are saved in `eval/outputs/`.

## How a reply is decided

| Rule | When | What the user sees |
|------|------|--------------------|
| R0 | Greeting, help, or quiz request | What CoMind can and cannot do, or a quiz button |
| R1 | Cleaned input equals an Arabic, English or Franco label | Video + badge "✓ Exact match" |
| R2 | Cleaned input equals a team-reviewed alternative word | Video + badge "✓ Exact match (alternative word)" |
| R3 | No exact match; similarity ≥ T (0.70), or a listed look-alike word | Up to 3 videos, badge "≈ Related, not the same word", score and reason |
| R4 | Nothing reaches T, or "Exact matches only" is on | "∅ No verified match", suggestions, and who to ask |
| R5 | Not a word lookup (long sentence or other topic) | What CoMind can do |
| R6 | Server error or timeout | Calm message + Try again / Edit word / Start over |
| R7 | Emergency, interpretation request, insult request, or personal data | Fixed safety message and handover to a person |

Every request writes a **decision trace** (input, cleaning steps, checks, rule, entry, score, threshold,
candidates, settings, model status). The "Why this result?" panel is drawn only from this trace.
The language model receives the trace facts and only rewords R1–R4 replies; `llm.validate()` rejects
any reply that drops the label, names another entry, adds a link, or contradicts the rule, and the
template is used instead. Safety, scope and error messages are always fixed text.

## Versions

- Engine: `engine-1.0 (2026-11-21)`, threshold T = 0.70, similarity: difflib character ratio
- Model: `Qwen/Qwen2.5-7B-Instruct` via Hugging Face Inference Providers, temperature 0, prompt `phrasing-prompt-v1`
- Data: Egyptian Sign Language Recognition (Kaggle, Abdullah Sherdy & Eng Sira), 56 words, one video per word.
  Arabic and English labels were written by the team from the folder names.

## Data and keys

Only public data is used. No personal data is stored; phone numbers and emails are removed before processing.
API keys live in `backend/.env`, which `.gitignore` excludes. Logs (`backend/logs/`) are also excluded.
