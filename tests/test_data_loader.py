import json
import os
import tempfile
import unittest
from unittest import mock

from app import data_loader


class TestDataLoader(unittest.TestCase):
    def assert_nav_item_contract(self, nav_items):
        self.assertIsInstance(nav_items, list)
        self.assertGreater(len(nav_items), 0)

        for item in nav_items:
            self.assertIn("label", item)
            self.assertIn("route", item)
            self.assertIn("enabled", item)

    def test_load_json_file_returns_fallback_when_missing(self):
        fallback = {"ok": False}
        missing_name = "definitely_missing_file.json"

        self.assertEqual(data_loader.load_json_file(missing_name, fallback), fallback)

    def test_load_json_file_reads_valid_json_from_absolute_path(self):
        fallback = {"ok": False}

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "sample.json")
            payload = {"name": "portfolio", "enabled": True}

            with open(file_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)

            self.assertEqual(data_loader.load_json_file(file_path, fallback), payload)

    def test_load_nav_items_returns_fallback_when_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(data_loader, "DATA_DIR", temp_dir):
                nav_items = data_loader.load_nav_items()

        self.assert_nav_item_contract(nav_items)

    def test_load_nav_items_returns_fallback_when_file_invalid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_file = os.path.join(temp_dir, "site_nav.json")
            with open(invalid_file, "w", encoding="utf-8") as handle:
                handle.write("{invalid json")

            with mock.patch.object(data_loader, "DATA_DIR", temp_dir):
                nav_items = data_loader.load_nav_items()

        self.assert_nav_item_contract(nav_items)

    def test_load_nav_items_returns_only_enabled_items(self):
        payload = {
            "items": [
                {"label": "Home", "route": "/", "enabled": True},
                {"label": "About", "route": "/about"},
                {"label": "Hidden", "route": "/hidden", "enabled": False},
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "site_nav.json")
            with open(file_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)

            with mock.patch.object(data_loader, "DATA_DIR", temp_dir):
                nav_items = data_loader.load_nav_items()

        self.assertEqual(
            nav_items,
            [
                {"label": "Home", "route": "/", "enabled": True},
                {"label": "About", "route": "/about", "enabled": True},
            ],
        )
        self.assert_nav_item_contract(nav_items)


if __name__ == "__main__":
    unittest.main()
