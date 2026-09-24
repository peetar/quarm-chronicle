import os
import json
from typing import Optional, Dict, Any, List

EQPETFINDER_DATA_PATH = r"C:\code\eqpetfinder\npc-data.json"

# Extra / Scripted bosses that spawn via scripts/events rather than static spawn groups
CUSTOM_BOSS_OVERRIDES = {
    "the avatar of war": {
        "id": 113244,
        "name": "The_Avatar_of_War",
        "level": 70,
        "hp": 250000,
        "zone_short": "kael",
        "zone_long": "Kael Drakkel"
    },
    "avatar of war": {
        "id": 113244,
        "name": "The_Avatar_of_War",
        "level": 70,
        "hp": 250000,
        "zone_short": "kael",
        "zone_long": "Kael Drakkel"
    },
    "vulak`aerr": {
        "id": 124128,
        "name": "#Vulak`Aerr",
        "level": 66,
        "hp": 150000,
        "zone_short": "templeveeshan",
        "zone_long": "Temple of Veeshan"
    },
    "vulak'aerr": {
        "id": 124128,
        "name": "#Vulak`Aerr",
        "level": 66,
        "hp": 150000,
        "zone_short": "templeveeshan",
        "zone_long": "Temple of Veeshan"
    },
    "tunare": {
        "id": 127002,
        "name": "#Tunare",
        "level": 65,
        "hp": 1000000,
        "zone_short": "growthplane",
        "zone_long": "Plane of Growth"
    },
    "emperor ssraeshza": {
        "id": 162065,
        "name": "#Emperor_Ssraeshza",
        "level": 66,
        "hp": 1000000,
        "zone_short": "ssratemple",
        "zone_long": "Ssraeshza Temple"
    },
    "high priest of ssraeshza": {
        "id": 162076,
        "name": "High_Priest_of_Ssraeshza",
        "level": 66,
        "hp": 930000,
        "zone_short": "ssratemple",
        "zone_long": "Ssraeshza Temple"
    }
}

class NPCDatabase:
    """
    In-memory NPC resolver connecting EverQuest log names and zones
    to Project Quarm database IDs and pqdi.cc URLs.
    """
    def __init__(self, data_path: str = EQPETFINDER_DATA_PATH):
        self.data_path = data_path
        self.zone_map: Dict[str, str] = {}
        self.npc_by_name: Dict[str, List[Dict[str, Any]]] = {}
        self._load()

    def _clean(self, name: str) -> str:
        return name.lstrip("#").replace("_", " ").strip().lower().replace("`", "'")

    def _load(self):
        if not os.path.exists(self.data_path):
            print(f"[NPCDatabase] Warning: {self.data_path} not found.")
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for z in data.get("zones", []):
            self.zone_map[z["short_name"]] = z["long_name"]

        for z_short, npcs in data.get("npcsByZone", {}).items():
            z_long = self.zone_map.get(z_short, z_short)
            for npc in npcs:
                cn = self._clean(npc["name"])
                if cn not in self.npc_by_name:
                    self.npc_by_name[cn] = []
                self.npc_by_name[cn].append({
                    "id": npc["id"],
                    "name": npc["name"],
                    "level": npc.get("level"),
                    "hp": npc.get("hp"),
                    "maxdmg": npc.get("maxdmg"),
                    "bodytype": npc.get("bodytype"),
                    "zone_short": z_short,
                    "zone_long": z_long,
                    "url": f"https://www.pqdi.cc/npc/{npc['id']}"
                })

        # Inject overrides
        for cn, override in CUSTOM_BOSS_OVERRIDES.items():
            cn_clean = self._clean(cn)
            override["url"] = f"https://www.pqdi.cc/npc/{override['id']}"
            if cn_clean not in self.npc_by_name:
                self.npc_by_name[cn_clean] = []
            self.npc_by_name[cn_clean].append(override)

    def resolve(self, npc_name: str, current_zone: Optional[str] = None) -> Optional[Dict[str, Any]]:
        cn = self._clean(npc_name)
        
        matches = self.npc_by_name.get(cn, [])
        if not matches:
            # Try removing common prefixes
            for prefix in ["a ", "an ", "the "]:
                if cn.startswith(prefix):
                    trimmed = cn[len(prefix):]
                    matches = self.npc_by_name.get(trimmed, [])
                    if matches:
                        break
                else:
                    prefixed = prefix + cn
                    matches = self.npc_by_name.get(prefixed, [])
                    if matches:
                        break

        if not matches:
            return None

        # If zone is provided, find the closest zone match
        if current_zone:
            cz_low = current_zone.lower()
            for m in matches:
                if cz_low in m["zone_long"].lower() or m["zone_short"].lower() in cz_low or m["zone_long"].lower() in cz_low:
                    return m

        # Fallback to the first match
        return matches[0]

    def get_url(self, npc_name: str, current_zone: Optional[str] = None) -> Optional[str]:
        res = self.resolve(npc_name, current_zone)
        return res["url"] if res else None
