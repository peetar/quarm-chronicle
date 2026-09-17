import os
import re
import json
from collections import Counter, defaultdict

LOG_FILE = r"C:\TAKPv22\eqlog_Tweedlede_pq.proj.txt"

TS_PATTERN = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<msg>.*)$")
ZONE_PATTERN = re.compile(r"^You have entered ([^\.]+)\.", re.I)
DING_PATTERN = re.compile(r"Welcome to level (\d+)!", re.I)
AA_PATTERN = re.compile(r"You have gained an ability point!\s*You now have (\d+) ability point(?:\(s\)|s)?\.", re.I)
DEATH_SLAIN = re.compile(r"^You have been slain by ([^!]+)!", re.I)
DEATH_DIED = re.compile(r"^You died\.", re.I)
DEATH_BY_PATTERN = re.compile(r"^You have been slain by ([^!]+)!", re.I)
REZ_PATTERN = re.compile(r"You regain some experience from resurrection", re.I)
YOU_SLAIN_PATTERN = re.compile(r"^You have slain (?:an? )?([^!]+)!", re.I)

TELL_SENT = re.compile(r"^You told ([A-Za-z]+),\s*'(.*)'", re.I)
TELL_RECV = re.compile(r"^([A-Za-z]+) tells you,\s*'(.*)'", re.I)
CAST_PATTERN = re.compile(r"^You begin (?:casting|singing) (.*?)\.", re.I)
GUILD_JOIN = re.compile(r"^You have joined (?!the group|the raid)(.+?)\.?$", re.I)
GUILD_LEAVE = re.compile(r"^You are no longer a member of (.+?)\.?$", re.I)
GUILD_KILL = re.compile(r"^Druzzil Ro tells the guild, '(?P<player>.+?) of (?P<guild>.+?)> has killed (?P<boss>.+?) in (?P<zone>.+?)!'", re.I)
LOCKOUT_PATTERN = re.compile(r"^You have incurred a lockout for (?P<boss>.+?) that expires in", re.I)
LOCAL_SLAY = re.compile(r"^(?P<target>.*?) has been slain by (?P<killer>.*?)!", re.I)

GROUP_TELL = re.compile(r"^([A-Za-z]+) tells the group,\s*'(.*)'", re.I)
RAID_TELL = re.compile(r"^([A-Za-z]+) tells the raid,\s*'(.*)'", re.I)
GROUP_CHAT = re.compile(r"^\[Group\]\s*([A-Za-z]+):\s*(.*)", re.I)
RAID_CHAT = re.compile(r"^\[Raid\]\s*([A-Za-z]+):\s*(.*)", re.I)
LOOT_PATTERN = re.compile(r"^--([A-Za-z]+) has looted a (.*)\.--", re.I)

KUNARK_ZONES = {'The Overthere', 'Field of Bone', 'Kurn\'s Tower', 'Lake of Ill Omen', 'Firiona Vie', 'Timorous Deep', 'The Burning Wood', 'Skyfire Mountains', 'Chardok', 'Ruins of Sebilis', 'Karnor\'s Castle', 'The Emerald Jungle', 'Trakanon\'s Teeth'}
VELIOUS_ZONES = {'Iceclad Ocean', 'Eastern Wastes', 'The Great Divide', 'Kael Drakkel', 'Thurgadin', 'Crystal Caverns', 'Western Wastes', 'Temple of Veeshan', 'Siren\'s Grotto', 'Cobalt Scar', 'Plane of Mischief'}
LUCLIN_ZONES = {'The Nexus', 'Nexus', 'The Bazaar', 'Shadow Haven', 'The Maiden\'s Eye', 'The Umbral Plains', 'Ssraeshza Temple', 'Vex Thal', 'The Fungus Grove', 'The Twilight Sea', 'Sanctus Seru', 'The Dawnshroud Peaks', 'Akheva Ruins'}

