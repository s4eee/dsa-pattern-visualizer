import os
import json
import re
import sqlite3
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from database import init_db, save_analysis

load_dotenv()

app = Flask(__name__)
init_db()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    data = request.get_json()
    user_code = data.get('code', '')
    
    if not user_code.strip():
        return jsonify({"status": "error", "message": "Code snippet cannot be empty!"}), 400

    try:
        prompt = f"""
        Analyze the following programming code snippet and identify its primary Data Structures & Algorithms (DSA) core structural pattern (e.g., Two Pointers, Sliding Window, Fast and Slow Pointers, Merge Intervals, Breadth-First Search, Depth-First Search, etc.).

        You must respond STRICTLY with a valid JSON object. Do not include any markdown formatting, backticks, or 'json' tags. Match this exact structural schema:
        {{
            "pattern": "Name of the DSA Pattern",
            "explanation": "A clear 2-sentence explanation of why this pattern applies to this code.",
            "practice_questions": [
                {{
                    "title": "Question Title 1",
                    "difficulty": "Easy",
                    "description": "Brief 1-sentence prompt of what the problem asks to solve.",
                    "url": "https://leetcode.com/problems/problem-slug-1/"
                }},
                {{
                    "title": "Question Title 2",
                    "difficulty": "Medium",
                    "description": "Brief 1-sentence prompt of what the problem asks to solve.",
                    "url": "https://leetcode.com/problems/problem-slug-2/"
                }},
                {{
                    "title": "Question Title 3",
                    "difficulty": "Hard",
                    "description": "Brief 1-sentence prompt of what the problem asks to solve.",
                    "url": "https://leetcode.com/problems/problem-slug-3/"
                }}
            ]
        }}

        Code Snippet to analyze:
        {user_code}
        """

        # FIX: Added max_tokens guardrail to fit within OpenRouter free token allocation limits
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            timeout=15.0
        )
        
        raw_content = response.choices[0].message.content.strip()

        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if match:
            clean_json_str = match.group(0)
        else:
            raise ValueError("No valid JSON structure found in the AI response.")
        
        result_data = json.loads(clean_json_str)

        try:
            save_analysis(user_code, result_data.get("pattern", "Unknown"))
        except Exception as db_err:
            print(f"Database Save Warning: {db_err}")
        
        return jsonify({
            "status": "success",
            "pattern": result_data.get("pattern"),
            "explanation": result_data.get("explanation"),
            "questions": result_data.get("practice_questions", [])
        })

    except Exception as e:
        print(f"💥 Error during execution lifecycle: {e}")
        return jsonify({"status": "error", "message": f"Failed to parse structure: {str(e)}"}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'dsa_tool.db')
        conn = sqlite3.connect('dsa_tool.db')
        cursor = conn.cursor()
        
        # SAFETY CHECK: Ensure table exists so an empty database doesn't crash the frontend
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                code_snippet TEXT,
                detected_pattern TEXT
            )
        ''')
        
        cursor.execute('''
            SELECT id, timestamp, code_snippet, detected_pattern 
            FROM analysis_history 
            ORDER BY timestamp DESC LIMIT 10
        ''')
        
        rows = cursor.fetchall()
        print(f"📦 DEBUG DATABASE FETCH: Found {len(rows)} rows in SQLite.") # <-- ADD THIS LINE
        
        conn.close()
        
        history_list = []
        for row in rows:
            history_list.append({
                "id": row[0],
                "timestamp": row[1],
                "code": row[2],
                "pattern": row[3]
            })
            
        return jsonify({"status": "success", "history": history_list})
    except Exception as e:
        print(f"Database Query Error: {e}")
        return jsonify({"status": "error", "message": "Failed to load historical analytics."}), 500

if __name__ == "__main__":
    app.run(debug=True)