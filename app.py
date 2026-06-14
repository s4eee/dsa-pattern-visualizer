import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI  # Switched to the standard OpenAI client layout
from database import init_db, save_analysis

load_dotenv()

app = Flask(__name__)
init_db()

# INITIALIZATION: Connects to OpenRouter using their universal base URL endpoint
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
        # We instruct the AI to return the pattern, explanation, and 3 real LeetCode questions with URLs
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

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Clean up any accidental wrapping strings if the LLM adds them
        ai_response = response.choices[0].message.content.strip()
        if ai_response.startswith("```json"):
            ai_response = ai_response.replace("```json", "", 1)
        if ai_response.endswith("```"):
            ai_response = ai_response.rstrip("```")
        
        # Parse the raw text into a real Python dictionary
        result_data = json.loads(ai_response.strip())

        # DATABASE LOGGING (Keeps your history tracker intact!)
        save_analysis(user_code, result_data.get("pattern", "Unknown"))
        
        return jsonify({
            "status": "success",
            "pattern": result_data.get("pattern"),
            "explanation": result_data.get("explanation"),
            "questions": result_data.get("practice_questions", [])
        })

    except Exception as e:
        print(f"Error during execution: {e}")
        return jsonify({"status": "error", "message": "Failed to parse or analyze code structure."}), 500
# THIS MUST BE FLUSHED TO THE LEFT MARGIN BELOW ALL FUNCTIONS TO BOOT THE APP
if __name__ == "__main__":
    app.run(debug=True)