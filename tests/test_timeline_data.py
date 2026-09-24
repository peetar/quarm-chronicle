import os
import json
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "sample_output", "tweedlede_timeline.json")

class TestTimelineData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assertTrue(os.path.exists(DATA_FILE), f"{DATA_FILE} does not exist")
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_top_level_keys(self):
        self.assertIn("character", self.data)
        self.assertEqual(self.data["character"], "Tweedlede")
        self.assertIn("date_range", self.data)
        self.assertIn("eras", self.data)
        self.assertIn("events", self.data)

    def test_significance_levels_present(self):
        events = self.data["events"]
        self.assertIn("level_1", events)
        self.assertIn("level_2", events)
        self.assertIn("level_3", events)

        # Level 1 has dings, guild joins, epic, and pinnacles
        l1_types = {e["type"] for e in events["level_1"]}
        self.assertIn("level_ding", l1_types)
        self.assertTrue(any("guild" in t for t in l1_types))

        # Check level 1 badges are concise
        for e in events["level_1"]:
            if e["type"] == "level_ding":
                self.assertTrue(e["badge"].isdigit())

    def test_chronological_ordering(self):
        l1 = self.data["events"]["level_1"]
        dates = [e.get("date") for e in l1 if e.get("date")]
        self.assertEqual(dates, sorted(dates))

    def test_html_card_exists(self):
        html_path = os.path.join(PROJECT_ROOT, "src", "cards", "timeline_card.html")
        self.assertTrue(os.path.exists(html_path))
        self.assertGreater(os.path.getsize(html_path), 50000)

    def test_html_features_and_fixes(self):
        html_path = os.path.join(PROJECT_ROOT, "src", "cards", "timeline_card.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1) Draggable Scrubber
        self.assertIn("setupScrubberDrag", content)
        self.assertIn("isDraggingScrubber", content)

        # 2) Regular date ticks on axis (no "Wk of")
        self.assertIn("renderAxisTicks", content)
        self.assertIn("axis-tick", content)
        self.assertIn("axis-tick-label", content)
        self.assertNotIn("Wk of", content)

        # 3) & 5) Death skull icon with tooltip and stem line
        self.assertIn("death-icon-badge", content)
        self.assertIn("death-tooltip", content)
        self.assertIn("death-stem", content)

        # 4) & 6) Staggered distance and vertical lines
        self.assertIn("zone-first-stem", content)
        self.assertIn("zoneStaggerIdx", content)
        self.assertIn("spell-first-stem", content)
        self.assertIn("spellStaggerIdx", content)

        # 7) Modal does not contain Significance Tier or redundant Date
        self.assertNotIn("addRow('Significance Tier'", content)
        self.assertNotIn("addRow('Date'", content)
        self.assertIn("Exact Timestamp", content)

        # 8) Wider bounding box to prevent scrollbar
        self.assertIn("max-width: 1560px", content)

        # 9) Seasonal zoom zooms out to 30 days (monthSpan)
        self.assertIn("monthSpan = 30 * 24 * 60 * 60 * 1000", content)

        # 10) Monthly Boss Summaries with staggered stems and modal breakdown
        self.assertIn("getMonthlyBossSummaries", content)
        self.assertIn("node-monthly-boss", content)
        self.assertIn("monthly-boss-stem", content)
        self.assertIn("monthly-boss-badge", content)
        self.assertIn("modal-kills-list", content)

        # 11) Small non-clickable AA markers on Macro timeline
        self.assertIn("node-aa-gain-macro", content)
        self.assertIn("pointer-events: none !important", content)

if __name__ == "__main__":
    unittest.main()

