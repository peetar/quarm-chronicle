import os
import re
import json
import sys
from collections import defaultdict, Counter
from datetime import datetime
from typing import Optional, Dict, Any, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.models.npc_database import NPCDatabase
from src.parser.stitcher import LogStitcher

TS_PATTERN = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<msg>.*)$")
ZONE_PATTERN = re.compile(r"^You have entered ([^\.]+)\.", re.I)
DING_PATTERN = re.compile(r"Welcome to level (\d+)!", re.I)
AA_PATTERN = re.compile(r"You have gained an ability point!\s*You now have (\d+) ability point(?:\(s\)|s)?\.", re.I)
DEATH_SLAIN = re.compile(r"^You have been slain by ([^!]+)!", re.I)
CAST_PATTERN = re.compile(r"^You begin (?:casting|singing) (.*?)\.", re.I)
GUILD_JOIN = re.compile(r"^You have joined (?!the group|the raid)(.+?)\.?$", re.I)
GUILD_LEAVE = re.compile(r"^You are no longer a member of (.+?)\.?$", re.I)
GUILD_KILL = re.compile(r"^Druzzil Ro tells the guild, '(?P<player>.+?) of (?P<guild>.+?)> has killed (?P<boss>.+?) in (?P<zone>.+?)!'", re.I)
LOCKOUT_PATTERN = re.compile(r"^You have incurred a lockout for (?P<boss>.+?) that expires in", re.I)
LOCAL_SLAY = re.compile(r"^(?P<target>.*?) has been slain by (?P<killer>.*?)!", re.I)
PVP_KILL = re.compile(r"^\[PVP\]\s*(?P<player>.+?)\s*of\s*<(?P<guild>.+?)>\s*has killed\s*(?P<boss>.+?)\s*in\s*(?P<zone>.+?)!", re.I)

KUNARK_ZONES = {'The Overthere', 'Field of Bone', 'Kurn\'s Tower', 'Lake of Ill Omen', 'Firiona Vie', 'Timorous Deep', 'The Burning Wood', 'Skyfire Mountains', 'Chardok', 'Ruins of Sebilis', 'Karnor\'s Castle', 'The Emerald Jungle', 'Trakanon\'s Teeth'}
VELIOUS_ZONES = {'Iceclad Ocean', 'Eastern Wastes', 'The Great Divide', 'Kael Drakkel', 'Thurgadin', 'Crystal Caverns', 'Western Wastes', 'Temple of Veeshan', 'Siren\'s Grotto', 'Cobalt Scar', 'Plane of Mischief'}
LUCLIN_ZONES = {'The Nexus', 'Nexus', 'The Bazaar', 'Shadow Haven', 'The Maiden\'s Eye', 'The Umbral Plains', 'Ssraeshza Temple', 'Vex Thal', 'The Fungus Grove', 'The Twilight Sea', 'Sanctus Seru', 'The Dawnshroud Peaks', 'Akheva Ruins'}
POP_ZONES = {'Plane of Knowledge', 'Plane of Tranquility', 'Plane of Innovation', 'Plane of Disease', 'Plane of Nightmare', 'Plane of Justice', 'Plane of Storms', 'Plane of Valor', 'Plane of Torment', 'Plane of Tactics', 'Plane of Air', 'Plane of Fire', 'Plane of Water', 'Plane of Earth', 'Plane of Time'}

PINNACLES = {
    "Classic": ["Lord Nagafen", "Lady Vox"],
    "Kunark": ["Phara Dar"],
    "Velious": ["Tunare", "Vulak`Aerr", "The Avatar of War"],
    "Luclin": ["Aten Ha Ra"],
    "Planes of Power": ["Quarm"]
}

NORM_PINNACLES = {
    "lord nagafen": "Lord Nagafen",
    "lady vox": "Lady Vox",
    "phara dar": "Phara Dar",
    "tunare": "Tunare",
    "vulak'aerr": "Vulak`Aerr",
    "vulak`aerr": "Vulak`Aerr",
    "the herald of vulak'aerr": "Vulak`Aerr",
    "the avatar of war": "The Avatar of War",
    "avatar of war": "The Avatar of War",
    "aten ha ra": "Aten Ha Ra",
    "quarm": "Quarm"
}

