import os
import re
import json
from collections import Counter, defaultdict

LOG_FILE = r"C:\TAKPv22\eqlog_Tweedlede_pq.proj.txt"

# Regexes
TS_PATTERN = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<msg>.*)$")
ZONE_PATTERN = re.compile(r"^You have entered ([^\.]+)\.", re.I)
DING_PATTERN = re.compile(r"^Welcome to level (\d+)!", re.I)
AA_PATTERN = re.compile(r"^You have gained an ability point!\s*You now have (\d+) ability points?\.", re.I)
DEATH_PATTERN = re.compile(r"^(You have been slain by (.*?)|You died)\.?", re.I)
TELL_SENT = re.compile(r"^You told ([A-Za-z]+),\s*'(.*)'", re.I)
TELL_RECV = re.compile(r"^([A-Za-z]+) tells you,\s*'(.*)'", re.I)
CAST_PATTERN = re.compile(r"^You begin (?:casting|singing) (.*?)\.", re.I)
SERVER_KILL = re.compile(r"PVP Druzzil Ro BROADCASTS, '(?P<killer>.*?) of <(?P<guild>.*?)> has killed (?P<boss>.*?) in (?P<zone>.*?)!'", re.I)
LOCAL_SLAY = re.compile(r"^(?P<target>.*?) has been slain by (?P<killer>.*?)!", re.I)

# Known raid bosses
PINNACLE_BOSSES = {
    "Lord Nagafen", "Lady Vox", "Trakanon", "Venril Sathir", "Gorenaire", "Talendor", 
    "Severilous", "Faydedar", "Derakor the Vindicator", "The Statue of Rallos Zek",
    "Lord Yelinak", "King Tormax", "Dain Frostreaver IV", "Cazic-Thule", "Innoruuk",
    "Aten Ha Ra", "Emperor Ssraeshza", "Shei Vinitras", "Burrower Parasite", "Thought Horror Overfiend"
}

def analyze():
    current_zone = "Unknown"
    first_ts = None
    last_ts = None
    
    zone_entries = Counter()
    zone_deaths = Counter()
    zone_aas = Counter()
    
    level_timeline = [] # list of {timestamp, level, zone}
    aa_events = [] # list of {timestamp, total_aa, zone}
    deaths = [] # list of {timestamp, killer, zone}
    
    tells_sent = Counter()
    tells_recv = Counter()
    spells_cast = Counter()
    
    raid_kills_witnessed = [] # {timestamp, boss, killer, zone, type}
    
    print(f"Streaming {LOG_FILE}...")
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = TS_PATTERN.match(line)
            if not m:
                continue
            ts, msg = m.group("ts"), m.group("msg")
            if first_ts is None:
                first_ts = ts
            last_ts = ts
            
            # Fast filter: check msg prefixes or common keywords
            # 1. Zone
            if msg.startswith("You have entered "):
                zm = ZONE_PATTERN.match(msg)
                if zm:
                    current_zone = zm.group(1).strip()
                    zone_entries[current_zone] += 1
                continue

            # 2. Level ding
            if "Welcome to level " in msg:
                dm = DING_PATTERN.match(msg)
                if dm:
                    lvl = int(dm.group(1))
                    level_timeline.append({"timestamp": ts, "level": lvl, "zone": current_zone})
                continue
                
            # 3. AA Point
            if "You have gained an ability point!" in msg:
                am = AA_PATTERN.match(msg)
                if am:
                    total_aa = int(am.group(1))
                    zone_aas[current_zone] += 1
                    aa_events.append({"timestamp": ts, "total_aa": total_aa, "zone": current_zone})
                continue

            # 4. Death
            if msg.startswith("You have been slain by") or msg == "You died.":
                dm = DEATH_PATTERN.match(msg)
                killer = dm.group(2) if dm and dm.group(2) else "Unknown/Gravity"
                zone_deaths[current_zone] += 1
                deaths.append({"timestamp": ts, "killer": killer, "zone": current_zone})
                continue
                
            # 5. Tells
            if msg.startswith("You told "):
                tm = TELL_SENT.match(msg)
                if tm:
                    tells_sent[tm.group(1)] += 1
                continue
            elif " tells you, " in msg:
                tm = TELL_RECV.match(msg)
                if tm:
                    sender = tm.group(1)
                    if not sender.lower().endswith("merchant"):
                        tells_recv[sender] += 1
                continue
                
            # 6. Spells
            if msg.startswith("You begin "):
                cm = CAST_PATTERN.match(msg)
                if cm:
                    spells_cast[cm.group(1)] += 1
                continue

            # 7. Raid Boss Kills
            if "has killed" in msg and "PVP Druzzil Ro BROADCASTS" in msg:
                sk = SERVER_KILL.search(msg)
                if sk:
                    raid_kills_witnessed.append({
                        "timestamp": ts,
                        "boss": sk.group("boss"),
                        "killer": sk.group("killer"),
                        "guild": sk.group("guild"),
                        "zone": sk.group("zone"),
                        "type": "server_broadcast"
                    })
                continue
            elif " has been slain by " in msg:
                sl = LOCAL_SLAY.match(msg)
                if sl:
                    target = sl.group("target").strip()
                    for boss in PINNACLE_BOSSES:
                        if boss.lower() == target.lower():
                            raid_kills_witnessed.append({
                                "timestamp": ts,
                                "boss": boss,
                                "killer": sl.group("killer"),
                                "zone": current_zone,
                                "type": "local_slay"
                            })
                            break

    result = {
        "character": "Tweedlede",
        "class": "Enchanter",
        "date_range": {"first": first_ts, "last": last_ts},
        "stats": {
            "total_deaths": len(deaths),
            "total_level_dings": len(level_timeline),
            "total_aas_earned": len(aa_events),
            "max_level": max((x["level"] for x in level_timeline), default=60),
            "top_zones_by_entries": zone_entries.most_common(10),
            "top_zones_by_deaths": zone_deaths.most_common(10),
            "top_zones_by_aas": zone_aas.most_common(10),
            "top_tell_recipients": tells_sent.most_common(10),
            "top_tell_senders": tells_recv.most_common(10),
            "top_spells_cast": spells_cast.most_common(10),
            "raid_kills_count": len(raid_kills_witnessed)
        },
        "level_timeline": level_timeline,
        "aa_events": aa_events,
        "deaths_sample": deaths[:20],
        "raid_kills": raid_kills_witnessed
    }

    os.makedirs(r"C:\code\quarm-chronicle\data\sample_output", exist_ok=True)
    out_path = r"C:\code\quarm-chronicle\data\sample_output\tweedlede_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Summary saved to {out_path}!")
    
    print("\n=== HIGHLIGHTS ===")
    print(f"Total AAs: {len(aa_events)}")
    print(f"AAs by Zone: {zone_aas.most_common(5)}")
    print(f"Deaths by Zone: {zone_deaths.most_common(5)}")
    print(f"Raid Kills Witnessed: {len(raid_kills_witnessed)}")
    if raid_kills_witnessed:
        print(f"Sample Raid Kills: {raid_kills_witnessed[:5]}")

if __name__ == "__main__":
    analyze()
