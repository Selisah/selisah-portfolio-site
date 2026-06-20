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
    "photos": [
        {
            "title": "Favorite moment",
            "caption": "Photobooths are my favorite...",
            "image": "photo-1.jpg",
        },
        {
            "title": "Hiking in Colorado",
            "caption": "Saint Mary's Glacier Trail",
            "image": "photo-2.jpg",
        },
        {
            "title": "Halloweekend",
            "caption": "Clark Kent in Austin!",
            "image": "photo-3.jpg",
        },
    ],
    "experience": [
        {
            "position": "Production Engineer Fellow",
            "company": "Major League Hacking x Meta",
            "duration": "June 2026 - Present",
            "description": "learning fundamental site reliability engineering skills and how to build/maintain large-scale systems in production",
        },
        {
            "position": "Computer Vision Research Intern",
            "company": "University of North Texas",
            "duration": "January 2026 - May 2026",
            "description": "computer vision–based road debris detection",
        },
        {
            "position": "Student Director",
            "company": "UH NSM Career Center",
            "duration": "September 2025 - May 2026",
            "description": "connecting students with industry leaders through career fairs and events that support career development and employer engagement",
        },
        {
            "position": "Coding Instructor",
            "company": "Code Ninjas",
            "duration": "Dec 2024 - May 2026",
            "description": "teaching kids how to code through game development, robotics, and other cool projects!",
        },
        {
            "position": "Machine Learning Research Intern",
            "company": "California State University, Dominguez Hills",
            "duration": "January 2025 - June 2025",
            "description": "Project: Towards Inclusive Healthcare: Leveraging Low-Resource Translation for Multilingual Communication",
        },
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "school": "University of Houston",
            "graduation": "May 2026",
            "details": "Minor in Mathematics, CougarCS, CSGirls, Student Director",
        },
    ],
    "hobbies": [
        {
            "hobby": "Music and concerts",
            "description": "Listening to new music and going to concerts.",
            "images": ["music-picture.JPG"],
        },
        {
            "hobby": "Computer projects",
            "description": "Anything involving my computer, whether it's coding, gaming, video editing! I built my own PC last May!",
            "images": ["pc-1.JPG", "pc-2.jpg"],
        },
        {
            "hobby": "Food adventures",
            "description": "Cooking, baking, trying new restaurants.",
            "images": ["food-1.JPG", "food-2.JPG", "food-3.JPG"],
        },
    ],
    "visited_regions": [
        {
            "region": "Pacific Northwest",
            "places": "Vancouver and Seattle",
            "x": 17.0,
            "y": 22.5,
            "size": 4.8,
        },
        {
            "region": "California and Southern California",
            "places": "San Francisco and LA / OC",
            "x": 17.0,
            "y": 31.0,
            "size": 5.2,
        },
        {
            "region": "Southwest",
            "places": "Las Vegas and Phoenix",
            "x": 19.0,
            "y": 32.5,
            "size": 5.0,
        },
        {
            "region": "Rocky Mountains",
            "places": "Denver and Cheyenne",
            "x": 22.2,
            "y": 29.0,
            "size": 4.8,
        },
        {
            "region": "Texas",
            "places": "Austin and Houston",
            "x": 24.4,
            "y": 37.2,
            "size": 5.0,
        },
        {
            "region": "Florida",
            "places": "Miami and Orlando",
            "x": 29.2,
            "y": 37.4,
            "size": 4.2,
        },
        {
            "region": "Yucatan Peninsula",
            "places": "Cancun",
            "x": 25.0,
            "y": 42.2,
            "size": 4.2,
        },
        {
            "region": "Vietnam",
            "places": "Vietnam",
            "x": 78.5,
            "y": 42.8,
            "size": 4.5,
        },
    ],
    "visited_cities": [
        {"city": "Vancouver", "x": 17.5, "y": 25.3},
        {"city": "Seattle", "x": 17.4, "y": 27.1},
        {"city": "San Francisco", "x": 17.6, "y": 33.2},
        {"city": "LA / OC", "x": 18.2, "y": 36.0},
        {"city": "Las Vegas", "x": 19.0, "y": 34.3},
        {"city": "Phoenix", "x": 19.8, "y": 36.4},
        {"city": "Cheyenne", "x": 22.4, "y": 31.5},
        {"city": "Denver", "x": 22.5, "y": 32.8},
        {"city": "Austin", "x": 25.4, "y": 38.8},
        {"city": "Houston", "x": 26.1, "y": 39.3},
        {"city": "Miami / Orlando", "x": 30.4, "y": 39.4},
        {"city": "Cancun", "x": 24.8, "y": 44.7},
        {"city": "Vietnam", "x": 79.3, "y": 45.5},
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


@app.route("/jessica/hobbies")
def jessica_hobbies():
    return render_template(
        "hobbies.html",
        title=f"{JESSICA['name']} | Hobbies",
        url=os.getenv("URL"),
        profile=JESSICA,
        fellows=TEAM_MEMBERS,
    )
