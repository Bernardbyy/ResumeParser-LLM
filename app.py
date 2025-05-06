# FLASK APP - Run the app using flask --app app.py run (Creates a simple web server with two routes)
import os, sys
from flask import Flask, request, render_template
from pypdf import PdfReader 
import json
from resumeparser import ats_extractor, job_description_extractor
from matcher import ResumeMatcher

sys.path.insert(0, os.path.abspath(os.getcwd()))


UPLOAD_PATH = r"__DATA__"
app = Flask(__name__)

# Renders the main page
@app.route('/')
def index():
    return render_template('index.html')

# Handles resume uploads, processes them, and returns results
@app.route("/process", methods=["POST"])
def ats():
    doc = request.files['pdf_doc']
    doc.save(os.path.join(UPLOAD_PATH, "file.pdf"))
    doc_path = os.path.join(UPLOAD_PATH, "file.pdf")
    
    # Extract resume data
    resume_text = _read_file_from_path(doc_path)
    resume_data = ats_extractor(resume_text)
    
    # Get job description if provided
    job_description = request.form.get('job_description', '')
    job_data = None
    match_results = None
    
    if job_description.strip():  # If job description is provided
        job_data = job_description_extractor(job_description)
    
    # Process both results
    try:
        parsed_resume = json.loads(resume_data)
        parsed_job = json.loads(job_data) if job_data else None
        
        # Calculate match if both resume and job data exist
        if parsed_resume and parsed_job:
            from matcher import ResumeMatcher
            matcher = ResumeMatcher()
            match_results = matcher.calculate_match(parsed_resume, parsed_job)
        
        return render_template('index.html', 
                             resume_data=parsed_resume,
                             job_data=parsed_job,
                             match_results=match_results)
    except json.JSONDecodeError as e:
        # Handle errors...
        error_message = {
            "error": f"Failed to parse JSON response: {str(e)}",
            "resume_raw": resume_data if 'resume_data' in locals() else None,
            "job_raw": job_data if 'job_data' in locals() else None
        }
        return render_template('index.html', data=error_message)
 
def _read_file_from_path(path):
    reader = PdfReader(path) 
    data = ""

    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no] 
        data += page.extract_text()

    return data 


if __name__ == "__main__":
    app.run(port=8000, debug=True)

