import os
import re
import json
from collections import Counter, defaultdict

LOG_FILE = r"C:\TAKPv22\eqlog_Tweedlede_pq.proj.txt"

TS_PATTERN = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<msg>.*)$")
ZONE_PATTERN = re.compile(r"^You have entered ([^\.]+)\.", re.I)
DING_PATTERN = re.compile(r"Welcome to level (\d+)!", re.I)
AA_PATTERN = re.compile(r"You have gained an ability point!\s*You now have (\d+) ability point(?:\(s\)|s)?\.", re.I)
DEATH_PATTERN = re.compile(r"^(You have been slain by (.*?)|You died)\.?", re.I)
TELL_SENT = re.compile(r"^You told ([A-Za-z]+),\s*'(.*)'", re.I)
TELL_RECV = re.compile(r"^([A-Za-z]+) tells you,\s*'(.*)'", re.I)
CAST_PATTERN = re.compile(r"^You begin (?:casting|singing) (.*?)\.", re.I)
GUILD_JOIN = re.compile(r"^You have joined (?!the group|the raid)(.+?)\.?$", re.I)
GUILD_LEAVE = re.compile(r"^You are no longer a member of (.+?)\.?$", re.I)
GUILD_KILL = re.compile(r"^Druzzil Ro tells the guild, '(?P<player>.+?) of (?P<guild>.+?)> has killed (?P<boss>.+?) in (?P<zone>.+?)!'", re.I)
LOCKOUT_PATTERN = re.compile(r"^You have incurred a lockout for (?P<boss>.+?) that expires in", re.I)
LOCAL_SLAY = re.compile(r"^(?P<target>.*?) has been slain by (?P<killer>.*?)!", re.I)

KUNARK_ZONES = {'The Overthere', 'Field of Bone', 'Kurn\'s Tower', 'Lake of Ill Omen', 'Firiona Vie', 'Timorous Deep', 'The Burning Wood', 'Skyfire Mountains', 'Chardok', 'Ruins of Sebilis', 'Karnor\'s Castle', 'The Emerald Jungle', 'Trakanon\'s Teeth'}
VELIOUS_ZONES = {'Iceclad Ocean', 'Eastern Wastes', 'The Great Divide', 'Kael Drakkel', 'Thurgadin', 'Crystal Caverns', 'Western Wastes', 'Temple of Veeshan', 'Siren\'s Grotto', 'Cobalt Scar', 'Plane of Mischief'}
LUCLIN_ZONES = {'The Nexus', 'Nexus', 'The Bazaar', 'Shadow Haven', 'The Maiden\'s Eye', 'The Umbral Plains', 'Ssraeshza Temple', 'Vex Thal', 'The Fungus Grove', 'The Twilight Sea', 'Sanctus Seru', 'The Dawnshroud Peaks', 'Akheva Ruins'}

def norm_zone(z):
    if not z:
        return ""
    return z.lower().replace(" (instanced)", "").replace(" instanced", "").replace("the ", "").strip()

