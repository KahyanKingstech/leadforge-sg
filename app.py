import os
from flask import Flask, request, render_template
import psycopg2
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load local .env file (for dev)
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def lead_form():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        # ✅ Save locally in PostgreSQL
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO leads (name, email, phone, message) VALUES (%s, %s, %s, %s)',
            (name, email, phone, message)
        )
        conn.commit()
        cur.close()
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
