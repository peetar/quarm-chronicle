import re

SQL_PATH = r"C:\code\eqpetfinder\dump\quarm_2025-11-02-07_55\quarm_2025-11-02-07_55.sql"

def find_npc_types():
    in_npc_types = False
    targets = ["Avatar_of_War", "Vulak`Aerr", "Tunare"]
    found = []
    
    with open(SQL_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "CREATE TABLE `npc_types`" in line or "INSERT INTO `npc_types`" in line:
                in_npc_types = True
            elif in_npc_types and line.startswith("CREATE TABLE"):
                break
            
            if in_npc_types:
                for t in targets:
                    if t.lower() in line.lower():
                        # match (id, 'name', ...)
                        matches = re.findall(r"\((\d+),\s*'([^']+)'", line)
                        for nid, name in matches:
                            if any(t.lower() in name.lower() for t in targets):
                                found.append((nid, name))
                                
    for nid, name in found:
        print(f"ID: {nid:6s} | Name: {name:30s} -> https://www.pqdi.cc/npc/{nid}")

if __name__ == "__main__":
    find_npc_types()
