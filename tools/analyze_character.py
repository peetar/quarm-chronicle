import os
import re
import json
import sys
from collections import Counter
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
AA_GAIN_PATTERN = re.compile(r'^You have gained the ability \"(?P<name>[^\"]+)\" at a cost of (?P<cost>\d+) ability points?\.', re.I)
AA_IMPROVE_PATTERN = re.compile(r'^You have improved (?P<name>.+?)(?:\s+(?P<rank>\d+))? at a cost of (?P<cost>\d+) ability points?\.', re.I)

DEATH_SLAIN = re.compile(r"^You have been slain by ([^!]+)!", re.I)
DEATH_DIED = re.compile(r"^You died\.", re.I)
REZ_PATTERN = re.compile(r"You regain some experience from resurrection", re.I)
YOU_SLAIN_PATTERN = re.compile(r"^You have slain (?:an? )?([^!]+)!", re.I)

TELL_SENT = re.compile(r"^You told ([A-Za-z]+),\s*'(.*)'", re.I)
TELL_RECV = re.compile(r"^([A-Za-z\s]+) tells you,\s*'(.*)'", re.I)
CAST_PATTERN = re.compile(r"^You begin (?:casting|singing) (.*?)\.", re.I)
MEM_PATTERN = re.compile(r"^You have finished memorizing (.*?)\.", re.I)
BARD_DAMAGE_PATTERN = re.compile(r"has taken \d+ (?:non-melee )?damage from your (.*?)\.", re.I)

DISC_ACTIVATIONS = {
    # Monk
    'You assume a stone stance.': 'Stonestance Discipline',
    'You assume a void stance.': 'Voiddance Discipline',
    'You begin to whirl.': 'Whirlwind Discipline',
    'You summon your inner strength.': 'Inner Flame Discipline',
    'You prepare to strike with furious speed.': 'Hundred Fists Discipline',
    'You prepare for thunderous strikes.': 'Thunderkick Discipline',
    # Warrior
    'You assume a defensive fighting style.': 'Defensive Discipline',
    'You assume an evasive fighting style.': 'Evasive Discipline',
    'You assume an aggressive fighting style.': 'Aggressive Discipline',
    'You begin to throw frantic strikes.': 'Furious Discipline',
    'You ready yourself to deflect incoming blows.': 'Fortitude Discipline',
    'You prepare to attack with precision.': 'Precision Discipline',
    'You prepare to land a fell strike.': 'Fellstrike Discipline',
    'You prepare to land mighty strikes.': 'Mighty Strike Discipline',
    'You begin to charge your weapons.': 'Charge Discipline',
    # Ranger
    'You become hyper-focused on your archery.': 'Trueshot Discipline',
    'You prepare for weapon strikes.': 'Weapon Shield Discipline',
    # Rogue
    'You prepare to duel.': 'Duelist Discipline',
    'You focus on your kinesthetic movements.': 'Kinesthetics Discipline',
    'You become more nimble.': 'Nimble Discipline',
    'You focus your aim.': 'Deadeye Discipline',
    'You prepare to counterattack.': 'Counterattack Discipline',
    # General / Melee
    'You prepare to resist magical attacks.': 'Resistant Discipline',
    'You become fearless.': 'Fearless Discipline',
    'You steel your nerves.': 'Fearless Discipline',
}

KICK_HIT_PATTERN = re.compile(r"^You (?:flying kick|round kick|kick) .* for \d+ points? of damage\.", re.I)
MARTIAL_HIT_PATTERN = re.compile(r"^You (?:dragon punch|tail rake|tiger claw|eagle strike) .* for \d+ points? of damage\.", re.I)
BACKSTAB_HIT_PATTERN = re.compile(r"^You backstab .* for \d+ points? of damage\.", re.I)
FD_FALL_PATTERN = re.compile(r"^([A-Za-z]+) has fallen to the ground\.", re.I)

