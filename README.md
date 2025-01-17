# AI News Analysis App
This project is a web-based application that detects whether a news article is AI-generated and classifies it as real or fake news using machine learning models.

## Author

This project was created by Ethan Worthen

## License

This project is licensed under the [MIT License](LICENSE).

## Features
- Analyze plain text or URL content.
- Detect if the content is AI-generated.
- Classify content as real or fake news.
- Display analysis results on the Angular frontend.

---

## Project Structure
```
project-directory/
├── angular/                   # Angular frontend
├── flask/                     # Flask backend
│   ├── app/
│   │   ├── app.py             # Flask application
│   │   └── requirements.txt   # Python dependencies
├── nginx/                     # Nginx configuration
│   └── default.conf           # Proxy settings for Angular and Flask
├── docker-compose.yml         # Docker configuration
├── README.md                  # Project documentation
```

---

## Requirements
- Docker
- Docker Compose

---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd project-directory
   ```

2. **Build and Start the Containers**
   ```bash
   docker-compose up --build
   ```

3. **Access the Application**
   - Open your browser and navigate to `http://localhost`.
   - The frontend (Angular) will load.
   - The Flask API runs on `http://localhost:5000`.

---

## Flask Backend
The Flask app performs the following:
- Processes user input from the Angular frontend.
- Uses Hugging Face models to detect AI-generated content and classify it as real or fake news.

### Flask API Endpoints
#### `POST /analyze`
- **Request Body**:
  ```json
  {
    "content": "Text or URL to analyze",
    "is_url": "true" or "false"
  }
  ```
- **Response**:
  ```json
  {
    "ai_generated": "LABEL_0 or LABEL_1",
    "ai_confidence": 0.999,
    "fake_news": "FAKE or REAL",
    "fake_confidence": 0.987,
    "article_text": "Extracted article text (first 500 characters)"
  }
  ```

---

## Angular Frontend
The Angular app allows users to:
- Paste or type content.
- Enter a URL for analysis.
- View detailed results of the analysis.

### How to Use:
1. Paste the text or URL into the provided textarea.
2. Click the "Analyze" button to submit the content.
3. View the analysis results.

---

## Nginx Configuration
Nginx acts as a reverse proxy:
- Routes requests to the Angular frontend (`http://localhost`).
- Routes API requests to the Flask backend (`http://localhost/`).

### Nginx Configuration (`default.conf`):
```nginx
server {
    listen 80;

    server_name localhost;

    location / {
        proxy_pass http://angular:4200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://flask:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Development Notes
### Backend
- **Models Used**:
  - `roberta-base-openai-detector` (AI detection)
  - `mikiohat/distilbert-base-uncased-LoRA-finetuned-fake-or-real-news` (Fake news detection)

### Frontend
- Angular app is built with `@angular/cli` and serves on port `4200`.

---

## Future Improvements
1. Add database support for storing results (optional).
2. Extend analysis models for broader AI-generated content detection.
3. Improve UI/UX for better user experience.

---

## License
This project is licensed under the MIT License. See `LICENSE` for details.

---

## Authors
- **Your Name** (Developer)