SIGNATURE_SPELLS_BY_CLASS = {
    "Enchanter": [
        "Shallow Breath", "Pacify", "Mesmerize", "Minor Shielding", "Boltran's Agacerie",
        "Color Slant", "Clarity II", "Rapture", "Tashani", "Dementia", "Boon of the Clear Mind", "Allure"
    ],
    "Cleric": [
        "Complete Healing", "Greater Healing", "Reviviscence", "Yaulp V", "Divine Intervention",
        "Heroic Bond", "Aegolism", "Immobilize", "Celestial Elixir", "Strike", "Pacify"
    ],
    "Bard": [
        "Selo's Accelerating Chorus", "Largo's Absonant Binding", "Fufil's Curtailing Chant",
        "Solon's Bewitching Bravura", "Occlusion of Sound", "Cantata of Soothing", "Chant of Flame"
    ],
    "Necromancer": [
        "Dooming Darkness", "Splurt", "Cessation of Cor", "Vexing Mordinia", "Ancient: Lifebane",
        "Mana Conversion", "Feign Death", "Emissary of Thule", "Sedulous Subversion", "Funeral Pyre of Kelador"
    ]
}

EPICS_REF = {
    "Enchanter": {"weapon": "Staff of the Serpent", "effect": "Speed of the Shissar"},
    "Bard": {"weapon": "Singing Short Sword", "effect": "Dance of the Blade"},
    "Cleric": {"weapon": "Water Sprinkler of Nem Ankh", "effect": "Reviviscence"},
    "Necromancer": {"weapon": "Scythe of the Shadowed Soul", "effect": "Tormenting Darkness"}
}

TIME_FORMAT = "%a %b %d %H:%M:%S %Y"

def normalize_boss_name(name: str) -> str:
    n = name.strip().replace("`", "'")
    nl = n.lower()
    if nl.startswith("the "):
        nl = nl[4:].strip()
    for norm_k, canon in NORM_PINNACLES.items():
        k = norm_k.replace("`", "'")
        if k.startswith("the "):
            k = k[4:].strip()
        if nl == k:
            return canon
    return name.strip()

