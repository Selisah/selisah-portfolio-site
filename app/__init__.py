import os
from flask import Flask, render_template
from dotenv import load_dotenv
from app.data_loader import load_json_file, load_nav_items

load_dotenv()
app = Flask(__name__)


@app.context_processor
def inject_nav_items():
    return {"nav_items": load_nav_items()}


@app.route('/')
def index():
    about_payload = load_json_file("about.json", fallback={})
    work_payload = load_json_file("work.json", fallback={})
    education_payload = load_json_file("education.json", fallback={})
    hobbies_payload = load_json_file("hobbies.json", fallback={})

    fallback_map_payload = {
        "map_style": {
            "outline_color": "#66BB6A",
            "background_color": "#FFFFFF",
            "marker_color": "#E02424",
            "connector_style": "dotted",
        },
        "locations": [],
        "connections": [],
    }
    map_payload = load_json_file("map_locations.json", fallback=fallback_map_payload)
    if not isinstance(map_payload, dict):
        map_payload = dict(fallback_map_payload)

    return render_template(
        'index.html',
        title="Portfolio",
        url=os.getenv("URL"),
        about=about_payload,
        work=work_payload,
        education=education_payload,
        hobbies=hobbies_payload,
        map_payload=map_payload,
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
