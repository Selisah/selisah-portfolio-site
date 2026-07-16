import unittest
import os

os.environ["TESTING"] = "true"

from app import app, db, TimelinePost


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        db.connect(reuse_if_open=True)
        db.drop_tables([TimelinePost])
        db.create_tables([TimelinePost])

    def tearDown(self):
        db.drop_tables([TimelinePost])

    # ---- Tests for GET /api/timeline_post ----

    def test_get_timeline_post_empty(self):
        """Test GET returns empty list when no posts exist."""
        response = self.client.get("/api/timeline_post")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["timeline_posts"], [])

    def test_get_timeline_post_with_data(self):
        """Test GET returns posts after creating some."""
        TimelinePost.create(name="Test User", email="test@example.com", content="Test post")
        response = self.client.get("/api/timeline_post")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["timeline_posts"]), 1)
        self.assertEqual(response.json["timeline_posts"][0]["name"], "Test User")

    # ---- Tests for POST /api/timeline_post ----

    def test_post_timeline_post(self):
        """Test creating a valid timeline post."""
        response = self.client.post("/api/timeline_post", data={
            "name": "Test User",
            "email": "test@example.com",
            "content": "This is a test post"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Test User")
        self.assertEqual(response.json["email"], "test@example.com")
        self.assertEqual(response.json["content"], "This is a test post")

    def test_post_timeline_post_persists(self):
        """Test that a posted timeline post is saved to the database."""
        self.client.post("/api/timeline_post", data={
            "name": "Persist User",
            "email": "persist@example.com",
            "content": "Checking persistence"
        })
        posts = TimelinePost.select()
        self.assertEqual(posts.count(), 1)
        self.assertEqual(posts[0].name, "Persist User")

    # ---- Tests for the Timeline page ----

    def test_timeline_page(self):
        """Test that the /timeline page loads successfully."""
        response = self.client.get("/timeline")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Timeline", response.data)

    # ---- Edge case / error tests (TDD) ----

    def test_post_timeline_post_missing_name(self):
        """Test POST with missing name returns 400."""
        response = self.client.post("/api/timeline_post", data={
            "email": "test@example.com",
            "content": "Missing name"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid name", response.data)

    def test_post_timeline_post_missing_content(self):
        """Test POST with missing content returns 400."""
        response = self.client.post("/api/timeline_post", data={
            "name": "Test User",
            "email": "test@example.com"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid content", response.data)

    def test_post_timeline_post_invalid_email(self):
        """Test POST with invalid email returns 400."""
        response = self.client.post("/api/timeline_post", data={
            "name": "Test User",
            "email": "not-an-email",
            "content": "Bad email test"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid email", response.data)

    def test_post_timeline_post_missing_email(self):
        """Test POST with missing email returns 400."""
        response = self.client.post("/api/timeline_post", data={
            "name": "Test User",
            "content": "Missing email"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid email", response.data)


if __name__ == "__main__":
    unittest.main()
