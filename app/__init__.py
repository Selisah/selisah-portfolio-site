import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

TEAM_MEMBERS = [
    {
        "name": "Jessica Nguyen",
        "image": "jessica-picture.jpg",
        "url": "/jessica",
        "available": True,
    },
    {
        "name": "Elizabeth Mensah",
        "image": "placeholder-fellow.svg",
        "url": None,
        "available": False,
    },
    {
        "name": "Ngaatendwe Wish Dumbarimwe",
        "image": "placeholder-fellow.svg",
        "url": None,
        "available": False,
    },
]

JESSICA = {
    "name": "Jessica Nguyen",
    "title": "MLH Fellow",
    "avatar": "jessica-picture.jpg",
    "about": (
        "Hi! My name is Jessica and I'm a recent CS graduate from the "
        "University of Houston. I'm passionate about solving real-world "
        "problems, while inspiring others to pursue their passions in STEM."
    ),
    "links": [
        {
            "label": "LinkedIn",
            "url": "https://www.linkedin.com/in/jessicaknguyen04/",
            "platform": "linkedin",
            "hint": "View my profile",
        },
        {
            "label": "GitHub",
            "url": "https://github.com/jessicangu",
            "platform": "github",
            "hint": "See my projects",
        },
    ],
}

PORTFOLIO_SECTIONS = [
    {"id": "about", "title": "About Me"},
    {"id": "photos", "title": "Photos"},
    {"id": "experience", "title": "Experience"},
    {"id": "education", "title": "Education"},
    {"id": "hobbies", "title": "Hobbies"},
]


@app.route("/")
def home():
    return render_template(
        "home.html",
        title="Our Pod Portfolio",
        url=os.getenv("URL"),
        team_members=TEAM_MEMBERS,
        fellows=TEAM_MEMBERS,
    )


@app.route("/jessica")
def jessica():
    return render_template(
        "jessica.html",
        title=JESSICA["name"],
        url=os.getenv("URL"),
        profile=JESSICA,
        sections=PORTFOLIO_SECTIONS,
        fellows=TEAM_MEMBERS,
    )