def analyze():
    current_zone = "Unknown"
    first_ts = None
    last_ts = None
    
    zone_entries = Counter()
    zone_deaths = Counter()
    zone_aas = Counter()
    
    level_timeline = []
    seen_levels = set()
    aa_events = []
    deaths = []
    guild_history = []
    
    tells_sent = Counter()
    tells_recv = Counter()
    spells_cast = Counter()
    
    lockouts = []
    attended_guild_kills = []
    remote_guild_kills = []
    
    expansion_firsts = {
        "Kunark": None,
        "Velious": None,
        "Luclin": None
    }
    
    epic_quest = None

    print(f"Deep analyzing {LOG_FILE}...")
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = TS_PATTERN.match(line)
            if not m:
                continue
            ts, msg = m.group("ts"), m.group("msg")
            if first_ts is None:
                first_ts = ts
            last_ts = ts
            
            # Zone tracking
            if msg.startswith("You have entered "):
                zm = ZONE_PATTERN.match(msg)
                if zm:
                    current_zone = zm.group(1).strip()
                    zone_entries[current_zone] += 1
                    
                    if not expansion_firsts["Kunark"] and any(kz.lower() in current_zone.lower() for kz in KUNARK_ZONES):
                        expansion_firsts["Kunark"] = {"timestamp": ts, "zone": current_zone}
                    if not expansion_firsts["Velious"] and any(vz.lower() in current_zone.lower() for vz in VELIOUS_ZONES):
                        expansion_firsts["Velious"] = {"timestamp": ts, "zone": current_zone}
                    if not expansion_firsts["Luclin"] and any(lz.lower() in current_zone.lower() for lz in LUCLIN_ZONES):
                        expansion_firsts["Luclin"] = {"timestamp": ts, "zone": current_zone}
                continue

            # Guild changes
            if msg.startswith("You have joined "):
                gjm = GUILD_JOIN.match(msg)
                if gjm:
                    guild_history.append({"timestamp": ts, "action": "joined", "guild": gjm.group(1).strip()})
                continue
            elif msg.startswith("You are no longer a member of "):
                glm = GUILD_LEAVE.match(msg)
                if glm:
                    guild_history.append({"timestamp": ts, "action": "left", "guild": glm.group(1).strip()})
                continue

            # Level dings
            if "Welcome to level " in msg:
                dm = DING_PATTERN.search(msg)
                if dm:
                    lvl = int(dm.group(1))
                    is_first = lvl not in seen_levels
                    seen_levels.add(lvl)
                    level_timeline.append({
                        "timestamp": ts,
                        "level": lvl,
                        "zone": current_zone,
                        "first_time": is_first
                    })
                continue
                
            # AA Points
            if "You have gained an ability point!" in msg:
                am = AA_PATTERN.search(msg)
                banked = int(am.group(1)) if am else None
                zone_aas[current_zone] += 1
                aa_events.append({"timestamp": ts, "banked": banked, "zone": current_zone})
                continue

            # Lockouts (direct proof of raid participation)
            if msg.startswith("You have incurred a lockout for "):
                lm = LOCKOUT_PATTERN.match(msg)
                if lm:
                    lockouts.append({"timestamp": ts, "boss": lm.group("boss").strip(), "zone": current_zone})
                continue

            # Guild kill announcements (check player attendance)
            if msg.startswith("Druzzil Ro tells the guild, '"):
                gkm = GUILD_KILL.match(msg)
                if gkm:
                    target_zone = gkm.group("zone").strip()
                    attended = norm_zone(current_zone) in norm_zone(target_zone) or norm_zone(target_zone) in norm_zone(current_zone)
                    kill_obj = {
                        "timestamp": ts,
                        "boss": gkm.group("boss"),
                        "killer": gkm.group("player"),
                        "zone": target_zone,
                        "player_zone": current_zone
                    }
                    if attended:
                        attended_guild_kills.append(kill_obj)
                    else:
                        remote_guild_kills.append(kill_obj)
                continue

            # Deaths
            if msg.startswith("You have been slain by") or msg == "You died.":
                dm = DEATH_PATTERN.match(msg)
                killer = dm.group(2) if dm and dm.group(2) else "Unknown/Gravity"
                zone_deaths[current_zone] += 1
                deaths.append({"timestamp": ts, "killer": killer, "zone": current_zone})
                continue
                
            # Tells
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
                
            # Spells
            if msg.startswith("You begin "):
                cm = CAST_PATTERN.match(msg)
                if cm:
                    spells_cast[cm.group(1)] += 1
                continue

            # Epic Quest completion detection
            if "worthy to bear the Serpent" in msg or "Snek Staff of the Serpent" in msg:
                if not epic_quest:
                    epic_quest = {
                        "name": "Staff of the Serpent",
                        "class": "Enchanter Epic 1.0",
                        "timestamp": ts,
                        "zone": current_zone
                    }

    # Aggregate unique lockout bosses
    boss_counts = Counter(x["boss"] for x in lockouts)
    
    result = {
        "character": "Tweedlede",
        "class": "Enchanter",
        "date_range": {"first": first_ts, "last": last_ts},
        "guild_history": guild_history,
        "expansion_firsts": expansion_firsts,
        "epic_quest": epic_quest,
        "stats": {
            "total_deaths": len(deaths),
            "total_level_dings": len(level_timeline),
            "max_level": 60,
            "total_aas_earned": len(aa_events),
            "total_lockouts": len(lockouts),
            "unique_lockout_bosses": len(boss_counts),
            "attended_guild_kills": len(attended_guild_kills),
            "remote_guild_kills": len(remote_guild_kills),
            "top_zones_by_entries": zone_entries.most_common(10),
            "top_zones_by_deaths": zone_deaths.most_common(10),
            "top_zones_by_aas": zone_aas.most_common(10),
            "top_tell_recipients": tells_sent.most_common(10),
            "top_tell_senders": tells_recv.most_common(10),
            "top_spells_cast": spells_cast.most_common(10),
            "top_lockout_bosses": boss_counts.most_common(15)
        },
        "level_timeline_firsts": [x for x in level_timeline if x["first_time"]],
        "aa_events": aa_events,
        "attended_guild_kills_sample": attended_guild_kills[:20],
        "lockouts_sample": lockouts[:20]
    }

    out_path = r"C:\code\quarm-chronicle\data\sample_output\tweedlede_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Summary successfully updated in {out_path}!")

if __name__ == "__main__":
    analyze()
