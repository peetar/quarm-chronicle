import sys
import unittest

sys.path.insert(0, r"C:\code\quarm-chronicle")
from src.models.npc_database import NPCDatabase

class TestNPCDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = NPCDatabase()

    def test_pinnacle_bosses(self):
        aow = self.db.resolve("The Avatar of War", "Kael Drakkel")
        self.assertIsNotNone(aow)
        self.assertEqual(aow["id"], 113244)
        self.assertEqual(aow["url"], "https://www.pqdi.cc/npc/113244")

        vulak = self.db.resolve("Vulak`Aerr", "Temple of Veeshan")
        self.assertIsNotNone(vulak)
        self.assertEqual(vulak["id"], 124128)

        nagafen = self.db.resolve("Lord Nagafen", "Nagafen's Lair")
        self.assertIsNotNone(nagafen)
        self.assertEqual(nagafen["id"], 32040)

        phara = self.db.resolve("Phara Dar", "Veeshan's Peak")
        self.assertIsNotNone(phara)
        self.assertEqual(phara["id"], 108510)

        emperor = self.db.resolve("Emperor Ssraeshza", "Ssraeshza Temple")
        self.assertIsNotNone(emperor)
        self.assertEqual(emperor["id"], 162065)
        self.assertEqual(emperor["url"], "https://www.pqdi.cc/npc/162065")

        aten = self.db.resolve("Aten Ha Ra", "Vex Thal")
        self.assertIsNotNone(aten)
        self.assertEqual(aten["id"], 158436)
        self.assertEqual(aten["url"], "https://www.pqdi.cc/npc/158436")

    def test_trash_mobs(self):
        slave = self.db.resolve("escaped slave", "Chardok")
        self.assertIsNotNone(slave)
        self.assertEqual(slave["id"], 103097)

    def test_player_non_match(self):
        rival = self.db.resolve("Xebobn", "an Arena (PvP) area")
        self.assertIsNone(rival)

if __name__ == "__main__":
    unittest.main()
