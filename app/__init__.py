import os
import json
import urllib.parse
import urllib.request
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from app.data_loader import load_json_file, load_nav_items, save_json_file
from datetime import datetime
from peewee import *
from playhouse.shortcuts import model_to_dict


load_dotenv()
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "portfolio.sqlite3")


def _create_database():
    if os.getenv("TESTING") == "true":
        return SqliteDatabase(":memory:")

    database_name = os.getenv("MYSQL_DATABASE") or ""
    database_user = os.getenv("MYSQL_USER") or ""
    database_password = os.getenv("MYSQL_PASSWORD") or ""
    database_host = os.getenv("MYSQL_HOST") or ""

    if all([database_name, database_user, database_password, database_host]):
        try:
            mysql_db = MySQLDatabase(
                database_name,
                user=database_user,
                password=database_password,
                host=database_host,
                port=3306,
            )
            mysql_db.connect(reuse_if_open=True)
            mysql_db.close()
            return mysql_db
        except Exception:
            pass

    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    return SqliteDatabase(DATABASE_PATH)


db = _create_database()
mydb = db

print(mydb)

class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db


db.connect(reuse_if_open=True)
db.create_tables([TimelinePost], safe=True)


SECTION_FILE_MAP = {
    "education": "education.json",
    "map": "map_locations.json",
}


def _split_lines(raw_text):
    if not raw_text:
        return []
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def _parse_positions_lines(raw_text):
    positions = []
    for line in _split_lines(raw_text):
        parts = [part.strip() for part in line.split(";")]
        if len(parts) < 3:
            continue
        positions.append(
            {
                "title": parts[0],
                "organization": parts[1],
                "details": parts[2],
            }
        )
    return positions


def _parse_education_lines(raw_text):
    entries = []
    for line in _split_lines(raw_text):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 7:
            continue
        coursework = []
        extracurriculars = []
        highlights = []
        if len(parts) > 7 and parts[7]:
            coursework = [item.strip() for item in parts[7].split(";") if item.strip()]
        if len(parts) > 8 and parts[8]:
            extracurriculars = [item.strip() for item in parts[8].split(";") if item.strip()]
        if len(parts) > 9 and parts[9]:
            highlights = [item.strip() for item in parts[9].split(";") if item.strip()]

        entries.append(
            {
                "school_name": parts[0],
                "program": parts[1],
                "location": parts[2],
                "start_date": parts[3],
                "grad_date": parts[4],
                "gpa": parts[5],
                "classification": parts[6],
                "coursework": coursework,
                "extracurriculars": extracurriculars,
                "highlights": highlights,
            }
        )
    return entries


def _parse_map_locations(raw_text):
    locations = []
    for line in _split_lines(raw_text):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 1:
            continue
        name = parts[0]
        country = parts[1] if len(parts) > 1 else ""
        note = parts[2] if len(parts) > 2 else ""
        if not name:
            continue
        lat_lng = _resolve_location_coordinates(name=name, country=country)
        if lat_lng is None:
            continue
        lat, lng = lat_lng
        generated_id = f"{name}-{country}".strip("-").lower().replace(" ", "-")
        locations.append(
            {
                "id": generated_id,
                "name": name,
                "country": country,
                "lat": lat,
                "lng": lng,
                "label": name,
                "note": note,
            }
        )
    return locations


def _build_profile_summary(current_education):
    if not current_education:
        return "Education"
    first = current_education[0]
    school = (first.get("school_name") or "").strip()
    program = (first.get("program") or "").strip()
    location = (first.get("location") or "").strip()
    summary_parts = [part for part in [school, program, location] if part]
    if summary_parts:
        return " - ".join(summary_parts)
    return "Education"