NPC_TELL_PATTERNS = [
    re.compile(r"\bMaster[\.!]?$", re.I),
    re.compile(r"^Attacking .* Master", re.I),
    re.compile(r"^Following you, Master", re.I),
    re.compile(r"^Guarding .* Master", re.I),
    re.compile(r"^At your service, Master", re.I),
    re.compile(r"^As you command, Master", re.I),
    re.compile(r"^I am unable to obey, Master", re.I),
    re.compile(r"^Sorry, Master", re.I),
    re.compile(r"^That(?:'ll| will) be \d+", re.I),
    re.compile(r"^I(?:'ll| will) give you \d+", re.I),
    re.compile(r"^I(?:'ll| will) buy that ", re.I),
    re.compile(r"^I don'?t buy ", re.I),
    re.compile(r"^I don'?t want that", re.I),
    re.compile(r"^You(?:'ll| will) have to pay ", re.I),
    re.compile(r"^I have nothing to give you for that", re.I),
    re.compile(r"^I cannot buy that from you", re.I),
    re.compile(r"^You cannot afford that", re.I),
    re.compile(r"^You do not have enough", re.I),
    re.compile(r"per (?:ticket|bottle|ration|flask|arrow|pattern|clay|sketches|sketch|meat)", re.I),
    re.compile(r"^Welcome to my bank!", re.I),
    re.compile(r"^Come back soon!", re.I),
    re.compile(r"^You don'?t have that much money in the bank!", re.I),
    re.compile(r"^You have deposited ", re.I),
    re.compile(r"^You have withdrawn ", re.I),
    re.compile(r"^You have increased your skill in ", re.I),
    re.compile(r"^You have no more training points", re.I),
    re.compile(r"^You will have to achieve level ", re.I),
    re.compile(r"^Welcome to the Guild of ", re.I),
    re.compile(r"^Binding your soul", re.I),
    re.compile(r"^You are now bound to this location", re.I),
]

def is_npc_tell(sender: str, text: str) -> bool:
    s = sender.strip()
    if " " in s:
        return True
    if s and s[0].islower():
        return True
    for p in NPC_TELL_PATTERNS:
        if p.search(text):
            return True
    return False

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

WHO_ENTRY_PATTERN = re.compile(r"^\[(?P<lvl>\d+)\s+(?P<cls>[A-Za-z\s]+)\]\s+(?:(?P<title>[A-Za-z]+)\s+)?(?P<first>[A-Za-z0-9]+)(?:\s+(?P<surname>[A-Za-z0-9]+))?(?:\s+\((?P<race>[A-Za-z\s]+)\))?(?:\s+<(?P<guild>[^>]+)>)?", re.I)
WHO_ANON_PATTERN = re.compile(r"^\[(?:ANONYMOUS|ROLEPLAYING)\]\s+(?:(?P<title>[A-Za-z]+)\s+)?(?P<first>[A-Za-z0-9]+)(?:\s+(?P<surname>[A-Za-z0-9]+))?(?:\s+\((?P<race>[A-Za-z\s]+)\))?(?:\s+<(?P<guild>[^>]+)>)?", re.I)

KUNARK_ZONES = {'The Overthere', 'Field of Bone', 'Kurn\'s Tower', 'Lake of Ill Omen', 'Firiona Vie', 'Timorous Deep', 'The Burning Wood', 'Skyfire Mountains', 'Chardok', 'Ruins of Sebilis', 'Karnor\'s Castle', 'The Emerald Jungle', 'Trakanon\'s Teeth'}
VELIOUS_ZONES = {'Iceclad Ocean', 'Eastern Wastes', 'The Great Divide', 'Kael Drakkel', 'Thurgadin', 'Crystal Caverns', 'Western Wastes', 'Temple of Veeshan', 'Siren\'s Grotto', 'Cobalt Scar', 'Plane of Mischief'}
LUCLIN_ZONES = {'The Nexus', 'Nexus', 'The Bazaar', 'Shadow Haven', 'The Maiden\'s Eye', 'The Umbral Plains', 'Ssraeshza Temple', 'Vex Thal', 'The Fungus Grove', 'The Twilight Sea', 'Sanctus Seru', 'The Dawnshroud Peaks', 'Akheva Ruins'}

PINNACLES = {
    "Classic": ["Lord Nagafen", "Lady Vox"],
    "Kunark": ["Phara Dar"],
    "Velious": ["Tunare", "Vulak`Aerr", "The Avatar of War"],
    "Luclin": ["Aten Ha Ra"],
    "Planes of Power": ["Quarm"]
}

TIME_FORMAT = "%a %b %d %H:%M:%S %Y"

