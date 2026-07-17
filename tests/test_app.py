import os
import unittest

os.environ["TESTING"] = "true"

from app import app, db, TimelinePost


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        db.connect(reuse_if_open=True)
        db.create_tables([TimelinePost], safe=True)
        TimelinePost.delete().execute()

    def tearDown(self):
        TimelinePost.delete().execute()

    def test_home(self):
        response = self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<title>Portfolio</title>" in html
        assert "Portfolio" in html
        assert "/about" in html
        assert "/work" in html
        assert "/education" in html
        assert "/map" in html
        assert "/timeline" in html

    def test_timeline(self):
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json
        json = response.get_json()
        assert "timeline_posts" in json
        assert len(json["timeline_posts"]) == 0

        post_response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "content": "This is a test post",
            },
        )
        assert post_response.status_code == 200
        assert post_response.json["name"] == "Test User"
        assert post_response.json["email"] == "test@example.com"
        assert post_response.json["content"] == "This is a test post"

        get_response = self.client.get("/api/timeline_post")
        assert get_response.status_code == 200
        json = get_response.get_json()
        assert len(json["timeline_posts"]) == 1
        assert json["timeline_posts"][0]["name"] == "Test User"

        page_response = self.client.get("/timeline")
        assert page_response.status_code == 200
        page_html = page_response.get_data(as_text=True)
        assert "Timeline" in page_html

    def test_malformed_timeline_post(self):
        # Test missing name
        response = self.client.post(
            "/api/timeline_post",
            data={
                "email": "john@example.com",
                "content": "Hello world, I'm John!",
            },
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid name" in html

        # Test empty content
        response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "content": "",
            },
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid content" in html

        # Test invalid email
        response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "not-an-email",
                "content": "Hello world, I'm John!",
            },
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html

        # Test missing email
        response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "content": "Hello world, I'm John!",
            },
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html


if __name__ == "__main__":
    unittest.main()
