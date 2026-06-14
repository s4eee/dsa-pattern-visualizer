import os
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
        prompt = f"""
        Analyze the following programming code snippet and identify its primary Data Structures & Algorithms (DSA) core structural pattern (e.g., Two Pointers, Sliding Window, Fast and Slow Pointers, Merge Intervals, Breadth-First Search, Depth-First Search, etc.).

        Provide your response strictly in the following format:
        PATTERN: [Name of the Pattern]
        EXPLANATION: [A brief 2-3 sentence clear explanation of why this pattern applies and how it operates within the context of the provided code snippet.]

        Code Snippet:
        {user_code}
        """

        # Call OpenRouter using the free multi-model routing tier
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse formatting rules
        lines = ai_response.strip().split("\n")
        detected_pattern = "Unknown Pattern"
        explanation = ai_response

        for line in lines:
            if line.startswith("PATTERN:"):
                detected_pattern = line.replace("PATTERN:", "").strip()
            elif line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()

        # Database logging
        save_analysis(user_code, detected_pattern)
        
        return jsonify({
            "status": "success",
            "pattern": detected_pattern,
            "explanation": explanation
        })

    except Exception as e:
        print(f"Error during OpenRouter API execution loop: {e}")
        return jsonify({"status": "error", "message": "Failed to connect or process with AI API."}), 500

if __name__ == '__main__':
    app.run(debug=True)