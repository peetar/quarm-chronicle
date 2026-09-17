import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"C:\code\eqpetfinder\npc-data.json"

def test():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    zone_map = {z["short_name"]: z["long_name"] for z in db.get("zones", [])}

    def clean_name(n):
        return n.lstrip("#").replace("_", " ").strip().lower()

    npc_index = {}
    for z_short, npcs in db.get("npcsByZone", {}).items():
        z_long = zone_map.get(z_short, z_short)
        for npc in npcs:
            cn = clean_name(npc["name"])
            if cn not in npc_index:
                npc_index[cn] = []
            npc_index[cn].append({
                "id": npc["id"],
                "raw_name": npc["name"],
                "level": npc["level"],
                "hp": npc["hp"],
                "maxdmg": npc["maxdmg"],
                "zone_short": z_short,
                "zone_long": z_long
            })

    print(f"Unique clean NPC names indexed: {len(npc_index):,}")

    test_queries = [
        ("escaped slave", "Chardok"),
        ("goblin guard", "Steamfont Mountains"),
        ("shackled champion", "Chardok"),
        ("Lord Nagafen", "Nagafen's Lair"),
        ("Lady Vox", "Permafrost Keep"),
        ("Phara Dar", "Veeshan's Peak"),
        ("Trakanon", "Ruins of Sebilis"),
        ("Venril Sathir", "Karnor's Castle"),
        ("Vulak`Aerr", "Temple of Veeshan"),
        ("The Avatar of War", "Kael Drakkel"),
        ("Aten Ha Ra", "Vex Thal"),
        ("Xebobn", "an Arena (PvP) area")
    ]

    print("\n=== TESTING LOOKUPS & PQDI LINKS ===")
    for name, zone in test_queries:
        cn = clean_name(name)
        # Handle backticks and apostrophes
        cn_clean = cn.replace("`", "'")
        matches = npc_index.get(cn, []) or npc_index.get(cn.replace("`", "'"), []) or npc_index.get(cn.replace("'", "`"), [])
        
        # Strip common articles: 'a ', 'an ', 'the '
        if not matches:
            for prefix in ["a ", "an ", "the "]:
                matches = npc_index.get(prefix + cn, []) or npc_index.get(prefix + cn_clean, [])
                if matches:
                    break

        zone_match = [m for m in matches if zone.lower() in m["zone_long"].lower() or m["zone_short"].lower() in zone.lower()]
        target = zone_match[0] if zone_match else (matches[0] if matches else None)
    print("\n=== SEARCHING FOR VULAK / AVATAR / TUNARE ===")
    for z_short, npcs in db.get("npcsByZone", {}).items():
        for npc in npcs:
            low = npc["name"].lower()
            if any(k in low for k in ["vulak", "avatar", "war", "tunare"]):
                if any(k in low for k in ["vulak", "avatar", "tunare", "the_avatar"]):
                    print(f"[{z_short}] ID: {npc['id']}, Name: {npc['name']}, Lvl: {npc['level']}")

if __name__ == "__main__":
    test()
