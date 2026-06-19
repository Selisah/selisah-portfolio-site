import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json_file(path_or_name, fallback):
    if os.path.isabs(path_or_name):
        file_path = path_or_name
    else:
        file_path = os.path.join(DATA_DIR, path_or_name)

    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return fallback


def load_nav_items():
    fallback_payload = {
        "items": [
            {"label": "Home", "route": "/", "enabled": True},
            {"label": "About", "route": "/about", "enabled": True},
            {"label": "Work", "route": "/work", "enabled": True},
            {"label": "Education", "route": "/education", "enabled": True},
            {"label": "Hobbies", "route": "/hobbies", "enabled": True},
            {"label": "Map", "route": "/map", "enabled": True},
        ]
    }

    payload = load_json_file("site_nav.json", fallback_payload)
    if not isinstance(payload, dict):
        payload = fallback_payload

    nav_items = payload.get("items", [])
    if not isinstance(nav_items, list):
        nav_items = fallback_payload["items"]

    enabled_items = []
    for item in nav_items:
        if not isinstance(item, dict):
            continue
        if not item.get("enabled", True):
            continue

        label = item.get("label")
        route = item.get("route")
        if not label or not route:
            continue

        enabled_items.append(
            {"label": label, "route": route, "enabled": item.get("enabled", True)}
        )

    if enabled_items:
        return enabled_items

    return [item for item in fallback_payload["items"] if item.get("enabled", True)]
