# EverQuest TAKP / Project Quarm Log Specification

## Timestamp Format

EverQuest logs on Project Quarm (TAKP client) prepend standard timestamps to every entry:
```
[Day Mon DD HH:MM:SS YYYY] Message text
```
Examples:
- `[Sat Jul 06 10:11:41 2024] You have entered West Freeport.`
- `[Sat Jul 06 10:12:22 2024] You have slain a decaying skeleton!`
- `[Sat Jul 06 10:12:25 2024] Steps saved.`

Regex pattern:
```python
r'^\[(?P<timestamp>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\] (?P<text>.*)$'
```

## Common Event Patterns

### 1. Level Progression & Dings
- `You have gained a level! Welcome to level (?P<level>\d+)!`
- Project Quarm New Game Plus (NG+): Custom server broadcast/messages when prestige/reset occurs.

### 2. Combat Kills & Bosses
- Personal kill: `You have slain (?P<target>.*)!`
- Group/Raid kill: `(?P<target>.*) has been slain by (?P<killer>.*)!`
- Deaths: `You have been slain by (?P<killer>.*)!` or `You died.`

### 3. Social & Tells
- Outgoing tell: `You told (?P<recipient>.*?): '(?P<message>.*)'`
- Incoming tell: `(?P<sender>.*?) told you, '(?P<message>.*)'`
- Guild chat: `\[(?P<channel>Guild)\] (?P<speaker>.*?): '(?P<message>.*)'`

### 4. Zone Changes
- `You have entered (?P<zone>.*)\.`

### 5. Loot & Trades
- `You receive (?P<item>.*) from (?P<giver>.*)\.`
- `You have looted a (?P<item>.*)\.`
- `--(?P<looter>.*) has looted a (?P<item>.*)\.--`

### 6. Critical Hits & Damage
- `You deliver a critical blast! \((?P<damage>\d+)\)`
- `You score a critical hit! \((?P<damage>\d+)\)`
- `(?P<attacker>.*) hits (?P<target>.*) for (?P<damage>\d+) points of damage\.`
