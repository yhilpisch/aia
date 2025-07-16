# Algorithmic Trading Bootcamp Registration

This is a simple web application to register for the Free Algorithmic Trading Bootcamp. It serves a static landing page and handles registration via a Python Flask backend, storing submissions in a SQLite database and appending to a CSV file.

## Requirements

- Python 3.x
- Flask

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

The app will run on http://localhost:5000.

## Data Storage

- Registrations are saved to `registrations.db` (SQLite3).
- Each registration is appended to `registrations.csv`.
