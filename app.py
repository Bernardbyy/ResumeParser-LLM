# FLASK APP - Run the app using flask --app app.py run (Creates a simple web server with two routes)
import os, sys
from flask import Flask, request, render_template
from pypdf import PdfReader 
import json
from resumeparser import ats_extractor

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
    data = _read_file_from_path(doc_path)
    data = ats_extractor(data)

    # Add more robust error handling
    try:
        parsed_data = json.loads(data)
        return render_template('index.html', data=parsed_data)
    except json.JSONDecodeError as e:
        # Try to parse the error message to find the problematic part
        error_message = {
            "error": f"Failed to parse JSON response from the model: {str(e)}",
            "raw_response": data,
            "debug_info": {
                "error_position": e.pos if hasattr(e, 'pos') else None,
                "error_line": e.lineno if hasattr(e, 'lineno') else None,
                "error_column": e.colno if hasattr(e, 'colno') else None
            }
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