def _resolve_location_coordinates(name, country):
    query = f"{name}, {country}".strip(", ")
    url = (
        "https://nominatim.openstreetmap.org/search?"
        + urllib.parse.urlencode(
            {
                "format": "jsonv2",
                "limit": 1,
                "q": query,
            }
        )
    )
    request_obj = urllib.request.Request(
        url,
        headers={"User-Agent": "selisah-portfolio-site/1.0"},
    )
    try:
        with urllib.request.urlopen(request_obj, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None

    if not isinstance(payload, list) or not payload:
        return None

    first = payload[0]
    try:
        lat = float(first.get("lat"))
        lng = float(first.get("lon"))
    except (TypeError, ValueError):
        return None
    return lat, lng


@app.context_processor
def inject_nav_items():
    return {"nav_items": load_nav_items()}


@app.route('/')
def index():
    return render_template(
        'index.html',
        title="Portfolio",
        url=os.getenv("URL"),
    )


@app.route('/about')
def about():
    payload = load_json_file("about.json", fallback={})
    return render_template('about.html', title="About", about=payload)


@app.route('/work')
def work():
    payload = load_json_file("work.json", fallback={})
    return render_template('work.html', title="Work", work=payload)


@app.route('/education')
def education():
    payload = load_json_file("education.json", fallback={})
    return render_template('education.html', title="Education", education=payload)


@app.route('/hobbies')
def hobbies():
    payload = load_json_file("hobbies.json", fallback={})
    return render_template('hobbies.html', title="Hobbies", hobbies=payload)


@app.route('/map')
def map_page():
    fallback_payload = {
        "map_style": {
            "outline_color": "#66BB6A",
            "background_color": "#FFFFFF",
            "marker_color": "#E02424",
            "connector_style": "dotted",
        },
        "locations": [],
        "connections": [],
    }

    payload = load_json_file(
        "map_locations.json",
        fallback=fallback_payload,
    )
    if not isinstance(payload, dict):
        payload = dict(fallback_payload)

    map_style = payload.get("map_style")
    if not isinstance(map_style, dict):
        map_style = {}

    payload["map_style"] = {
        "outline_color": map_style.get("outline_color") or "#66BB6A",
        "background_color": map_style.get("background_color") or "#FFFFFF",
        "marker_color": map_style.get("marker_color") or "#E02424",
        "connector_style": map_style.get("connector_style") or "dotted",
    }

    locations = payload.get("locations")
    payload["locations"] = locations if isinstance(locations, list) else []

    connections = payload.get("connections")
    payload["connections"] = connections if isinstance(connections, list) else []

    return render_template('map.html', title="Map", map_payload=payload)


@app.route('/admin')
def admin():
    education_data = load_json_file("education.json", fallback={})
    map_data = load_json_file("map_locations.json", fallback={})
    if not isinstance(education_data, dict):
        education_data = {}
    if not isinstance(map_data, dict):
        map_data = {}

    return render_template(
        "admin.html",
        title="Admin Editor",
        education_data=education_data,
        map_data=map_data,
        saved=request.args.get("saved", ""),
        error=request.args.get("error", ""),
    )


@app.route('/admin/save/<section>', methods=["POST"])
def admin_save(section):
    filename = SECTION_FILE_MAP.get(section)
    if not filename:
        return redirect(url_for("admin", error="unknown_section"))

    parsed_payload = {}
    if section == "education":
        current_education = _parse_education_lines(request.form.get("current_education", ""))
        past_education = _parse_education_lines(request.form.get("past_education", ""))
        parsed_payload = {
            "profile_summary": _build_profile_summary(current_education),
            "current_education": current_education,
            "past_education": past_education,
            "campus_positions": _parse_positions_lines(request.form.get("campus_positions", "")),
            "jobs": _parse_positions_lines(request.form.get("jobs", "")),
        }
    elif section == "map":
        parsed_payload = {
            "map_style": {
                "outline_color": "#66BB6A",
                "background_color": "#FFFFFF",
                "marker_color": "#E02424",
                "connector_style": "dotted",
            },
            "locations": _parse_map_locations(request.form.get("locations", "")),
            "connections": [],
        }

    if not save_json_file(filename, parsed_payload):
        return redirect(url_for("admin", error=section))

    return redirect(url_for("admin", saved=section))


@app.route('/timeline')
def timeline():
    timeline_posts = [
        model_to_dict(p)
        for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
    ]
    return render_template(
        'timeline.html',
        title="Timeline",
        timeline_posts=timeline_posts,
    )


@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    import re
    from flask import jsonify
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    content = request.form.get('content', '')

    if not name or name.strip() == '':
        return jsonify({"error": "Invalid name"}), 400
    if not email or not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return jsonify({"error": "Invalid email"}), 400
    if not content or content.strip() == '':
        return jsonify({"error": "Invalid content"}), 400

    timeline_post = TimelinePost.create(name=name, email=email, content=content)

    return model_to_dict(timeline_post)


@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
    return {
        'timeline_posts': [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }
