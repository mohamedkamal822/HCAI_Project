# HCAI_Project
# Ishara – Egyptian Sign Language Learning Chatbot

**Team:** CoMind

**Tagline:** Breaking Barriers, Expanding Access.

## About the Project

Ishara is an educational chatbot designed to help Arabic-speaking beginners learn Egyptian Sign Language (ESL) through verified sign language video demonstrations.

The project aims to make learning sign language more accessible and interactive by allowing users to search for words and phrases in either Arabic or English and explore their corresponding signs.

## Key Features

- **Word and Phrase Search:** Users can enter words and phrases in Arabic or English.
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
    │   └── prepare_dataset.py
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

### 4. Build the Sign Index

```bash
python backend/build_signs_index.py
```

### 5. Run the Backend

```bash
python -m uvicorn backend.main:app --reload
```

The backend will be available at:

`http://127.0.0.1:8000`

### 6. Open the Frontend

Open `frontend/index.html` in your browser.

*Note: The frontend and backend must be configured to communicate with each other for the application to work correctly.*

## Project Scope

Ishara currently focuses on searching a predefined collection of verified Egyptian Sign Language signs. Its results are limited to the available dataset, ensuring that the system does not present unsupported or unverified translations.

## Team

**CoMind** – Human-AI Interaction Course Project