import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route('/')
def index():
    about_yourself = (
        "I am a production engineering enthusiast who enjoys building reliable web "
        "applications, learning from open-source communities, and creating helpful "
        "tools for everyday users."
    )

    work_experiences = [
        {
            "role": "Production Engineering Fellow",
            "company": "MLH Fellowship",
            "duration": "Summer 2026",
            "description": "Collaborated on open source software with a global cohort.",
        },
        {
            "role": "Software Engineering Intern",
            "company": "Tech Startup",
            "duration": "2025",
            "description": "Built and shipped customer-facing web features in Flask.",
        },
    ]

    education_history = [
        {
            "school": "University of Technology",
            "degree": "BSc in Computer Science",
            "duration": "2022 - Present",
        },
        {
            "school": "City STEM College",
            "degree": "Pre-University Science",
            "duration": "2020 - 2022",
        },
    ]

    hobbies = [
        {
            "name": "Photography",
            "description": "Capturing street and landscape moments.",
        },
        {
            "name": "Traveling",
            "description": "Exploring new cultures and cuisines.",
        },
        {
            "name": "Reading",
            "description": "Enjoying technology and personal growth books.",
        },
    ]

    return render_template(
        'index.html',
        title="MLH Fellow",
        url=os.getenv("URL"),
        about_yourself=about_yourself,
        work_experiences=work_experiences,
        education_history=education_history,
        hobbies=hobbies,
    )
