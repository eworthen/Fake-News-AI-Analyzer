from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bs4 import BeautifulSoup
import requests
import os
import json
from werkzeug.middleware.proxy_fix import ProxyFix

# Flask setup
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

# Rate limiter: 1 requests/day per IP globally, 5/minute for /analyze
limiter = Limiter(
    key_func=get_remote_address,
    #storage_uri="redis://127.0.0.1:6379", - Production
    storage_uri="redis://redis:6379",
    default_limits=["10 per hour"]
)
limiter.init_app(app)

# API Keys and Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
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
        recaptcha_token = request.form.get("g-recaptcha-response")
        if not recaptcha_token:
            result = {"error": "reCAPTCHA token is missing."}
        else:
            # Verify with Google
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            verify_response = requests.post(
                verify_url,
                data={
                    "secret": RECAPTCHA_SECRET_KEY,
                    "response": recaptcha_token
                }
            )
            verify_result = verify_response.json()
            if not verify_result.get("success"):
                result = {"error": "reCAPTCHA validation failed."}
            else:
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

    return render_template(
        "index.html",
        result=result,
        text=text,
        is_url=is_url,
        recaptcha_site_key=RECAPTCHA_SITE_KEY
    )

# Run the app
if __name__ == "__main__":
    print(f"🚀 Fake News Analyzer running with Groq model: {GROQ_MODEL}")
    app.run(host="0.0.0.0", port=5000)
