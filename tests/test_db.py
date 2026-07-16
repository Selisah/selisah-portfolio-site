import unittest
import os

os.environ["TESTING"] = "true"

from peewee import SqliteDatabase
from app import TimelinePost

MODELS = [TimelinePost]
test_db = SqliteDatabase(":memory:")


class TestTimelinePost(unittest.TestCase):
    def setUp(self):
        test_db.bind(MODELS)
        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()

    def test_timeline_post(self):
        """Test that we can create and retrieve a timeline post."""
        first_post = TimelinePost.create(
            name="John Doe",
            email="john@example.com",
            content="Hello world, I'm John!"
        )
        assert first_post.id == 1

        second_post = TimelinePost.create(
            name="Jane Doe",
            email="jane@example.com",
            content="Hello world, I'm Jane!"
        )
        assert second_post.id == 2

        # Get all timeline posts and check they are in descending order
        posts = TimelinePost.select().order_by(TimelinePost.created_at.desc())
        assert posts.count() == 2

        # Check the posts have the correct data
        posts_list = list(posts)
        assert posts_list[0].name == "Jane Doe"
        assert posts_list[0].email == "jane@example.com"
        assert posts_list[0].content == "Hello world, I'm Jane!"

        assert posts_list[1].name == "John Doe"
        assert posts_list[1].email == "john@example.com"
        assert posts_list[1].content == "Hello world, I'm John!"


if __name__ == "__main__":
    unittest.main()
