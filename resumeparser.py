# Uses OpenAI's API (specifically GPT-3.5-turbo) to extract information
# import libraries

import requests
import json
from openai import OpenAI
import yaml

api_key = None
CONFIG_PATH = r"config.yaml"

with open(CONFIG_PATH) as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
    api_key = data['OPENROUTER_API_KEY']

def ats_extractor(resume_data):

    prompt = '''
    You are a resume parsing assistant. Extract information from the resume and format it according to this EXACT JSON structure:

    Required JSON structure (PAY ATTENTION TO PLURAL FORMS):
    {
        "personal_info": {
            "full_name": "string",
            "email": "string", 
            "github": "string or null",
            "linkedin": "string or null"
        },
        "experience": {
            "total_years": number,
            "positions": [  # NOTE: "positions" is PLURAL
                {
                    "title": "string",
                    "company": "string", 
                    "duration": "string",
                    "start_date": "string",
                    "end_date": "string or 'Present'",
                    "responsibilities": ["string array"]  # NOTE: "responsibilities" is PLURAL
                }
            ]
        },
        "skills": {  # NOTE: "skills" is PLURAL
            "technical": {
                "languages": ["string array"],  # NOTE: PLURAL
                "frameworks": ["string array"],  # NOTE: PLURAL
                "tools": ["string array"],  # NOTE: PLURAL
                "databases": ["string array"],  # NOTE: PLURAL
                "cloud": ["string array"]
            },
            "soft": ["string array"],
            "domain": ["string array"]
        },
        "education": [
            {
                "degree": "string",
                "field": "string",
                "institution": "string",
                "year": "string"
            }
        ],
        "certifications": ["string array"],  # NOTE: PLURAL
        "miscellaneous": ["string array"]
    }


    Rules:
    1. Return ONLY valid JSON - no markdown, no explanations
    2. Include ALL fields even if empty (use null, [], or "")
    3. Calculate total_years from the experience dates
    4. Extract domain knowledge from job descriptions and skills
    5. Categorize all technical skills into the appropriate subcategories
    6. The "miscellaneous" field should include any relevant information that doesn't fit other categories, such as:
    - Additional languages spoken (e.g., "Speaks Japanese and Korean")
    - Volunteer work
    - Publications
    - Awards and honors
    - Hobbies related to career
    - Security clearances
    - Professional memberships
    - Other unique qualifications

    Parse the resume below and return the structured JSON:
    '''

    # Initialize OpenAI client with OpenRouter endpoint
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key = api_key,
    )    

    # Create Completion
    completion = client.chat.completions.create(
        extra_headers={
            "X-Title": "Resume Parser App with LLM",
        },
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": resume_data}
        ],
        temperature=0.1,
        max_tokens=1500
    )

    # Extract response content
    data = completion.choices[0].message.content

    # DEBUG: Print raw response to console
    print("=" * 50)
    print("RAW MODEL RESPONSE:")
    print(data)
    print("=" * 50)

    # Clean Up the Response to handle markdown formatting
    data = clean_json_response(data)

    return data #Returns structured JSON data

def job_description_extractor(job_description_text):
    prompt = '''
    You are a job description parsing assistant. Extract information from the job description and format it according to this EXACT JSON structure:

    Required JSON structure:
    {
        "job_info": {
            "title": "string",
            "company": "string or null",
            "location": "string or null",
            "type": "string or null"
        },
        "technical_skills": {
            "required": ["string array"],
            "languages": ["string array"],
            "frameworks": ["string array"],
            "tools": ["string array"],
            "databases": ["string array"],
            "cloud": ["string array"]
        },
        "domain_knowledge": {
            "required": ["string array"]
        },
        "experience_requirements": {
            "minimum_years": number or null,
            "required_education": ["string array"],
            "specific_experience": ["string array"]
        },
        "soft_skills": {
            "required": ["string array"]
        },
        "job_responsibilities": {
            "primary": ["string array"],
            "secondary": ["string array"]
        }
    }

    Rules:
    1. Return ONLY valid JSON - no markdown, no explanations
    2. Include ALL fields even if empty (use null, [], or "")
    3. Only extract required skills and requirements, ignore preferred/nice-to-have items
    4. Extract specific technical skills and categorize them appropriately
    5. Identify domain-specific knowledge requirements
    6. Parse experience requirements including years and specific types
    7. Extract required soft skills only
    8. Separate primary/core responsibilities from secondary ones
    9. If information is not explicitly stated, use null or empty array

    Parse the job description below and return the structured JSON:
    '''

    # Initialize OpenAI client with OpenRouter endpoint
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key = api_key,
    )    

    # Create Completion
    completion = client.chat.completions.create(
        extra_headers={
            "X-Title": "Job Description Parser with LLM",
        },
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": job_description_text}
        ],
        temperature=0.1,
        max_tokens=1500
    )

    # Extract response content
    data = completion.choices[0].message.content

    # DEBUG: Print raw response to console
    print("=" * 50)
    print("JOB DESCRIPTION RAW RESPONSE:")
    print(data)
    print("=" * 50)

    # Clean Up the Response to handle markdown formatting
    data = clean_json_response(data)

    return data

def clean_json_response(response):
    """Cleans up the response to ensure valid JSON."""
    """Example:
                    ```json
                    {
                    "response": "This is a raw JSON response as you requested.",
                    "status": "success",
                    "timestamp": "2023-11-15T12:00:00Z"
                    }
                    ``` 
    """
    # Remove markdown code block formatting if present
    if response.startswith('```'):
        # Find the end of the first line
        first_line_end = response.find('\n')
        if first_line_end != -1:
            # Extract the rest, removing the first line
            response = response[first_line_end+1:]
    
    # Remove trailing markdown markers
    if response.endswith('```'):
        response = response[:-3]
    
    # Trim whitespace
    response = response.strip()
    
    # Validate JSON
    try:
        json.loads(response)
        return response
    except json.JSONDecodeError:
        # If still invalid, try to extract JSON from within the text
        import re
        json_pattern = r'({[\s\S]*})'
        matches = re.search(json_pattern, response)
        if matches:
            potential_json = matches.group(1)
            try:
                json.loads(potential_json)
                return potential_json
            except:
                pass
        
        return response