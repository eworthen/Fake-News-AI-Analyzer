from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bs4 import BeautifulSoup
import requests
import os

# Flask setup
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Rate limiter: 1 requests/day per IP globally, 5/minute for /analyze
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379",  # Match your service name
    default_limits=["1 per day"]
)
limiter.init_app(app)

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"
MAX_RESPONSE_TOKENS = 1200

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY environment variable")

# Utility: Truncate text to a specific word count
def truncate_words(text: str, max_words: int = 800) -> str:
    return " ".join(text.split()[:max_words])

# Utility: Extract readable article content from a URL
def fetch_article(url: str) -> str:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return " ".join(p.get_text() for p in soup.find_all("p"))
    except Exception as e:
        return f"Error: {str(e)}"

# Call Groq API to analyze content
def analyze_with_groq(text: str) -> dict:
    truncated = truncate_words(text)
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a fake news and AI content detector."},
            {"role": "user", "content": f"Analyze this article. Return AI-generated? Real or fake news?\n\n{truncated}"}
        ],
        "max_tokens": MAX_RESPONSE_TOKENS,
        "temperature": 0.2
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return {"result": data["choices"][0]["message"]["content"].strip()}

# API endpoint: Analyze text or URL content
@app.route("/analyze", methods=["POST"])
@limiter.limit("5 per minute")
def analyze_api():
    data = request.get_json(force=True)
    content = data.get("content", "")
    is_url = data.get("is_url", False)

    if not content:
        return jsonify({"error": "Missing content"}), 400

    if is_url:
        content = fetch_article(content)
        if content.startswith("Error:"):
            return jsonify({"error": content}), 400

    try:
        analysis = analyze_with_groq(content)
        return jsonify({
            "analysis": analysis["result"],
            "content_preview": truncate_words(content, max_words=50)
        })
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# Web UI: Form interface
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    text = ""
    is_url = False

    if request.method == "POST":
        # Honeypot anti-bot field
        if request.form.get("hp_field"):
            result = {"error": "Bot submission detected."}
        else:
            text = request.form.get("content", "")
            is_url = request.form.get("is_url", "false") == "true"

            if not text:
                result = {"error": "Missing input content."}
            elif len(text.split()) > 800:
                result = {"error": "Content exceeds 800-word limit. Please shorten your input."}
            else:
                payload = {"content": text, "is_url": is_url}
                with app.test_client() as client:
                    response = client.post("/analyze", json=payload)
                    result = response.get_json() if response.status_code == 200 else {"error": "Analysis failed."}

    return render_template("index.html", result=result, text=text, is_url=is_url)

# Run the app
if __name__ == "__main__":
    print(f"🚀 Fake News Analyzer running with Groq model: {GROQ_MODEL}")
    app.run(host="0.0.0.0", port=5000)
