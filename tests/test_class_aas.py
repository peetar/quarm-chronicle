import unittest
import os
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASS_AAS_PATH = os.path.join(PROJECT_ROOT, "src", "data", "class_aas.json")

class TestClassAAs(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(CLASS_AAS_PATH), f"class_aas.json not found at {CLASS_AAS_PATH}")
        with open(CLASS_AAS_PATH, "r", encoding="utf-8") as f:
            self.class_aas = json.load(f)

    def test_database_not_empty(self):
        self.assertGreater(len(self.class_aas), 100)

    def test_core_class_aas_present(self):
        # Necromancer Lifeburn
        self.assertIn("lifeburn", self.class_aas)
        self.assertEqual(self.class_aas["lifeburn"]["category"], "Class AA")
        self.assertEqual(self.class_aas["lifeburn"]["ranks"], 1)

        # Bard Instrument Mastery
        self.assertIn("instrument mastery", self.class_aas)
        self.assertEqual(self.class_aas["instrument mastery"]["category"], "Class AA")
        self.assertEqual(self.class_aas["instrument mastery"]["ranks"], 3)

        # Enchanter Dire Charm
        self.assertIn("dire charm", self.class_aas)

        # Cleric Bestow Divine Aura
        self.assertIn("bestow divine aura", self.class_aas)

    def test_pop_ability_aas_filtered_correctly(self):
        # Hastened Exodus (WIZ DRU - classes <= 3) should be included
        self.assertIn("hastened exodus", self.class_aas)
        self.assertEqual(self.class_aas["hastened exodus"]["category"], "PoP Ability AA")

        # Fading Memories (BRD) should be included
        self.assertIn("fading memories", self.class_aas)

        # Headshot (RNG) should be included
        self.assertIn("headshot", self.class_aas)

        # General/Archetype and broad melee abilities should NOT be in the database
        self.assertNotIn("innate run speed", self.class_aas)
        self.assertNotIn("combat agility", self.class_aas)
        self.assertNotIn("advanced healing gift", self.class_aas)
        self.assertNotIn("ingenuity", self.class_aas)
        self.assertNotIn("fury of the ages", self.class_aas)

    def test_log_regex_parsing(self):
        p1 = re.compile(r'^You have gained the ability \"(?P<name>[^\"]+)\" at a cost of (?P<cost>\d+) ability points?\.', re.I)
        p2 = re.compile(r'^You have improved (?P<name>.+?)(?:\s+(?P<rank>\d+))? at a cost of (?P<cost>\d+) ability points?\.', re.I)

        # Lifeburn rank 1
        m1 = p1.match('You have gained the ability "Lifeburn" at a cost of 9 ability points.')
        self.assertIsNotNone(m1)
        self.assertEqual(m1.group("name"), "Lifeburn")
        self.assertEqual(m1.group("cost"), "9")

        # Instrument Mastery rank 1
        m2 = p1.match('You have gained the ability "Instrument Mastery" at a cost of 3 ability points.')
        self.assertIsNotNone(m2)
        self.assertEqual(m2.group("name"), "Instrument Mastery")
        self.assertEqual(m2.group("cost"), "3")

        # Instrument Mastery rank 2
        m3 = p2.match('You have improved Instrument Mastery 2 at a cost of 6 ability points.')
        self.assertIsNotNone(m3)
        self.assertEqual(m3.group("name"), "Instrument Mastery")
        self.assertEqual(m3.group("rank"), "2")
        self.assertEqual(m3.group("cost"), "6")

        # Instrument Mastery rank 3
        m4 = p2.match('You have improved Instrument Mastery 3 at a cost of 9 ability points.')
        self.assertIsNotNone(m4)
        self.assertEqual(m4.group("name"), "Instrument Mastery")
        self.assertEqual(m4.group("rank"), "3")
        self.assertEqual(m4.group("cost"), "9")

if __name__ == "__main__":
    unittest.main()
