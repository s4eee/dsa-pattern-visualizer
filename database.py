import os
import sqlite3

# This calculates the exact absolute directory path where app.py lives
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dsa_tool.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            code_snippet TEXT,
            detected_pattern TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_analysis(code, pattern):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analysis_history (code_snippet, detected_pattern)
        VALUES (?, ?)
    ''', (code, pattern))
    conn.commit()
    conn.close()
    print(f"✅ Securely wrote entry to: {DB_PATH}")