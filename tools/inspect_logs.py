import os
import re
import sys
from collections import Counter
from datetime import datetime

LOG_DIR = r"C:\TAKPv22"
CHARACTERS = ["Steps", "Thebrain", "Tweedlede", "Zondro"]

# Regex patterns
TIMESTAMP_PATTERN = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<msg>.*)$")
LEVEL_PATTERN = re.compile(r"Welcome to level (\d+)!", re.IGNORECASE)
DEATH_PATTERN = re.compile(r"(You have been slain by|You died)", re.IGNORECASE)
TELL_SENT = re.compile(r"^You told ([A-Za-z]+),\s*'(.*)'", re.IGNORECASE)
TELL_RECV = re.compile(r"^([A-Za-z]+) tells you,\s*'(.*)'", re.IGNORECASE)
SLAY_PATTERN = re.compile(r"You have slain ([^!]+)!", re.IGNORECASE)
ZONE_PATTERN = re.compile(r"You have entered ([^\.]+)\.", re.IGNORECASE)
CAST_PATTERN = re.compile(r"You begin (?:casting|singing) (.*?)\.", re.IGNORECASE)
VENDOR_BUY = re.compile(r"tells you, 'That'll be (.*?) for (?:the )?(.*?)\.'", re.IGNORECASE)

def inspect_character(char_name):
    log_file = os.path.join(LOG_DIR, f"eqlog_{char_name}_pq.proj.txt")
    if not os.path.exists(log_file):
        print(f"Log file not found for {char_name}: {log_file}")
        return

    size_mb = os.path.getsize(log_file) / (1024 * 1024)
    print(f"\n==========================================")
    print(f"Character: {char_name} ({size_mb:.1f} MB)")
    print(f"File: {log_file}")
    print(f"==========================================")

    first_ts = None
    last_ts = None
    total_lines = 0

    levels_seen = []
    deaths = 0
    tells_sent_to = Counter()
    tells_recv_from = Counter()
    zones_visited = Counter()
    spells_cast = Counter()
    vendor_buys = Counter()

    # Stream line by line
    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            total_lines += 1
            m = TIMESTAMP_PATTERN.match(line)
            if not m:
                continue
            ts_str, msg = m.group("ts"), m.group("msg")
            if first_ts is None:
                first_ts = ts_str
            last_ts = ts_str

            # Dings
            lvl_m = LEVEL_PATTERN.search(msg)
            if lvl_m:
                levels_seen.append((ts_str, int(lvl_m.group(1))))

            # Deaths
            if DEATH_PATTERN.search(msg):
                deaths += 1

            # Tells
            t_sent = TELL_SENT.match(msg)
            if t_sent:
                tells_sent_to[t_sent.group(1)] += 1

            t_recv = TELL_RECV.match(msg)
            if t_recv:
                sender = t_recv.group(1)
                if not sender.lower().endswith("merchant"):
                    tells_recv_from[sender] += 1

            # Spells / Songs
            cm = CAST_PATTERN.search(msg)
            if cm:
                spells_cast[cm.group(1)] += 1

            # Vendor purchases
            vm = VENDOR_BUY.search(msg)
            if vm:
                vendor_buys[vm.group(2)] += 1

            # Zones
            zm = ZONE_PATTERN.search(msg)
            if zm:
                zones_visited[zm.group(1)] += 1

    print(f"Date Range: {first_ts} -> {last_ts}")
    print(f"Total Lines: {total_lines:,}")
    if levels_seen:
        print(f"Level Milestones ({len(levels_seen)}): min={min(lvl for _, lvl in levels_seen)}, max={max(lvl for _, lvl in levels_seen)}")
    else:
        print("Level Milestones: None in this log file (likely started at level 50/60)")
    print(f"Total Deaths: {deaths:,}")
    print(f"Top 5 Outgoing Tell Recipients: {tells_sent_to.most_common(5)}")
    print(f"Top 5 Incoming Tell Senders: {tells_recv_from.most_common(5)}")
    print(f"Top 5 Spells/Songs: {spells_cast.most_common(5)}")
    print(f"Top 5 Most Entered Zones: {zones_visited.most_common(5)}")

if __name__ == "__main__":
    for c in CHARACTERS:
        inspect_character(c)