# Defined Pinnacle Bosses
PINNACLES = {
    "Classic": ["Lord Nagafen", "Lady Vox"],
    "Kunark": ["Phara Dar"],
    "Velious": ["Tunare", "Vulak`Aerr", "The Avatar of War"],
    "Luclin": ["Aten Ha Ra"],
    "Planes of Power": ["Quarm"]
}

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
    death_killers = Counter()
    rez_count = 0
    npcs_slain = Counter()
    
    guild_history = []
    
    tells_sent = Counter()
    tells_recv = Counter()
    spells_cast = Counter()
    
    group_companions = Counter()
    raid_companions = Counter()
    looters = Counter()
    
    lockouts = []
    all_guild_kills = []
    local_slays = []
    
    pinnacle_first_kills = {}
    pinnacle_total_kills = Counter()
    all_boss_kills = Counter()
    
    expansion_firsts = {
        "Kunark": None,
        "Velious": None,
        "Luclin": None
    }
    
    epic_quest = None

    print(f"Deep analyzing {LOG_FILE} with Pinnacle Boss definitions and social metrics...")
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

            # Resurrections accepted
            if REZ_PATTERN.search(msg):
                rez_count += 1
                continue

            # NPCs personally slain
            if msg.startswith("You have slain "):
                sm = YOU_SLAIN_PATTERN.match(msg)
                if sm:
                    npcs_slain[sm.group(1).strip()] += 1
                continue

            # Lockouts (direct proof of raid participation)
            if msg.startswith("You have incurred a lockout for "):
                lm = LOCKOUT_PATTERN.match(msg)
                if lm:
                    boss_name = lm.group("boss").strip()
                    lockouts.append({"timestamp": ts, "boss": boss_name, "zone": current_zone})
                    all_boss_kills[boss_name] += 1
                    for era, plist in PINNACLES.items():
                        for pb in plist:
                            if pb.lower() in boss_name.lower():
                                pinnacle_total_kills[pb] += 1
                                if pb not in pinnacle_first_kills:
                                    pinnacle_first_kills[pb] = ts
                continue

            # Guild kill announcements
            if msg.startswith("Druzzil Ro tells the guild, '"):
                gkm = GUILD_KILL.match(msg)
                if gkm:
                    boss_name = gkm.group("boss").strip()
                    all_guild_kills.append({
                        "timestamp": ts,
                        "boss": boss_name,
                        "killer": gkm.group("player"),
                        "zone": gkm.group("zone").strip()
                    })
                    all_boss_kills[boss_name] += 1
                    for era, plist in PINNACLES.items():
                        for pb in plist:
                            if pb.lower() in boss_name.lower():
                                pinnacle_total_kills[pb] += 1
                                if pb not in pinnacle_first_kills:
                                    pinnacle_first_kills[pb] = ts
                continue

            # Local slays
            if " has been slain by " in msg:
                lsm = LOCAL_SLAY.match(msg)
                if lsm:
                    target = lsm.group("target").strip()
                    for era, plist in PINNACLES.items():
                        for pb in plist:
                            if pb.lower() in target.lower():
                                local_slays.append({"timestamp": ts, "boss": pb, "killer": lsm.group("killer"), "zone": current_zone})
                                pinnacle_total_kills[pb] += 1
                                if pb not in pinnacle_first_kills:
                                    pinnacle_first_kills[pb] = ts
                continue

            # Deaths & Nemesis
            if msg.startswith("You have been slain by ") or msg == "You died.":
                if msg.startswith("You have been slain by "):
                    dsm = DEATH_SLAIN.match(msg)
                    killer = dsm.group(1).strip() if dsm else "Unknown"
                else:
                    killer = "Falling / Environmental"
                zone_deaths[current_zone] += 1
                deaths.append({"timestamp": ts, "killer": killer, "zone": current_zone})
                death_killers[killer] += 1
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

            # Group & Raid Companions
            gt = GROUP_TELL.match(msg) or GROUP_CHAT.match(msg)
            if gt:
                speaker = gt.group(1)
                if speaker.lower() != "you":
                    group_companions[speaker] += 1
                continue

            rt = RAID_TELL.match(msg) or RAID_CHAT.match(msg)
            if rt:
                speaker = rt.group(1)
                if speaker.lower() != "you":
                    raid_companions[speaker] += 1
                continue

            lt = LOOT_PATTERN.match(msg)
            if lt:
                looter = lt.group(1)
                if looter.lower() != "you":
                    looters[looter] += 1
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

    # Separate PvP duel deaths vs PvE mob deaths
    pve_nemesis = Counter({k: v for k, v in death_killers.items() if k != "Xebobn"})
    
    # Format Pinnacle Boss stats
    pinnacle_stats = {}
    for era, plist in PINNACLES.items():
        pinnacle_stats[era] = []
        for pb in plist:
            pinnacle_stats[era].append({
                "boss": pb,
                "first_kill": pinnacle_first_kills.get(pb, None),
                "total_kills_or_lockouts": pinnacle_total_kills.get(pb, 0)
            })

    result = {
        "character": "Tweedlede",
        "class": "Enchanter",
        "date_range": {"first": first_ts, "last": last_ts},
        "guild_history": guild_history,
        "expansion_firsts": expansion_firsts,
        "epic_quest": epic_quest,
        "pinnacle_bosses": pinnacle_stats,
        "stats": {
            "total_deaths": len(deaths),
            "resurrections_accepted": rez_count,
            "total_level_dings": len(level_timeline),
            "max_level": 60,
            "total_aas_earned": len(aa_events),
            "total_lockouts": len(lockouts),
            "total_guild_kill_announcements": len(all_guild_kills),
            "top_zones_by_entries": zone_entries.most_common(10),
            "top_zones_by_deaths": zone_deaths.most_common(10),
            "top_zones_by_aas": zone_aas.most_common(10),
            "top_npcs_slain": npcs_slain.most_common(10),
            "pvp_nemesis": ("Xebobn", death_killers["Xebobn"]),
            "top_pve_nemesis": pve_nemesis.most_common(5),
            "top_tell_recipients": tells_sent.most_common(10),
            "top_tell_senders": tells_recv.most_common(10),
            "top_group_companions": group_companions.most_common(10),
            "top_raid_companions": raid_companions.most_common(10),
            "top_looters_seen": looters.most_common(10),
            "top_spells_cast": spells_cast.most_common(10),
            "top_raid_boss_kills_overall": all_boss_kills.most_common(15)
        },
        "level_timeline_firsts": [x for x in level_timeline if x["first_time"]],
        "aa_events": aa_events
    }

    out_path = r"C:\code\quarm-chronicle\data\sample_output\tweedlede_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Summary successfully updated in {out_path}!")

if __name__ == "__main__":
    analyze()
