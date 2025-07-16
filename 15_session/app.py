from flask import Flask, request, redirect, send_from_directory
import sqlite3
import os
from datetime import datetime
import csv

DB_FILE = 'registrations.db'
CSV_FILE = 'registrations.csv'

app = Flask(__name__, static_folder='.', static_url_path='')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def append_csv(first_name, last_name, email, timestamp):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists or os.stat(CSV_FILE).st_size == 0:
            writer.writerow(['first_name', 'last_name', 'email', 'timestamp'])
        writer.writerow([first_name, last_name, email, timestamp])

@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

@app.route('/register', methods=['POST'])
def register():
    first = request.form.get('first_name', '').strip()
    last = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    if not (first and last and email):
        return "Missing data", 400
    timestamp = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        'INSERT INTO registrations (first_name, last_name, email, timestamp) VALUES (?, ?, ?, ?)',
        (first, last, email, timestamp)
    )
    conn.commit()
    conn.close()
    append_csv(first, last, email, timestamp)
    return redirect('/thankyou')

@app.route('/thankyou', methods=['GET'])
def thank_you():
    return send_from_directory('.', 'thankyou.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)