def normalize_boss_name(name: str) -> str:
    n = name.strip()
    n = n.replace("`", "'")
    if n.lower().startswith("the "):
        n = n[4:]
    return n.lower()

NORM_PINNACLES = {}
for era, plist in PINNACLES.items():
    for p in plist:
        NORM_PINNACLES[normalize_boss_name(p)] = p

EQ_CLASSES = {
    1: "Warrior", 2: "Cleric", 3: "Paladin", 4: "Ranger",
    5: "Shadow Knight", 6: "Druid", 7: "Monk", 8: "Bard",
    9: "Rogue", 10: "Shaman", 11: "Necromancer", 12: "Wizard",
    13: "Magician", 14: "Enchanter", 15: "Beastlord"
}

EQ_RACES = {
    1: "Human", 2: "Barbarian", 3: "Erudite", 4: "Wood Elf",
    5: "High Elf", 6: "Dark Elf", 7: "Half Elf", 8: "Dwarf",
    9: "Troll", 10: "Ogre", 11: "Halfling", 12: "Gnome",
    128: "Iksar", 130: "Vah Shir"
}

def load_quarmy_info(character_name: str, log_dir: str = r"C:\TAKPv22") -> Dict[str, Any]:
    # Quarmy dump files are unavailable for most players; rely purely on client logs
    return {}