def extract_timeline(character_name: str, log_dir: str = r"C:\TAKPv22", output_path: Optional[str] = None) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"Extracting Timeline Events for: {character_name}")
    print(f"=======================================================")

    stitcher = LogStitcher(log_dir, character_name)
    file_summary = stitcher.get_summary()
    print(f"Discovered {len(file_summary)} log file(s):")
    for fs in file_summary:
        print(f"  • {fs['file']} ({fs['size_mb']} MB) [{fs['start']} -> {fs['end']}]")

    npc_db = NPCDatabase()

    # Trackers
    first_ts = None
    last_ts = None
    current_zone = "Unknown"
    seen_levels = set()
    seen_zones = set()
    seen_spells = set()
    epic_acquired = False
    known_guilds = {"dungeons and dragons"}
    
    # Event collections by significance level
    level1_events: List[Dict[str, Any]] = []
    level2_events: List[Dict[str, Any]] = []
    level3_events: List[Dict[str, Any]] = []

    # Level 3 Aggregation buffers
    # Daily zone entries: date_str -> Counter(zone -> count)
    daily_zone_entries = defaultdict(Counter)
    
    # Raid boss kills: cluster window of 600s
    raw_boss_events = [] # (dt, boss_name, event_type, ts, zone)
    
    # Era first detection
    era_firsts = {
        "Classic": None,
        "Kunark": None,
        "Velious": None,
        "Luclin": None,
        "Planes of Power": None
    }

    first_dt = None
    last_dt = None

    line_count = 0
    for line in stitcher.stream_lines():
        line_count += 1
        m = TS_PATTERN.match(line)
        if not m:
            continue
        ts, msg = m.group("ts"), m.group("msg")
        try:
            dt = datetime.strptime(ts, TIME_FORMAT)
            date_iso = dt.strftime("%Y-%m-%d")
        except ValueError:
            dt = None
            date_iso = None

        if first_ts is None:
            first_ts = ts
            first_dt = dt
            era_firsts["Classic"] = {"timestamp": ts, "date": date_iso, "zone": current_zone}
        last_ts = ts
        if dt:
            last_dt = dt

        # -------------------------------------------------------------
        # Zone Transitions
        # -------------------------------------------------------------
        if msg.startswith("You have entered "):
            zm = ZONE_PATTERN.match(msg)
            if zm:
                zname = zm.group(1).strip()
                # Filter out PvP arena flag sub-area messages
                if "arena (pvp) area" in zname.lower():
                    continue
                current_zone = zname
                
                # Level 2: First time entering a new zone
                if current_zone not in seen_zones:
                    seen_zones.add(current_zone)
                    level2_events.append({
                        "level": 2,
                        "type": "zone_first",
                        "title": f"Discovered {current_zone}",
                        "zone": current_zone,
                        "timestamp": ts,
                        "date": date_iso,
                        "iso": dt.isoformat() if dt else None
                    })

                # Era Tracking
                if not era_firsts["Kunark"] and any(kz.lower() in current_zone.lower() for kz in KUNARK_ZONES):
                    era_firsts["Kunark"] = {"timestamp": ts, "date": date_iso, "zone": current_zone}
                if not era_firsts["Velious"] and any(vz.lower() in current_zone.lower() for vz in VELIOUS_ZONES):
                    era_firsts["Velious"] = {"timestamp": ts, "date": date_iso, "zone": current_zone}
                if not era_firsts["Luclin"] and any(lz.lower() in current_zone.lower() for lz in LUCLIN_ZONES):
                    era_firsts["Luclin"] = {"timestamp": ts, "date": date_iso, "zone": current_zone}
                if not era_firsts["Planes of Power"] and any(pz.lower() in current_zone.lower() for pz in POP_ZONES):
                    era_firsts["Planes of Power"] = {"timestamp": ts, "date": date_iso, "zone": current_zone}

                # Level 3: Daily zone transition counts
                if date_iso:
                    daily_zone_entries[date_iso][current_zone] += 1
            continue

        # -------------------------------------------------------------
        # Level Dings (Level 1 Significance)
        # -------------------------------------------------------------
        if "Welcome to level " in msg:
            dm = DING_PATTERN.search(msg)
            if dm:
                lvl = int(dm.group(1))
                if lvl not in seen_levels:
                    seen_levels.add(lvl)
                    level1_events.append({
                        "level": 1,
                        "type": "level_ding",
                        "ding_level": lvl,
                        "title": f"Level {lvl}",
                        "badge": str(lvl),
                        "zone": current_zone,
                        "timestamp": ts,
                        "date": date_iso,
                        "iso": dt.isoformat() if dt else None
                    })
            continue

        # -------------------------------------------------------------
        # Guild Joins / Departures (Level 1 Significance)
        # -------------------------------------------------------------
        if msg.startswith("You have joined "):
            gjm = GUILD_JOIN.match(msg)
            if gjm:
                guild_name = gjm.group(1).strip()
                known_guilds.add(guild_name.lower())
                level1_events.append({
                    "level": 1,
                    "type": "guild_join",
                    "title": f"Joined <{guild_name}>",
                    "guild": guild_name,
                    "action": "joined",
                    "zone": current_zone,
                    "timestamp": ts,
                    "date": date_iso,
                    "iso": dt.isoformat() if dt else None
                })
            continue
        elif msg.startswith("You are no longer a member of "):
            glm = GUILD_LEAVE.match(msg)
            if glm:
                guild_name = glm.group(1).strip()
                level1_events.append({
                    "level": 1,
                    "type": "guild_leave",
                    "title": f"Left <{guild_name}>",
                    "guild": guild_name,
                    "action": "left",
                    "zone": current_zone,
                    "timestamp": ts,
                    "date": date_iso,
                    "iso": dt.isoformat() if dt else None
                })
            continue

        # -------------------------------------------------------------
        # Epic Quest Acquisition (Level 1 Significance)
        # -------------------------------------------------------------
        if not epic_acquired:
            for cls_name, edata in EPICS_REF.items():
                if edata["weapon"].lower() in msg.lower():
                    if "you say to your guild" in msg.lower() or "you have looted" in msg.lower() or "worthy" in msg.lower() or "primary:" in msg.lower():
                        epic_acquired = True
                        level1_events.append({
                            "level": 1,
                            "type": "epic_acquired",
                            "title": edata["weapon"],
                            "epic_class": f"{cls_name} Epic 1.0",
                            "effect": edata["effect"],
                            "zone": current_zone,
                            "timestamp": ts,
                            "date": date_iso,
                            "iso": dt.isoformat() if dt else None
                        })
                        break

        # -------------------------------------------------------------
        # AA Points (Level 2 Significance)
        # -------------------------------------------------------------
        if "You have gained an ability point!" in msg:
            am = AA_PATTERN.search(msg)
            banked = int(am.group(1)) if am else None
            level2_events.append({
                "level": 2,
                "type": "aa_gain",
                "title": f"+1 AA Point ({banked} banked)" if banked is not None else "+1 AA Point",
                "banked": banked,
                "zone": current_zone,
                "timestamp": ts,
                "date": date_iso,
                "iso": dt.isoformat() if dt else None
            })
            continue

        # -------------------------------------------------------------
        # Signature Spells First Cast (Level 2 Significance)
        # -------------------------------------------------------------
        if msg.startswith("You begin "):
            cm = CAST_PATTERN.match(msg)
            if cm:
                spell_name = cm.group(1).strip()
                for c_name, sig_list in SIGNATURE_SPELLS_BY_CLASS.items():
                    for sig in sig_list:
                        if sig.lower() == spell_name.lower() and sig not in seen_spells:
                            seen_spells.add(sig)
                            level2_events.append({
                                "level": 2,
                                "type": "spell_first",
                                "title": f"First Cast: {sig}",
                                "spell": sig,
                                "spell_class": c_name,
                                "zone": current_zone,
                                "timestamp": ts,
                                "date": date_iso,
                                "iso": dt.isoformat() if dt else None
                            })
            continue

        # -------------------------------------------------------------
        # Deaths (Level 3 Significance)
        # -------------------------------------------------------------
        if msg.startswith("You have been slain by ") or msg == "You died.":
            if msg.startswith("You have been slain by "):
                dsm = DEATH_SLAIN.match(msg)
                killer = dsm.group(1).strip() if dsm else "Unknown"
            else:
                killer = "Bleeding / Environmental / Gravity"
            level3_events.append({
                "level": 3,
                "type": "death",
                "title": f"Died to {killer}",
                "killer": killer,
                "zone": current_zone,
                "timestamp": ts,
                "date": date_iso,
                "iso": dt.isoformat() if dt else None
            })
            continue


        # -------------------------------------------------------------
        # Boss Kills & Lockouts Buffer
        # -------------------------------------------------------------
        if msg.startswith("You have incurred a lockout for "):
            lm = LOCKOUT_PATTERN.match(msg)
            if lm:
                bname = lm.group("boss").strip()
                if dt:
                    raw_boss_events.append((dt, bname, "lockout", ts, current_zone, False))
            continue

        if msg.startswith("Druzzil Ro tells the guild, '"):
            gkm = GUILD_KILL.match(msg)
            if gkm:
                bname = gkm.group("boss").strip()
                bzone = gkm.group("zone").strip()
                # Verify player was present in the raid zone to avoid false remote kills
                in_zone = bzone.lower() in current_zone.lower() or current_zone.lower() in bzone.lower()
                if in_zone and dt:
                    raw_boss_events.append((dt, bname, "guild_kill", ts, bzone, False))
            continue

        if msg.startswith("[PVP] ") and "has killed " in msg:
            pm = PVP_KILL.match(msg)
            if pm:
                player = pm.group("player").strip()
                guild = pm.group("guild").strip()
                bname = pm.group("boss").strip()
                bzone = pm.group("zone").strip()
                is_me = player.lower() == character_name.lower()
                in_zone = bzone.lower() in current_zone.lower() or current_zone.lower() in bzone.lower()
                is_guild_in_zone = in_zone and guild.lower() in known_guilds
                if (is_me or is_guild_in_zone) and dt:
                    raw_boss_events.append((dt, bname, "pvp_kill", ts, bzone, True))
            continue

        if "has been slain by" in msg:
            sm = LOCAL_SLAY.match(msg)
            if sm:
                target = sm.group("target").strip()
                killer = sm.group("killer").strip()
                # Check for Vulak or target matches
                norm_tgt = normalize_boss_name(target)
                if norm_tgt in NORM_PINNACLES.values() or "vulak" in target.lower():
                    if dt:
                        raw_boss_events.append((dt, norm_tgt, "local_slay", ts, current_zone, False))
            continue

    # -------------------------------------------------------------
    # Cluster Boss Events (10-minute sliding window)
    # -------------------------------------------------------------
    print(f"Clustering {len(raw_boss_events)} raw boss event signals...")
    raw_boss_events.sort(key=lambda x: x[0])
    
    clustered_boss_kills = []
    pinnacle_first_kills = {}
    
    for dt, bname, etype, ts, bzone, is_pvp in raw_boss_events:
        canon_name = normalize_boss_name(bname)
        # Check if matches existing cluster within 600s
        matched = False
        for c in clustered_boss_kills:
            if c["boss"] == canon_name and abs((dt - c["dt"]).total_seconds()) <= 600:
                matched = True
                break
        if not matched:
            npc_res = npc_db.resolve(canon_name, bzone)
            is_pinnacle = canon_name in NORM_PINNACLES.values()
            
            kill_obj = {
                "boss": canon_name,
                "dt": dt,
                "timestamp": ts,
                "date": dt.strftime("%Y-%m-%d"),
                "iso": dt.isoformat(),
                "zone": bzone,
                "is_pinnacle": is_pinnacle,
                "is_pvp": is_pvp,
                "id": npc_res["id"] if npc_res else None,
                "url": npc_res["url"] if npc_res else None
            }
            clustered_boss_kills.append(kill_obj)
            
            # If Pinnacle First Kill -> Level 1 Event!
            if is_pinnacle and canon_name not in pinnacle_first_kills:
                pinnacle_first_kills[canon_name] = ts
                level1_events.append({
                    "level": 1,
                    "type": "pinnacle_first",
                    "title": f"First Kill: {canon_name}",
                    "boss": canon_name,
                    "zone": bzone,
                    "id": kill_obj["id"],
                    "url": kill_obj["url"],
                    "timestamp": ts,
                    "date": kill_obj["date"],
                    "iso": kill_obj["iso"]
                })

            # Level 3 Event: Each boss kill (Raid and PvP)
            level3_events.append({
                "level": 3,
                "type": "pvp_boss_kill" if is_pvp else "raid_boss_kill",
                "title": f"Defeated {canon_name}" + (" (PvP)" if is_pvp else ""),
                "boss": canon_name,
                "is_pinnacle": is_pinnacle,
                "is_pvp": is_pvp,
                "zone": bzone,
                "id": kill_obj["id"],
                "url": kill_obj["url"],
                "timestamp": ts,
                "date": kill_obj["date"],
                "iso": kill_obj["iso"]
            })

    # -------------------------------------------------------------
    # Append Daily Zone Activity Summaries (Level 3 Events)
    # -------------------------------------------------------------
    for date_str, zcounts in daily_zone_entries.items():
        total_transitions = sum(zcounts.values())
        top_zone_str = ", ".join(f"{z} (x{c})" for z, c in zcounts.most_common(3))
        level3_events.append({
            "level": 3,
            "type": "daily_zone_activity",
            "title": f"{total_transitions} Zone Transitions",
            "summary": top_zone_str,
            "total_transitions": total_transitions,
            "breakdown": dict(zcounts),
            "date": date_str,
            "timestamp": f"{date_str} 12:00:00"
        })

    # Sort all lists chronologically by timestamp/date
    def parse_sort_key(e):
        return e.get("iso") or e.get("date") or "9999"

    level1_events.sort(key=parse_sort_key)
    level2_events.sort(key=parse_sort_key)
    level3_events.sort(key=parse_sort_key)

    # Era Milestones
    eras_list = []
    for era_name, edata in era_firsts.items():
        if edata:
            eras_list.append({
                "era": era_name,
                "timestamp": edata["timestamp"],
                "date": edata["date"],
                "zone": edata["zone"]
            })

    result = {
        "character": character_name,
        "date_range": {
            "start_timestamp": first_ts,
            "end_timestamp": last_ts,
            "start_date": first_dt.strftime("%Y-%m-%d") if first_dt else None,
            "end_date": last_dt.strftime("%Y-%m-%d") if last_dt else None,
            "start_iso": first_dt.isoformat() if first_dt else None,
            "end_iso": last_dt.isoformat() if last_dt else None
        },
        "total_log_lines": line_count,
        "eras": eras_list,
        "counts": {
            "level_1_overview_events": len(level1_events),
            "level_2_seasonal_events": len(level2_events),
            "level_3_micro_events": len(level3_events),
            "total_events": len(level1_events) + len(level2_events) + len(level3_events)
        },
        "events": {
            "level_1": level1_events,
            "level_2": level2_events,
            "level_3": level3_events
        }
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Timeline successfully extracted to {output_path}!")
        print(f"Summary counts: Level 1: {len(level1_events)}, Level 2: {len(level2_events)}, Level 3: {len(level3_events)}")

    return result

if __name__ == "__main__":
    char = sys.argv[1] if len(sys.argv) > 1 else "Tweedlede"
    out = os.path.join(PROJECT_ROOT, "data", "sample_output", f"{char.lower()}_timeline.json")
    extract_timeline(char, output_path=out)
