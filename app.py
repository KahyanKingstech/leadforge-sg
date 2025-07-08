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
HUB_API_URL = os.getenv('HUB_API_URL')

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

        # ✅ Send to Hub
        if HUB_API_URL:
            try:
                data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "message": message,
                    "source_country": "SG"
                }
                res = requests.post(HUB_API_URL, json=data)
                if res.ok:
                    return "<h2>✅ Lead Submitted Successfully!</h2><a href='/'>Back</a>"
                else:
                    return f"<h2>❌ Error sending to Hub: {res.status_code}</h2><a href='/'>Back</a>"
            except Exception as e:
                return f"<h2>❌ Error sending to Hub: {e}</h2><a href='/'>Back</a>"
        else:
            return "<h2>✅ Lead saved locally (no Hub URL configured)</h2><a href='/'>Back</a>"

    return render_template('form.html')

@app.route('/view')
def view_leads():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name, email, phone, message, created_at FROM leads ORDER BY created_at DESC')
    leads = cur.fetchall()
    cur.close()
    conn.close()

    html = "<h1>All Leads</h1><table border='1'><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Message</th><th>Created At</th></tr>"
    for lead in leads:
        html += f"<tr><td>{lead[0]}</td><td>{lead[1]}</td><td>{lead[2]}</td><td>{lead[3]}</td><td>{lead[4]}</td><td>{lead[5]}</td></tr>"
    html += "</table>"
    return html

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
