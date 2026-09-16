import re
from datetime import datetime

LOG_FILE = r"C:\TAKPv22\eqlog_Tweedlede_pq.proj.txt"
TS_RE = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<msg>.*)$")

ZONE_RE = re.compile(r"^You have entered ([^\.]+)\.", re.I)
LOCKOUT_RE = re.compile(r"^You have incurred a lockout for (?P<boss>.+?) that expires in", re.I)
LOCAL_SLAY_RE = re.compile(r"^(?P<target>.+?) has been slain by (?P<killer>.+?)!", re.I)
GUILD_KILL_RE = re.compile(r"^Druzzil Ro tells the guild, '(?P<player>.+?) of (?P<guild>.+?)> has killed (?P<boss>.+?) in (?P<zone>.+?)!'", re.I)
PVP_KILL_RE = re.compile(r"(?:PVP Druzzil Ro BROADCASTS|\[PVP\]).*? has killed (?P<boss>.+?) in (?P<zone>.+?)!", re.I)

# Normalization of zone names
def norm_zone(z):
    if not z:
        return ""
    z = z.lower().replace(" (instanced)", "").replace(" instanced", "").replace("the ", "").strip()
    return z

def test_raid_involvement():
    current_zone = "Unknown"
    
    # Track events
    lockouts = [] # (ts, boss, zone)
    local_slays = [] # (ts, boss, killer, zone)
    guild_kills = [] # (ts, player, guild, boss, zone, attended)
    
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = TS_RE.match(line)
            if not m:
                continue
            ts, msg = m.group("ts"), m.group("msg")
            
            # Zone check
            if msg.startswith("You have entered "):
                zm = ZONE_RE.match(msg)
                if zm:
                    current_zone = zm.group(1).strip()
                continue
                
            # Lockout check
            if "You have incurred a lockout for " in msg:
                lm = LOCKOUT_RE.match(msg)
                if lm:
                    lockouts.append((ts, lm.group("boss"), current_zone))
                continue
                
            # Guild kill check
            if "Druzzil Ro tells the guild, " in msg:
                gm = GUILD_KILL_RE.match(msg)
                if gm:
                    target_zone = gm.group("zone").strip()
                    attended = norm_zone(current_zone) in norm_zone(target_zone) or norm_zone(target_zone) in norm_zone(current_zone)
                    guild_kills.append({
                        "ts": ts,
                        "player": gm.group("player"),
                        "boss": gm.group("boss"),
                        "zone": target_zone,
                        "player_zone": current_zone,
                        "attended": attended
                    })
                continue
                
            # Local slay check
            if " has been slain by " in msg:
                sm = LOCAL_SLAY_RE.match(msg)
                if sm:
                    local_slays.append((ts, sm.group("target"), sm.group("killer"), current_zone))

    print(f"Total Lockouts Received: {len(lockouts)}")
    unique_lockout_bosses = set(b for _, b, _ in lockouts)
    print(f"Unique Lockout Bosses ({len(unique_lockout_bosses)}): {unique_lockout_bosses}")

    attended_guild_kills = [k for k in guild_kills if k["attended"]]
    unattended_guild_kills = [k for k in guild_kills if not k["attended"]]
    print(f"\nGuild Kills Total: {len(guild_kills)}")
    print(f"  Attended (In Same Zone): {len(attended_guild_kills)}")
    print(f"  Unattended (Remote in {set(k['player_zone'] for k in unattended_guild_kills)}): {len(unattended_guild_kills)}")

    print("\nSample Attended Guild Kills:")
    for k in attended_guild_kills[:10]:
        print(f"  [{k['ts']}] {k['boss']} in {k['zone']} (Player was in {k['player_zone']})")

if __name__ == "__main__":
    test_raid_involvement()
