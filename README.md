# Fake News AI Analyzer

A containerized Flask web app that analyzes news content to determine whether it was AI-generated and classifies it as real or fake. The app uses the `llama3-8b-8192` model via the Groq Cloud API and implements Redis-backed rate limiting for abuse protection. Users can analyze either plain text or URLs through a lightweight, server-rendered UI.

---

## Author

**Ethan Worthen**

---

## License

Licensed under the [MIT License](LICENSE)

---

## 🚀 Features

- Accepts user input as raw text or a news article URL
- Detects if content is AI-generated
- Classifies articles as "Real" or "Fake" news
- Simple and clean UI built with Flask + Jinja2 templates
- Built-in rate limiting to prevent API abuse
- Honeypot form protection to block bots

---

## Project Structure

```
project-root/
├── flask/
│   ├── app/
│   │   ├── app.py              # Main Flask application logic
│   │   └── templates/
│   │       └── index.html      # User interface
│   └── Dockerfile              # Flask container image
├── docker-compose.yml          # Orchestrates Flask + Redis services
├── requirements.txt            # Python packages
├── .env                        # Your Groq API key and config
├── .env.example                # Template .env file
├── LICENSE
└── README.md                   # You're here!
```

---

## Requirements

- Docker  
- Docker Compose  
- Groq API Key (https://console.groq.com)

---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/fake-news-ai-analyzer.git
   cd fake-news-ai-analyzer
   ```

2. **Create the `.env` File**
   ```bash
   cp .env.example .env
   # Then edit the file and add your GROQ_API_KEY
   ```

3. **Build and Start the Containers**
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**
   Visit: [http://localhost:5000](http://localhost:5000)

---

## API Endpoint

### POST `/analyze`

Accepts plain text or a URL and returns AI and fake news classification results.

#### Request:
```json
{
  "content": "Text or URL to analyze",
  "is_url": true
}
```

#### Response:
```json
{
  "analysis": "AI-generated or not, and fake or real news.",
  "content_preview": "First 50 words of extracted or submitted content."
}
```

---

## Technical Details

### Flask Backend
- Handles form submissions and API POST requests
- Parses URLs using `BeautifulSoup`
- Sends input to Groq API via `requests`
- Applies Redis-backed rate limiting with `flask-limiter`
  - `10/hour` global per IP
  - `5/minute` on `/analyze`

### Groq API
- Model: `llama3-8b-8192`
- Endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Max Tokens: 1200

---

## Security

- **Rate Limiting**: Via Redis using `flask-limiter`
- **Bot Protection**: Honeypot field (`hp_field`)
- **Input Validation**: Max 800-word limit for direct text

---

## Future Improvements

- Export results to PDF or CSV
- Summarize articles using AI
- Add database support for tracking results
- Improve mobile responsiveness
- Admin dashboard for reviewing submissions

---

## Contributors

- Ethan Worthen
