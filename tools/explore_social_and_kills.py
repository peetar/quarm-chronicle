import os
import re
from collections import Counter

LOG_FILE = r"C:\TAKPv22\eqlog_Tweedlede_pq.proj.txt"
TS_RE = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<msg>.*)$")

# Patterns
REZ_PATTERN = re.compile(r"You regain some experience from resurrection", re.I)
YOU_SLAIN_PATTERN = re.compile(r"^You have slain (?:an? )?([^!]+)!", re.I)
DEATH_BY_PATTERN = re.compile(r"^You have been slain by ([^!]+)!", re.I)

# Group / Raid communication
GROUP_TELL = re.compile(r"^([A-Za-z]+) tells the group,\s*'(.*)'", re.I)
RAID_TELL = re.compile(r"^([A-Za-z]+) tells the raid,\s*'(.*)'", re.I)
GROUP_CHAT = re.compile(r"^\[Group\]\s*([A-Za-z]+):\s*(.*)", re.I)
RAID_CHAT = re.compile(r"^\[Raid\]\s*([A-Za-z]+):\s*(.*)", re.I)
LOOT_PATTERN = re.compile(r"^--([A-Za-z]+) has looted a (.*)\.--", re.I)

def test_explorations():
    rez_count = 0
    mobs_slain = Counter()
    death_killers = Counter()
    
    group_members = Counter()
    raid_members = Counter()
    looters = Counter()

    print(f"Scanning {LOG_FILE} for new stats...")
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = TS_RE.match(line)
            if not m:
                continue
            ts, msg = m.group("ts"), m.group("msg")

            # 1. Resurrections
            if REZ_PATTERN.search(msg):
                rez_count += 1
                continue

            # 2. Top NPCs Slain by Player
            if msg.startswith("You have slain "):
                sm = YOU_SLAIN_PATTERN.match(msg)
                if sm:
                    mobs_slain[sm.group(1).strip()] += 1
                continue

            # 3. Nemesis (Who killed player most)
            if msg.startswith("You have been slain by "):
                dm = DEATH_BY_PATTERN.match(msg)
                if dm:
                    death_killers[dm.group(1).strip()] += 1
                continue

            # 4. Group / Raid companions
            gt = GROUP_TELL.match(msg) or GROUP_CHAT.match(msg)
            if gt:
                speaker = gt.group(1)
                if speaker.lower() != "you":
                    group_members[speaker] += 1
                continue

            rt = RAID_TELL.match(msg) or RAID_CHAT.match(msg)
            if rt:
                speaker = rt.group(1)
                if speaker.lower() != "you":
                    raid_members[speaker] += 1
                continue

            lt = LOOT_PATTERN.match(msg)
            if lt:
                looter = lt.group(1)
                if looter.lower() != "you":
                    looters[looter] += 1
                continue

    print(f"\n1. Resurrections Accepted: {rez_count}")
    print(f"\n2. Top 10 Nemesis (Entities that killed Tweedlede most):")
    for k, c in death_killers.most_common(10):
        print(f"   {k}: {c} times")

    print(f"\n3. Top 10 NPCs Personally Slain by Tweedlede:")
    for m, c in mobs_slain.most_common(10):
        print(f"   {m}: {c} kills")

    print(f"\n4. Top 10 Group Chat Companions:")
    for p, c in group_members.most_common(10):
        print(f"   {p}: {c} group messages")

    print(f"\n5. Top 10 Raid Chat Companions:")
    for p, c in raid_members.most_common(10):
        print(f"   {p}: {c} raid messages")

    print(f"\n6. Top 10 Raid Looters Seen:")
    for p, c in looters.most_common(10):
        print(f"   {p}: {c} items looted")

if __name__ == "__main__":
    test_explorations()
