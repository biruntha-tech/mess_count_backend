# mess_count_backend

This is the FastAPI backend for the MessCount application.

## Setup

1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment: `.\venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your MySQL credentials.
5. Run the server: `uvicorn main:app --reload`
