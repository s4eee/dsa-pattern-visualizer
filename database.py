import sqlite3

DB_NAME = "dsa_tool.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table to store code analyzed by users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            code_snippet TEXT,
            detected_pattern TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_analysis(code, pattern):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (code_snippet, detected_pattern) VALUES (?, ?)", (code, pattern))
    conn.commit()
    conn.close()