def analyze_character(character_name: str, log_dir: str = r"C:\TAKPv22"):
    print(f"\n=======================================================")
    print(f"Starting Comprehensive Analysis for: {character_name}")
    print(f"=======================================================")
    
    quarmy_data = load_quarmy_info(character_name, log_dir)

    npc_db = NPCDatabase()
    stitcher = LogStitcher(log_dir, character_name)
    file_summary = stitcher.get_summary()
    print(f"Discovered {len(file_summary)} log file(s):")
    for fs in file_summary:
        print(f"  • {fs['file']} ({fs['size_mb']} MB) [{fs['start']} -> {fs['end']}]")

    current_zone = "Unknown"
    first_ts = None
    last_ts = None
    total_lines = 0

    zone_entries = Counter()
    zone_deaths = Counter()
    zone_aas = Counter()

    level_timeline = []
    seen_levels = set()
    aa_events = []
    deaths = []
    death_killers = Counter()
    environmental_deaths = 0
    rez_count = 0
    npcs_slain = Counter()

    guild_history = []

    tells_sent = Counter()
    tells_recv = Counter()
    known_npc_senders = set()
    spells_cast = Counter()
    songs_memorized = Counter()
    
    # Bard specific twisting metrics
    bard_selo_pulses = 0
    bard_songs_ended = 0
    bard_missed_notes = 0

    # Martial & Feign Death metrics
    monk_kicks = 0
    mend_successes = 0
    mend_failures = 0
    bind_wounds_count = 0
    fd_failed_or_broken = 0
    deaths_after_failed_fd = 0
    last_failed_fd_dt = None

    group_companions = Counter()
    raid_companions = Counter()
    looters = Counter()

    who_class_votes = Counter()
    who_race_votes = Counter()
    who_max_level = 0

    lockouts = []
    all_guild_kills = []
    local_slays = []
    raw_boss_events = []

    expansion_firsts = {
        "Kunark": None,
        "Velious": None,
        "Luclin": None
    }

    epic_quest_event = None
    candidate_epics = {}

    # Load Epics reference
    epics_ref_path = os.path.join(PROJECT_ROOT, "data", "reference", "epics.json")
    epics_ref = {}
    if os.path.exists(epics_ref_path):
        with open(epics_ref_path, "r", encoding="utf-8") as f:
            epics_ref = json.load(f)

    # Load Class AAs reference
    class_aas_ref_path = os.path.join(PROJECT_ROOT, "data", "reference", "class_aas.json")
    if not os.path.exists(class_aas_ref_path):
        class_aas_ref_path = os.path.join(PROJECT_ROOT, "src", "data", "class_aas.json")
    class_aas_ref = {}
    if os.path.exists(class_aas_ref_path):
        with open(class_aas_ref_path, "r", encoding="utf-8") as f:
            class_aas_ref = json.load(f)

    class_aa_events = []

    print("Streaming log lines (this may take a few moments for multi-GB logs)...")
    for line in stitcher.stream_lines():
        total_lines += 1
        m = TS_PATTERN.match(line)
        if not m:
            continue
        ts, msg = m.group("ts"), m.group("msg")
        try:
            dt = datetime.strptime(ts, TIME_FORMAT)
        except ValueError:
            dt = None
        if first_ts is None:
            first_ts = ts
        last_ts = ts

        # Zone tracking
        if msg.startswith("You have entered "):
            zm = ZONE_PATTERN.match(msg)
            if zm:
                zname = zm.group(1).strip()
                # Ignore PvP flag sub-area messages (e.g. "an Arena (PvP) area" in PvP raid instances)
                if "arena (pvp) area" in zname.lower():
                    continue
                current_zone = zname
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

        # /who inspection
        if msg.startswith("[") and not (msg.startswith("[Group]") or msg.startswith("[Raid]") or msg.startswith("[Guild]") or msg.startswith("[Tell]") or msg.startswith("[PVP]")):
            wm = WHO_ENTRY_PATTERN.match(msg)
            if wm:
                first = (wm.group("first") or "").lower()
                title = (wm.group("title") or "").lower()
                char_lower = character_name.lower()
                if first == char_lower or title == char_lower:
                    raw_cls = wm.group("cls").strip()
                    if raw_cls.lower() == "shadowknight":
                        raw_cls = "Shadow Knight"
                    who_class_votes[raw_cls] += 1
                    try:
                        who_max_level = max(who_max_level, int(wm.group("lvl")))
                    except ValueError:
                        pass
                    r = wm.group("race")
                    if r and r.lower() != "unknown":
                        who_race_votes[r.strip()] += 1
            else:
                am = WHO_ANON_PATTERN.match(msg)
                if am:
                    first = (am.group("first") or "").lower()
                    title = (am.group("title") or "").lower()
                    char_lower = character_name.lower()
                    if first == char_lower or title == char_lower:
                        r = am.group("race")
                        if r and r.lower() != "unknown":
                            who_race_votes[r.strip()] += 1

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

        # Class AA Learning & Improvement
        if msg.startswith('You have gained the ability "') or msg.startswith('You have improved '):
            if msg.startswith('You have gained the ability "'):
                gm = AA_GAIN_PATTERN.match(msg)
                if gm:
                    raw_name = gm.group("name").strip()
                    cost = int(gm.group("cost"))
                    rank = 1
                    aa_info = class_aas_ref.get(raw_name.lower())
                    if aa_info:
                        class_aa_events.append({
                            "timestamp": ts,
                            "date": dt.strftime("%Y-%m-%d") if dt else "",
                            "ability": aa_info["name"],
                            "rank": rank,
                            "cost": cost,
                            "category": aa_info["category"],
                            "classes": aa_info["classes"],
                            "description": aa_info["description"],
                            "zone": current_zone
                        })
            else:
                im = AA_IMPROVE_PATTERN.match(msg)
                if im:
                    raw_name = im.group("name").strip()
                    cost = int(im.group("cost"))
                    rank = int(im.group("rank")) if im.group("rank") else 2
                    aa_info = class_aas_ref.get(raw_name.lower())
                    if aa_info:
                        class_aa_events.append({
                            "timestamp": ts,
                            "date": dt.strftime("%Y-%m-%d") if dt else "",
                            "ability": aa_info["name"],
                            "rank": rank,
                            "cost": cost,
                            "category": aa_info["category"],
                            "classes": aa_info["classes"],
                            "description": aa_info["description"],
                            "zone": current_zone
                        })
            continue

        # Resurrections
        if REZ_PATTERN.search(msg):
            rez_count += 1
            continue

        # NPCs slain
        if msg.startswith("You have slain "):
            sm = YOU_SLAIN_PATTERN.match(msg)
            if sm:
                npcs_slain[sm.group(1).strip()] += 1
            continue

        # Deaths & Nemesis
        if msg.startswith("You have been slain by ") or msg == "You died.":
            if last_failed_fd_dt and dt:
                diff = (dt - last_failed_fd_dt).total_seconds()
                if 0 <= diff <= 30:
                    deaths_after_failed_fd += 1
                last_failed_fd_dt = None
            if msg.startswith("You have been slain by "):
                dsm = DEATH_SLAIN.match(msg)
                killer = dsm.group(1).strip() if dsm else "Unknown"
            else:
                killer = "Bleeding Out / Environmental / Gravity"
                environmental_deaths += 1
            zone_deaths[current_zone] += 1
            deaths.append({"timestamp": ts, "killer": killer, "zone": current_zone})
            death_killers[killer] += 1
            continue

        # Lockouts
        if msg.startswith("You have incurred a lockout for "):
            lm = LOCKOUT_PATTERN.match(msg)
            if lm:
                boss_name = lm.group("boss").strip()
                lockouts.append({"timestamp": ts, "boss": boss_name, "zone": current_zone})
                if dt:
                    raw_boss_events.append((dt, boss_name, "lockout", ts, current_zone))
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
                if dt:
                    raw_boss_events.append((dt, boss_name, "guild_kill", ts, gkm.group("zone").strip() or current_zone))
            continue

        # Local slays
        if " has been slain by " in msg:
            lsm = LOCAL_SLAY.match(msg)
            if lsm:
                target = lsm.group("target").strip()
                norm_target = normalize_boss_name(target)
                if norm_target in NORM_PINNACLES or "vulak" in norm_target:
                    local_slays.append({"timestamp": ts, "boss": target, "killer": lsm.group("killer"), "zone": current_zone})
                    if dt:
                        raw_boss_events.append((dt, target, "local_slay", ts, current_zone))
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
                sender = tm.group(1).strip()
                text = tm.group(2).strip()
                if is_npc_tell(sender, text):
                    known_npc_senders.add(sender.lower())
                else:
                    tells_recv[sender] += 1
            continue

        # Spells / Songs
        if msg.startswith("You begin "):
            cm = CAST_PATTERN.match(msg)
            if cm:
                spells_cast[cm.group(1)] += 1
            continue
        elif msg.startswith("You have finished memorizing "):
            mm = MEM_PATTERN.match(msg)
            if mm:
                songs_memorized[mm.group(1).strip()] += 1
            continue

        # Bard specific lines
        if msg == "Your feet move faster.":
            bard_selo_pulses += 1
            spells_cast["Selo's Accelerating Chorus"] += 1
            continue
        elif msg == "Your song ends.":
            bard_songs_ended += 1
            continue
        elif msg == "You miss a note, bringing your song to a close!":
            bard_missed_notes += 1
            continue
        elif "damage from your " in msg:
            bdm = BARD_DAMAGE_PATTERN.search(msg)
            if bdm:
                s_name = bdm.group(1).replace("`", "'").strip()
                spells_cast[s_name] += 1
                continue

        # Disciplines
        disc_name = DISC_ACTIVATIONS.get(msg)
        if disc_name:
            spells_cast[disc_name] += 1
            continue

        # Bandaging
        if msg == "The bandaging is complete.":
            bind_wounds_count += 1
            spells_cast["Bind Wound"] += 1
            continue

        # Mend
        if "You mend your wounds and heal some damage" in msg:
            mend_successes += 1
            spells_cast["Mend"] += 1
            continue
        elif "You have worsened your wounds!" in msg or "You have failed to mend your wounds" in msg:
            mend_failures += 1
            continue

        # Feign Death Fail / Spell Broken
        if msg == "You are no longer feigning death, because a spell hit you.":
            fd_failed_or_broken += 1
            last_failed_fd_dt = dt
            continue

        fdm = FD_FALL_PATTERN.match(msg)
        if fdm and fdm.group(1).lower() == character_name.lower():
            fd_failed_or_broken += 1
            last_failed_fd_dt = dt
            continue

        # Kicks & Martial Arts
        if KICK_HIT_PATTERN.match(msg):
            monk_kicks += 1
            skill = "Flying Kick" if msg.lower().startswith("you flying kick") else ("Round Kick" if msg.lower().startswith("you round kick") else "Kick")
            spells_cast[skill] += 1
        elif MARTIAL_HIT_PATTERN.match(msg):
            skill = "Dragon Punch" if msg.lower().startswith("you dragon punch") else ("Tail Rake" if msg.lower().startswith("you tail rake") else ("Tiger Claw" if msg.lower().startswith("you tiger claw") else "Eagle Strike"))
            spells_cast[skill] += 1
        elif BACKSTAB_HIT_PATTERN.match(msg):
            spells_cast["Backstab"] += 1

        # Group & Raid Chat Companions
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

        # Epic Quest detection in log
        for cls_name, edata in epics_ref.items():
            if cls_name not in candidate_epics:
                if edata["weapon"].lower() in msg.lower():
                    # Look for player acquisition or guild announcement
                    if "You say to your guild" in msg or "you have looted" in msg.lower() or "worthy" in msg.lower() or "primary:" in msg.lower():
                        candidate_epics[cls_name] = {
                            "name": edata["weapon"],
                            "class": f"{cls_name} Epic 1.0",
                            "effect": edata["effect"],
                            "timestamp": ts,
                            "zone": current_zone
                        }

    # Fallback: check inventory for Epic 1.0 if not captured in log text
    if not epic_quest_event:
        for item in quarmy_data.get("equipped", []):
            for cls_name, edata in epics_ref.items():
                if item["name"].lower() == edata["weapon"].lower():
                    epic_quest_event = {
                        "name": edata["weapon"],
                        "class": f"{cls_name} Epic 1.0",
                        "effect": edata["effect"],
                        "timestamp": "Inventory Confirmed",
                        "zone": "Project Quarm"
                    }
                    break
            if epic_quest_event:
                break

    # Resolve NPCs with NPCDatabase (linking to pqdi.cc)
    resolved_top_slain = []
    for npc_name, count in npcs_slain.most_common(10):
        resolved = npc_db.resolve(npc_name, current_zone=None)
        resolved_top_slain.append({
            "name": npc_name,
            "count": count,
            "id": resolved["id"] if resolved else None,
            "level": resolved.get("level") if resolved else None,
            "hp": resolved.get("hp") if resolved else None,
            "url": resolved["url"] if resolved else None,
            "zone": resolved.get("zone_long") if resolved else None
        })

    # Separate PvP vs PvE Nemesis
    pve_nemesis_raw = []
    pvp_nemesis_raw = []
    for killer, count in death_killers.most_common(20):
        if killer == "Bleeding Out / Environmental / Gravity":
            continue
        res = npc_db.resolve(killer)
        if res:
            pve_nemesis_raw.append({
                "name": killer,
                "count": count,
                "id": res["id"],
                "level": res.get("level"),
                "zone": res.get("zone_long"),
                "url": res["url"]
            })
        else:
            pvp_nemesis_raw.append({"name": killer, "count": count})

    # Deduplicate and cluster raw boss events into distinct kill occurrences
    # Any signals for the same canonical boss within 10 minutes (600s) are merged
    raw_boss_events.sort(key=lambda x: x[0])
    clustered_kills = []
    
    for dt, b_raw, source, ts_str, ev_zone in raw_boss_events:
        norm_b = normalize_boss_name(b_raw)
        canonical_pinnacle = NORM_PINNACLES.get(norm_b)
        if not canonical_pinnacle:
            if "herald of vulak" in norm_b or norm_b == "vulak'aerr":
                canonical_pinnacle = "Vulak`Aerr"
        
        boss_key = canonical_pinnacle if canonical_pinnacle else b_raw
        
        merged = False
        for i in range(len(clustered_kills) - 1, -1, -1):
            c_dt, c_boss, c_ts, c_sources, c_zone = clustered_kills[i]
            if abs((dt - c_dt).total_seconds()) <= 600:
                if normalize_boss_name(c_boss) == normalize_boss_name(boss_key):
                    c_sources.add(source)
                    merged = True
                    break
            else:
                if (dt - c_dt).total_seconds() > 600:
                    break
        
        if not merged:
            clustered_kills.append((dt, boss_key, ts_str, {source}, ev_zone))

    pinnacle_first_kills = {}
    pinnacle_total_kills = Counter()
    all_boss_kills = Counter()
    
    for dt, boss_name, ts_str, sources, ev_zone in clustered_kills:
        all_boss_kills[boss_name] += 1
        norm_b = normalize_boss_name(boss_name)
        canon = NORM_PINNACLES.get(norm_b)
        if canon:
            pinnacle_total_kills[canon] += 1
            if canon not in pinnacle_first_kills:
                pinnacle_first_kills[canon] = ts_str

    # Format Pinnacle Boss stats
    pinnacle_stats = {}
    for era, plist in PINNACLES.items():
        pinnacle_stats[era] = []
        for pb in plist:
            res = npc_db.resolve(pb)
            pinnacle_stats[era].append({
                "boss": pb,
                "id": res["id"] if res else None,
                "url": res["url"] if res else None,
                "first_kill": pinnacle_first_kills.get(pb, None),
                "total_kills_or_lockouts": pinnacle_total_kills.get(pb, 0)
            })

    # Infer class: Tier 1 (/who votes), Tier 2 (Quarmy metadata), Tier 3 (Spells)
    char_class = None
    if who_class_votes:
        char_class = who_class_votes.most_common(1)[0][0]
    if not char_class:
        char_class = quarmy_data.get("class")
    if not char_class:
        if bard_songs_ended > 0 or bard_selo_pulses > 0:
            char_class = "Bard"
        elif spells_cast.get("Complete Healing", 0) > 10:
            char_class = "Cleric"
        elif spells_cast.get("Sedulous Subversion", 0) > 0 or spells_cast.get("Splurt", 0) > 0 or spells_cast.get("Dooming Darkness", 0) > 0:
            char_class = "Necromancer"
        elif spells_cast.get("Boltran's Agacerie", 0) > 0 or spells_cast.get("Clarity II", 0) > 0:
            char_class = "Enchanter"
        elif monk_kicks > 5 or mend_successes > 0 or mend_failures > 0:
            char_class = "Monk"
        elif spells_cast.get("Backstab", 0) > 0:
            char_class = "Rogue"
        elif spells_cast.get("Defensive Discipline", 0) > 0 or spells_cast.get("Taunt", 0) > 0:
            char_class = "Warrior"
        else:
            char_class = "Adventurer"

    if not epic_quest_event:
        epic_quest_event = candidate_epics.get(char_class)
        if not epic_quest_event and len(candidate_epics) == 1:
            epic_quest_event = list(candidate_epics.values())[0]

    char_race = who_race_votes.most_common(1)[0][0] if who_race_votes else quarmy_data.get("race")

    result = {
        "character": character_name,
        "last_name": quarmy_data.get("last_name"),
        "character_class": char_class,
        "character_race": char_race,
        "date_range": {"first": first_ts, "last": last_ts},
        "total_log_lines": total_lines,
        "guild_history": guild_history,
        "expansion_firsts": expansion_firsts,
        "epic_quest": epic_quest_event,
        "equipped_gear": quarmy_data.get("equipped", []),
        "pinnacle_bosses": pinnacle_stats,
        "stats": {
            "total_deaths": len(deaths),
            "resurrections_accepted": rez_count,
            "environmental_or_bleeding_deaths": environmental_deaths,
            "total_level_dings": len(level_timeline),
            "max_level": quarmy_data.get("level") or max((x["level"] for x in level_timeline), default=60),
            "total_aas_earned": len(aa_events),
            "total_lockouts": len(lockouts),
            "total_guild_kill_announcements": len(all_guild_kills),
            "top_zones_by_entries": zone_entries.most_common(10),
            "top_zones_by_deaths": zone_deaths.most_common(10),
            "top_zones_by_aas": zone_aas.most_common(10),
            "top_npcs_slain": resolved_top_slain,
            "pvp_nemesis": pvp_nemesis_raw[:5],
            "top_pve_nemesis": pve_nemesis_raw[:5],
            "top_tell_recipients": [(p, c) for p, c in tells_sent.most_common(25) if p.lower() not in known_npc_senders and " " not in p and not p[0].islower()][:10],
            "top_tell_senders": [(p, c) for p, c in tells_recv.most_common(25) if p.lower() not in known_npc_senders and " " not in p and not p[0].islower()][:10],
            "top_group_companions": group_companions.most_common(10),
            "top_raid_companions": raid_companions.most_common(10),
            "top_looters_seen": looters.most_common(10),
            "top_spells_or_songs": spells_cast.most_common(15),
            "top_songs_memorized": songs_memorized.most_common(15),
            "bard_twisting": {
                "selo_pulses": bard_selo_pulses,
                "songs_completed": bard_songs_ended,
                "missed_notes": bard_missed_notes
            },
            "cleric_stats": {
                "complete_healing_casts": spells_cast.get("Complete Healing", 0),
                "rezzes_cast": (spells_cast.get("Reviviscence", 0) + 
                                spells_cast.get("Resurrection", 0) + 
                                spells_cast.get("Restoration", 0) + 
                                spells_cast.get("Resuscitate", 0)),
                "divine_intervention_casts": spells_cast.get("Divine Intervention", 0),
                "group_heals": (spells_cast.get("Word of Redemption", 0) + 
                                spells_cast.get("Word of Restoration", 0) + 
                                spells_cast.get("Word of Divine", 0)),
                "aegolism_casts": spells_cast.get("Aegolism", 0),
                "heroic_bond_casts": spells_cast.get("Heroic Bond", 0)
            },
            "necro_stats": {
                "twitch_casts": (spells_cast.get("Sedulous Subversion", 0) + 
                                 spells_cast.get("Covetous Subversion", 0) + 
                                 spells_cast.get("Rapacious Subversion", 0)),
                "dots_cast": (spells_cast.get("Splurt", 0) + 
                              spells_cast.get("Ignite Blood", 0) + 
                              spells_cast.get("Pyrocruor", 0) + 
                              spells_cast.get("Defiance", 0) + 
                              spells_cast.get("Boil Blood", 0) + 
                              spells_cast.get("Funeral Pyre of Kelador", 0) + 
                              spells_cast.get("Cascading Darkness", 0) + 
                              spells_cast.get("Cessation of Cor", 0)),
                "lifetaps_cast": (spells_cast.get("Drain Soul", 0) + 
                                  spells_cast.get("Drain Spirit", 0) + 
                                  spells_cast.get("Siphon Life", 0)),
                "feign_death_casts": spells_cast.get("Feign Death", 0),
                "pet_summons": (spells_cast.get("Emissary of Thule", 0) + 
                                spells_cast.get("Minion of Shadows", 0) + 
                                spells_cast.get("Servant of Bones", 0)),
                "rezzes_cast": spells_cast.get("Convergence", 0)
            },
            "monk_stats": {
                "kicks_landed": monk_kicks,
                "mend_successes": mend_successes,
                "mend_failures": mend_failures,
                "bandages_completed": bind_wounds_count,
                "fd_failed_or_broken": fd_failed_or_broken,
                "deaths_after_failed_fd": deaths_after_failed_fd
            },
            "top_raid_boss_kills_overall": all_boss_kills.most_common(15)
        },
        "level_timeline_firsts": [x for x in level_timeline if x["first_time"]],
        "aa_events": aa_events,
        "class_aa_milestones": class_aa_events
    }

    out_path = os.path.join(PROJECT_ROOT, "data", "sample_output", f"{character_name.lower()}_summary.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\n[DONE] Summary written to {out_path}!")

    # Print summary highlights to stdout
    print(f"\n==================== HIGHLIGHTS FOR {character_name.upper()} ====================")
    print(f"Date Range: {first_ts} -> {last_ts} ({total_lines:,} lines)")
    print(f"Guild History ({len(guild_history)}): {guild_history}")
    print(f"Max Level: {result['stats']['max_level']} ({len(level_timeline)} dings recorded)")
    print(f"Total AAs: {len(aa_events)} across zones: {zone_aas.most_common(5)}")
    print(f"Total Deaths: {len(deaths)} (Rezzes Accepted: {rez_count:,}, Bleeding/Gravity: {environmental_deaths})")
    print(f"Top 3 PvE Nemesis: {[x['name'] + ' (' + str(x['count']) + ')' for x in pve_nemesis_raw[:3]]}")
    print(f"Top 3 PvP Nemesis: {[x['name'] + ' (' + str(x['count']) + ')' for x in pvp_nemesis_raw[:3]]}")
    print(f"Bard Twisting: {bard_songs_ended:,} songs completed, {bard_selo_pulses:,} Selo pulses, {bard_missed_notes:,} missed notes")
    print(f"Top 5 Entered Zones: {zone_entries.most_common(5)}")
    print(f"Epic Milestone: {epic_quest_event}")
    print(f"Pinnacle Bosses Defeated:")
    for era, blist in pinnacle_stats.items():
        for b in blist:
            if b["total_kills_or_lockouts"] > 0:
                print(f"  [{era}] {b['boss']}: First={b['first_kill']}, Total={b['total_kills_or_lockouts']} (URL: {b['url']})")

    return result

if __name__ == "__main__":
    target_char = sys.argv[1] if len(sys.argv) > 1 else "Steps"
    analyze_character(target_char)
