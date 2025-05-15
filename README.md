# Resume Parser with LLM Integration

A Flask-based web application that uses Large Language Models (LLMs) to extract structured information from resumes 👨🏻‍💻.

📖Reference: https://github.com/pik1989/Resume-Parser-OpenAI

🧠💬LLM Model: [DeepSeek-V3-0324 (March 2025)](https://openrouter.ai/deepseek/deepseek-chat-v3-0324:free)

## Features

- PDF resume parsing and text extraction
- Integration with DeepSeek-V3-0324 via OpenRouter API
- JSON-structured data extraction for resume components
- Clean, modern UI for displaying parsed resume information

## Technical Stack

- **Backend**: Python, Flask
- **PDF Processing**: PyPDF
- **LLM Integration**: OpenRouter API (with [DeepSeek-V3-0324 (March 2025)](https://openrouter.ai/deepseek/deepseek-chat-v3-0324:freet) model)
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

## Resume Parser Demo <br>
Resume Parser Landing Page:
![image](https://github.com/user-attachments/assets/13b2e2af-48b8-4406-80a7-c0cc4bb62904)

Upload Resume from Local Drive: 
![image](https://github.com/user-attachments/assets/0c1489e0-c284-46f6-9ef5-d07871b95d4f)

Paste Job Description and Press Process Resume: 
![image](https://github.com/user-attachments/assets/8232e4a9-c3cb-478b-8ff1-caecc9821f3a)


Resume Analysis Section: 
Personal Information and Experience: 
![image](https://github.com/user-attachments/assets/795c580a-3c74-4964-b166-d3128edfb329)

Skills, Education and Additional Information:
![image](https://github.com/user-attachments/assets/d5cc7129-a59b-4324-8a0e-7594eb8ac5ad)

Job Description Analysis:
Job Information, Technical Requirements, Domain Knowledge and Experience Requirements:
![image](https://github.com/user-attachments/assets/56069b5c-c526-4847-bfef-d86f202663bd)

Job Responsibilities:
![image](https://github.com/user-attachments/assets/343dd1f6-bc87-4882-838d-46705732285b)

Job Matching Analysis: 
![image](https://github.com/user-attachments/assets/70db6382-cccc-4316-a9e0-6debe33e78ff)
