import io
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from PyPDF2 import PdfReader
from sqlalchemy import text
from werkzeug.utils import secure_filename

from config import debug_status, whitelist_origins
from debug import debug_only

from edutainment.narration import get_narration
from edutainment.text import GPTLessonText
from gpt_utils import test
from video import get_course_videos
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
#from flask_migrate import Migrate
from flask import send_from_directory


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=whitelist_origins)
db = SQLAlchemy(app)
#migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

def sanitize_html(html_input):
    # Remove leading/trailing white space and control characters
    soup = BeautifulSoup(html_input.strip(), "lxml")
    inputs = []

    for input_field in soup.find_all(["input", "textarea"]):
        field_type = input_field.get("type")

        # Check if the input field is of type 'text' or a 'textarea'
        if field_type == "text" or input_field.name == "textarea":
            field_id = input_field.get("id")  # Get the id of the input field
            name = input_field.get("name")
            class_name = input_field.get("class")
            label = input_field.find_previous("label")
            placeholder = input_field.get("placeholder")

            inputs.append(
                {
                    "id": field_id,  # Add the id to the dictionary
                    "name": name,
                    "type": field_type,
                    "class": class_name,
                    "label": str(label),
                    "placeholder": placeholder,
                }
            )

    return inputs


def sanitize_cv(cv_text):
    # Remove leading/trailing white space and control characters
    sanitized_cv = cv_text.strip()
    return sanitized_cv


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(io.BytesIO(pdf_file.read()))

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    return text


# Just for testing connection with backend; debugging purpose only
@app.route("/test", methods=["GET"])
def hello():
    return "Hello!"


@app.route("/generate-course", methods=["POST"])
def generate_course():
    try:
        # Extracting the PDF file
        article = request.files.get("selectedFile")
        if article:
            article_filename = secure_filename(article.filename)

        # Extracting other form data
        user_session_id = request.form.get("sessionId")
        age = request.form.get("age")
        expertise = request.form.get("expertise")
        topic = request.form.get("change_topic")

        logging.info(expertise)

        article_text = extract_text_from_pdf(article)
        article_text = sanitize_cv(article_text)

        lesson_generator = GPTLessonText(article_text)

        # lessons = lesson_generator.get_lessons(topic)
        lessons = ["a lesson"]

        for lesson in lessons:
            # get_narration(lesson["lesson"])
            logging.info(lesson)

        # lessons = get_course_videos(lessons)

        ### Not yet functional below here
        print("here?")
        print(user_session_id)
        print(article_filename)
        print(article_text)
        print(age)
        from edutainment.lesson_planner import LessonPlan
        with app.app_context():
            lesson_plan = LessonPlan(
                session_id=user_session_id,
                article_filename=article_filename,
                article_text=article_text,
                age=int(age),
                debug=True if os.getenv("DEBUG") == "TRUE" else False,
            )

        print("here2")
        topics = lesson_plan.get_topics()
        lessons = {}
        print("here3")
        print(topics)
        for t in topics:
            lessons[t] = lesson_plan.get_lessons(t, expertise)
            print("t")
            print(t)
        print("here5")
        print(lessons)

    except Exception as e:
        print(f"error: {e}")
        logging.error(str(e))
        return jsonify({"error": "Something went wrong"}), 500

    return jsonify(lessons), 200


@app.route('/narration/<path:filename>', methods=['GET'])
def serve_audio(filename):
    # Get the current working directory
    current_directory = os.getcwd()
    
    # Define the directory where audio files are stored relative to the current working directory
    narration_dir = os.path.join(current_directory, 'narration')
    
    # Use send_from_directory to serve the file
    return send_from_directory(narration_dir, filename, as_attachment=True)

if __name__ == "__main__":
    #with app.app_context():
        #db.create_all()
    app.run(debug=debug_status, port=4000)  # toggled for prod
