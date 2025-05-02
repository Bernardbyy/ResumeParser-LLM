# Resume Parser with LLM Integration

A Flask-based web application that uses Large Language Models (LLMs) to extract structured information from resumes 👨🏻‍💻.

📖Reference: https://github.com/pik1989/Resume-Parser-OpenAI

🧠💬LLM Model: [DeepSeek-V3-0324 (March 2025)](https://openrouter.ai/models/deepseek-chat)

## Features

- PDF resume parsing and text extraction
- Integration with DeepSeek-V3-0324 via OpenRouter API
- JSON-structured data extraction for resume components
- Clean, modern UI for displaying parsed resume information

## Technical Stack

- **Backend**: Python, Flask
- **PDF Processing**: PyPDF
- **LLM Integration**: OpenRouter API (with [DeepSeek-V3-0324 (March 2025)](https://openrouter.ai/models/deepseek-chat) model)
- **Frontend**: HTML, Tailwind CSS, JavaScript

## Setup Instructions

1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Create a `config.yaml` file with your OpenRouter API key:
   ```yaml
   OPENROUTER_API_KEY: "your_api_key_here"
   ```
4. Ensure a directory named __DATA__ exists in the project root
5. Run the app: python app.py
6. Access the interface at http://localhost:8000
