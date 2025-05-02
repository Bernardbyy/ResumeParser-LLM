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
    You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
    1. full name
    2. email id
    3. github portfolio
    4. linkedin id
    5. employment details
    6. technical skills
    7. soft skills
    Give the extracted information in json format only
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

    # Clean Up the Response to handle markdown formatting
    data = clean_json_response(data)

    return data #Returns structured JSON data


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