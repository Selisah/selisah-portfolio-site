import importlib
import os
import sys
import unittest
from unittest.mock import patch

from app import app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_app_falls_back_to_sqlite_when_mysql_config_is_missing(self):
        sys.modules.pop("app", None)
        with patch.dict(os.environ, {"MYSQL_DATABASE": "", "MYSQL_USER": "", "MYSQL_PASSWORD": "", "MYSQL_HOST": ""}, clear=False):
            module = importlib.import_module("app")

        self.assertIsNotNone(module.db)
        self.assertEqual(module.db.__class__.__name__, "SqliteDatabase")

    def test_route_smoke_pages_return_200(self):
        routes = ["/", "/about", "/work", "/education", "/hobbies", "/map", "/timeline", "/admin"]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_home_page_includes_core_nav_links(self):
        response = self.client.get("/")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        for route in ["/", "/about", "/work", "/education", "/map", "/timeline", "/admin"]:
            with self.subTest(route=route):
                self.assertIn(f'href="{route}"', body)

    def test_timeline_page_renders_form_and_posts_section(self):
        response = self.client.get("/timeline")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Create a Timeline Post", body)
        self.assertIn('id="timeline-form"', body)
        self.assertIn("Timeline Posts", body)

    def test_timeline_api_create_and_list_posts(self):
        create_response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "content": "Hello from unit test",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        created = create_response.get_json()
        self.assertEqual(created["name"], "Test User")
        self.assertEqual(created["content"], "Hello from unit test")

        list_response = self.client.get("/api/timeline_post")
        self.assertEqual(list_response.status_code, 200)
        posts = list_response.get_json()["timeline_posts"]
        self.assertTrue(any(post["content"] == "Hello from unit test" for post in posts))

        page_response = self.client.get("/timeline")
        self.assertIn("Hello from unit test", page_response.get_data(as_text=True))

    def test_about_page_sets_about_nav_link_active(self):
        response = self.client.get("/about")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("<h1>About</h1>", body)

    def test_work_page_renders_json_role_content(self):
        response = self.client.get("/work")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Work Experiences", body)
        self.assertIn("No work entries available yet.", body)

    def test_education_page_renders_application_fields(self):
        response = self.client.get("/education")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("GPA", body)
        self.assertIn("Classification", body)
        self.assertIn("Extracurriculars", body)
        self.assertIn("Relevant Coursework", body)

    def test_hobbies_page_renders_json_hobby_content(self):
        response = self.client.get("/hobbies")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Hobbies", body)
        self.assertIn("No hobbies listed yet.", body)

    def test_map_page_includes_renderer_script_and_marker_color(self):
        response = self.client.get("/map")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("map-renderer.js", body)
        self.assertIn("unpkg.com/leaflet", body)
        self.assertIn("#66BB6A", body)

    def test_admin_page_renders_plain_text_forms(self):
        response = self.client.get("/admin")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Admin Editor", body)
        self.assertIn('name="current_education"', body)
        self.assertIn('name="locations"', body)
        self.assertNotIn("Save About", body)
        self.assertNotIn("Save Hobbies", body)

    @patch("app._resolve_location_coordinates", return_value=(5.6037, -0.1870))
    @patch("app.save_json_file", return_value=True)
    def test_admin_save_posts_map_form_payload(self, mock_save_json, _mock_resolve_coordinates):
        response = self.client.post(
            "/admin/save/map",
            data={
                "locations": "Accra|Ghana|Home",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin?saved=map", response.headers["Location"])
        mock_save_json.assert_called_once()

    @patch("app.save_json_file", return_value=False)
    def test_admin_save_handles_write_failure(self, _mock_save_json):
        response = self.client.post(
            "/admin/save/map",
            data={},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin?error=map", response.headers["Location"])

    @patch("app.load_json_file", return_value=[])
    def test_map_page_handles_malformed_payload_shape(self, _mock_load_json_file):
        response = self.client.get("/map")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="map-root"', body)
        self.assertIn("map-renderer.js", body)


if __name__ == "__main__":
    unittest.main()
