import os
import re

def search_patterns():
    files = [
        r"C:\TAKPv22\eqlog_Tweedlede_pq.proj.txt",
        r"C:\TAKPv22\eqlog_Thebrain_pq.proj.txt",
        r"C:\TAKPv22\eqlog_Steps_pq.proj.txt"
    ]
    
    # 1. Search for AA messages
    print("=== Searching for AA messages ===")
    aa_re = re.compile(r"(ability point|alternate advancement|gained an ability)", re.I)
    found_aa = False
    for path in files:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if aa_re.search(line):
                    print(f"[{os.path.basename(path)}] {line.strip()}")
                    found_aa = True
                    break
            if found_aa:
                break
    if not found_aa:
        print("No matches for AA standard strings.")

    # 2. Search for Raid kill / Boss messages
    print("\n=== Searching for Raid Kill / Server Announcement messages ===")
    # Common Quarm / TAKP raid / server kill messages:
    # Look for known bosses like Nagafen, Vox, Trakanon, Venril, Gorenaire, Talendor, Severilous, Faydedar, Vindicator, Statue, Cazic, Innoruuk, Aten Ha Ra, Emperor Ssraeshza, Rhag
    bosses = ["trakanon", "nagafen", "vox", "venril sathir", "cazic-thule", "innoruuk", "aten ha ra", "emperor ssraeshza", "derakor the vindicator", "the statue of rallos zek"]
    for path in files:
        matches = 0
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                low = line.lower()
                if any(b in low for b in bosses) and any(kw in low for kw in ["slain", "defeated", "congratulations", "shouts", "falls"]):
                    print(f"[{os.path.basename(path)}] {line.strip()}")
                    matches += 1
                    if matches >= 5:
                        break
        if matches > 0:
            print(f"Found {matches} boss lines in {os.path.basename(path)}")

if __name__ == "__main__":
    search_patterns()
