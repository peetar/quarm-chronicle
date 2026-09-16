import re

LOG_FILE = r"C:\TAKPv22\eqlog_Tweedlede_pq.proj.txt"

def test():
    aa_lines = []
    guild_lines = []
    lockout_lines = []
    raid_exp_lines = []
    guild_kill_lines = []
    
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "gained an ability point" in line:
                aa_lines.append(line.strip())
            if "You have joined " in line or "You are no longer a member of " in line:
                guild_lines.append(line.strip())
            if "You have incurred a lockout" in line:
                lockout_lines.append(line.strip())
            if "You gained raid experience" in line:
                raid_exp_lines.append(line.strip())
            if "Druzzil Ro tells the guild" in line:
                guild_kill_lines.append(line.strip())

    print(f"Total AA lines found: {len(aa_lines)}")
    if aa_lines:
        print("Sample AA lines:")
        for l in aa_lines[:5]:
            print("  ", l)
        print("Last 3 AA lines:")
        for l in aa_lines[-3:]:
            print("  ", l)

    print(f"\nGuild history lines ({len(guild_lines)}):")
    for l in guild_lines:
        print("  ", l)

    print(f"\nLockouts ({len(lockout_lines)}):")
    for l in lockout_lines[:5]:
        print("  ", l)

    print(f"\nRaid Exp count: {len(raid_exp_lines)}")
    print(f"Guild Kill announcements count: {len(guild_kill_lines)}")
    if guild_kill_lines:
        for l in guild_kill_lines[:5]:
            print("  ", l)

if __name__ == "__main__":
    test()
