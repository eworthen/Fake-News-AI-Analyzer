from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load pre-trained models
model_name = "mikiohat/distilbert-base-uncased-LoRA-finetuned-fake-or-real-news"
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(model_name)
ai_detector = pipeline("text-classification", model="roberta-base-openai-detector")
fake_news_model = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Define label mapping
label_mapping = {"LABEL_0": "FAKE", "LABEL_1": "REAL"}

def fetch_article(url):
    """Fetch and extract article text from the URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all('p')
        article_text = " ".join([p.get_text() for p in paragraphs])
        return article_text
    except requests.exceptions.RequestException as e:
        return str(e)

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze the content or URL submitted via POST request.
    """
    data = request.json
    content = data.get("content", "")
    is_url = data.get("is_url", False)
    result = {}


    # Handle URL-based content
    if is_url:
        article_text = fetch_article(content)
        if not article_text or "Failed" in article_text:
            return jsonify({"error": f"Failed to fetch article content from URL: {content}"}), 400
        content = article_text

    # Analyze the content
    try:
        ai_detection = ai_detector(content)
        fake_news_classification = fake_news_model(content)

        result = {
            "ai_generated": {
                "label": label_mapping.get(ai_detection[0]["label"], ai_detection[0]["label"]),
                "confidence": ai_detection[0]["score"]
            },
            "fake_news": {
                "label": label_mapping.get(fake_news_classification[0]["label"], fake_news_classification[0]["label"]),
                "confidence": fake_news_classification[0]["score"]
            },
            "content_preview": content[:500]  # Include a preview of the analyzed content
        }
    except Exception as e:
        return jsonify({"error": f"Failed to analyze content: {str(e)}"}), 500

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
