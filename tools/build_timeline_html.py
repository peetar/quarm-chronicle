import os
import json
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def build_timeline_card(character_name: str = "Tweedlede"):
    char_key = character_name.lower()
    data_file = os.path.join(PROJECT_ROOT, "data", "sample_output", f"{char_key}_timeline.json")
    output_html = os.path.join(PROJECT_ROOT, "src", "cards", f"{char_key}_timeline.html")

    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found. Run extract_timeline_events.py first.")
        return None

    with open(data_file, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)

    # Embed data into HTML to prevent local file:// CORS issues
    json_embedded = json.dumps(timeline_data)

    # Character metadata resolution
    summary_file = os.path.join(PROJECT_ROOT, "data", "sample_output", f"{char_key}_summary.json")
    summary = {}
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as sf:
            summary = json.load(sf)

    char_name = timeline_data.get("character", character_name).capitalize()
    char_class = summary.get("character_class")
    char_race = summary.get("character_race", "")

    if not char_class:
        for e in timeline_data.get("events", {}).get("level_2", []):
            if e.get("spell_class"):
                char_class = e["spell_class"]
                break
    if not char_class:
        char_class = "Adventurer"

    dings = [e.get("ding_level", 0) for e in timeline_data.get("events", {}).get("level_1", []) if e.get("type") == "level_ding"]
    max_lvl = max(dings) if dings else 60

    guild = "Dungeons and Dragons"
    if summary.get("guild_history"):
        guild = summary["guild_history"][-1].get("guild", guild)
    else:
        guild_events = [e for e in timeline_data.get("events", {}).get("level_1", []) if e.get("type") == "guild_join"]
        if guild_events:
            guild = guild_events[-1].get("guild", guild)

    epic_ev = next((e for e in timeline_data.get("events", {}).get("level_1", []) if e.get("type") == "epic_acquired"), None)
    epic_title = epic_ev["title"] if epic_ev else "Epic 1.0 Weapon"

    total_aas = len([e for e in timeline_data.get("events", {}).get("level_2", []) if e.get("type") == "aa_gain"])
    total_bosses = len([e for e in timeline_data.get("events", {}).get("level_3", []) if e.get("type") in ("raid_boss_kill", "pvp_boss_kill")])

    dr = timeline_data.get("date_range", {})
    start_str = (dr.get("start_date") or "2024-07")[:7]
    end_str = (dr.get("end_date") or "2026-09")[:7]
    try:
        s_lbl = datetime.strptime(start_str, "%Y-%m").strftime("%b %Y")
    except Exception:
        s_lbl = "Jul 2024"
    try:
        e_lbl = datetime.strptime(end_str, "%Y-%m").strftime("%b %Y")
    except Exception:
        e_lbl = "Sep 2026"
    date_range_label = f"{s_lbl} &ndash; {e_lbl}"
    char_desc = f"Level {max_lvl} {char_race + ' ' if char_race else ''}{char_class} &bull; &lt;{guild}&gt; &bull; Dynamic Career Trajectory"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Quarm Chronicle - {char_name} Interactive Timeline</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
  :root {{
    --gold: #d4af37;
    --gold-dark: #82641e;
    --gold-soft: #f3df8a;
    --bg-dark: #080a0f;
    --card-bg: rgba(16, 21, 34, 0.95);
    --card-border: #222c40;
    --cyan: #38bdf8;
    --cyan-glow: #7dd3fc;
    --purple: #c084fc;
    --crimson: #f87171;
    --emerald: #4ade80;
    --gray: #94a3b8;
    --light-gray: #cbd5e1;
    --white: #f8fafc;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background-color: var(--bg-dark);
    background-image: radial-gradient(circle at 50% 8%, #1e1b4b 0%, #080a0f 80%);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: var(--white);
    min-height: 100vh;
    padding: 20px 16px 60px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}

  .container {{
    width: 98%;
    max-width: 1560px;
  }}

  /* Header */
  .timeline-header {{
    background: rgba(15, 20, 32, 0.85);
    border: 2px double var(--gold);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 25px rgba(212, 175, 55, 0.12);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }}

  .header-left .series-tag {{
    color: var(--gold-soft);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 700;
  }}

  .header-left h1 {{
    font-family: Georgia, serif;
    font-size: 32px;
    margin: 4px 0;
    color: #fff;
    text-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
  }}

  .header-left .subtitle {{
    color: var(--cyan);
    font-size: 14px;
    font-weight: 500;
  }}

  /* Mode Switcher Buttons */
  .mode-switch {{
    display: flex;
    background: rgba(10, 14, 24, 0.8);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
  }}

  .mode-btn {{
    background: transparent;
    border: none;
    color: var(--gray);
    padding: 10px 18px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .mode-btn:hover {{
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
  }}

  .mode-btn.active {{
    background: linear-gradient(180deg, #2a344d 0%, #161f33 100%);
    color: var(--gold-soft);
    border: 1px solid var(--gold);
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.25);
  }}

  /* Controls Panel */
  .controls-panel {{
    background: rgba(18, 24, 38, 0.95);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}

  .controls-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }}

  .control-group {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .control-label {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--gold-soft);
    margin-right: 4px;
  }}

  /* Zoom Buttons */
  .zoom-btn {{
    background: rgba(25, 33, 52, 0.8);
    border: 1px solid var(--card-border);
    color: var(--light-gray);
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }}

  .zoom-btn:hover {{
    background: rgba(40, 52, 80, 0.9);
    color: #fff;
    border-color: var(--gold-dark);
  }}

  .zoom-btn.active {{
    background: var(--gold-dark);
    color: #fff;
    border: 1px solid var(--gold);
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
  }}

  /* Step Nav Buttons */
  .step-btn {{
    background: rgba(25, 33, 52, 0.7);
    border: 1px solid var(--card-border);
    color: var(--white);
    padding: 7px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }}

  .step-btn:hover {{
    background: rgba(45, 60, 92, 0.9);
    border-color: var(--cyan);
  }}

  .current-window-badge {{
    background: rgba(10, 15, 26, 0.9);
    border: 1px solid rgba(212, 175, 55, 0.3);
    padding: 7px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 700;
    color: var(--gold-soft);
    font-family: Georgia, serif;
    letter-spacing: 0.5px;
  }}

  /* Era Quick Jumps */
  .era-btn {{
    background: transparent;
    border: 1px solid var(--card-border);
    color: var(--gray);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }}
  .era-btn:hover {{
    color: #fff;
    border-color: var(--gold-soft);
    background: rgba(255, 255, 255, 0.05);
  }}
  .era-btn.classic {{ border-color: #c2410c; color: #fdba74; }}
  .era-btn.kunark {{ border-color: #16a34a; color: #86efac; }}
  .era-btn.velious {{ border-color: #2563eb; color: #93c5fd; }}
  .era-btn.luclin {{ border-color: #9333ea; color: #d8b4fe; }}
  .era-btn.pop {{ border-color: #dc2626; color: #fca5a5; opacity: 0.8; }}

  /* Timeline Canvas / Track Container */
  .timeline-card {{
    background: var(--card-bg);
    border: 2px double var(--gold);
    border-radius: 12px;
    padding: 24px 20px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 35px rgba(212, 175, 55, 0.12);
    position: relative;
    backdrop-filter: blur(12px);
    overflow: hidden;
    margin-bottom: 20px;
  }}

  .track-wrapper {{
    position: relative;
    width: 100%;
    min-height: 520px;
    overflow-x: hidden;
    overflow-y: hidden;
    padding: 40px 10px 80px 10px;
    box-sizing: border-box;
  }}
  @media (max-width: 900px) {{
    .track-wrapper {{
      overflow-x: auto;
    }}
  }}

  .timeline-axis-line {{
    position: absolute;
    top: 240px;
    left: 20px;
    right: 20px;
    height: 4px;
    background: linear-gradient(90deg, #3b2a1a 0%, #16a34a 25%, #2563eb 50%, #9333ea 75%, #dc2626 100%);
    border-radius: 2px;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    z-index: 2;
  }}

  /* Axis Date Ticks */
  .axis-tick {{
    position: absolute;
    top: 236px;
    width: 1px;
    height: 12px;
    background: rgba(212, 175, 55, 0.6);
    z-index: 2;
    pointer-events: none;
  }}

  .axis-tick-label {{
    position: absolute;
    top: 252px;
    transform: translateX(-50%);
    font-size: 11px;
    font-weight: 600;
    color: var(--gold-soft);
    font-family: monospace, sans-serif;
    pointer-events: none;
    z-index: 2;
    white-space: nowrap;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9);
  }}

  /* Event Node Base */
  .timeline-node {{
    position: absolute;
    z-index: 5;
    pointer-events: none; /* Hitbox is strictly the child badge/box */
  }}
  .timeline-node:hover {{
    z-index: 150 !important;
  }}

  /* Never animate, grow, or move connecting stems */
  .pinnacle-stem, .epic-stem, .guild-stem, .zone-first-stem, .spell-first-stem, .death-stem, .boss-kill-stem, .monthly-boss-stem {{
    pointer-events: none !important;
    transition: none !important;
  }}

  /* Level 1: Numbers Only Level Ding Badges */
  .node-level-ding {{
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
    border: 2px solid #fef3c7;
    color: #111;
    font-size: 11px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 8px rgba(245, 158, 11, 0.6);
    top: 228px;
    transform: translateX(-50%);
    z-index: 10;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    transform-origin: center center;
  }}
  .node-level-ding.key-level {{
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
    border: 2px solid #fff;
    font-size: 13px;
    top: 224px;
    box-shadow: 0 0 14px rgba(251, 191, 36, 0.9);
    z-index: 11;
  }}
  .node-level-ding:hover {{
    transform: translateX(-50%) scale(1.25);
    z-index: 150;
    box-shadow: 0 0 16px rgba(251, 191, 36, 1);
  }}

  /* Level 1: Pinnacle Boss Defeat (Top Row) */
  .node-pinnacle {{
    top: 130px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    z-index: 12;
    pointer-events: none;
  }}
  .pinnacle-badge {{
    background: rgba(30, 20, 50, 0.95);
    border: 2px solid var(--purple);
    color: #fff;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    box-shadow: 0 0 12px rgba(192, 132, 252, 0.5);
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    z-index: 12;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    transform-origin: center bottom;
  }}
  .pinnacle-badge:hover {{
    transform: scale(1.15);
    box-shadow: 0 0 16px rgba(192, 132, 252, 0.9);
  }}
  .pinnacle-stem {{
    width: 2px;
    height: 80px;
    background: var(--purple);
    z-index: 1;
    pointer-events: none;
  }}

  /* Level 1: Epic Weapon Acquisition (Top Row) */
  .node-epic {{
    top: 80px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    z-index: 12;
    pointer-events: none;
  }}
  .epic-badge {{
    background: rgba(40, 30, 10, 0.95);
    border: 2px solid var(--gold);
    color: var(--gold-soft);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 0 16px rgba(212, 175, 55, 0.7);
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    z-index: 12;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    transform-origin: center bottom;
  }}
  .epic-badge:hover {{
    transform: scale(1.12);
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.95);
  }}
  .epic-stem {{
    width: 2px;
    height: 130px;
    background: var(--gold);
    z-index: 1;
    pointer-events: none;
  }}

  /* Level 1: Guild Join (Bottom Row) */
  .node-guild {{
    top: 240px;
    display: flex;
    flex-direction: column;
    align-items: center;
    transform: translateX(-50%);
    z-index: 10;
    pointer-events: none;
  }}
  .guild-stem {{
    width: 1px;
    height: 35px;
    background: var(--cyan);
    z-index: 1;
    pointer-events: none;
  }}
  .guild-badge {{
    background: rgba(10, 30, 45, 0.95);
    border: 1px solid var(--cyan);
    color: #fff;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    z-index: 10;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    transform-origin: center top;
  }}
  .guild-badge:hover {{
    transform: scale(1.15);
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.8);
  }}

  /* Level 2: Zone Firsts (Staggered & Vertical line touches timeline) */
  .node-zone-first {{
    position: absolute;
    top: 240px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 8;
    pointer-events: none;
  }}
  .zone-first-stem {{
    width: 1px;
    background: var(--emerald);
    opacity: 0.75;
    z-index: 1;
    pointer-events: none;
  }}
  .zone-first-badge {{
    background: rgba(10, 35, 20, 0.95);
    border: 1px solid var(--emerald);
    color: #86efac;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    z-index: 8;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    transform-origin: center top;
  }}
  .zone-first-badge:hover {{
    transform: scale(1.15);
    box-shadow: 0 0 14px rgba(74, 222, 128, 0.9);
    background: rgba(16, 55, 30, 1);
  }}

  /* Level 2: AA Gains */
  .node-aa-gain {{
    top: 245px;
    transform: translateX(-50%) rotate(45deg);
    width: 16px;
    height: 16px;
    border-radius: 3px;
    background: var(--purple);
    border: 1px solid #fff;
    box-shadow: 0 0 6px rgba(192, 132, 252, 0.7);
    z-index: 9;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  .node-aa-gain:hover {{
    transform: translateX(-50%) rotate(45deg) scale(1.3);
    box-shadow: 0 0 12px rgba(192, 132, 252, 1);
  }}
  /* Macro AA Markers: Small, non-clickable progression dots on the timeline */
  .node-aa-gain-macro {{
    position: absolute;
    top: 237px;
    transform: translateX(-50%) rotate(45deg);
    width: 6px;
    height: 6px;
    border-radius: 1px;
    background: #c084fc;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 0 4px rgba(192, 132, 252, 0.85);
    z-index: 4;
    pointer-events: none !important;
    cursor: default !important;
  }}
  .node-aa-gain-macro.overview {{
    top: 197px;
  }}

  /* Level 2: Spell Firsts (Staggered & Vertical line touches timeline) */
  .node-spell-first {{
    position: absolute;
    top: 240px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 7;
    pointer-events: none;
  }}
  .spell-first-stem {{
    width: 1px;
    background: var(--purple);
    opacity: 0.7;
    z-index: 1;
    pointer-events: none;
  }}
  .spell-first-badge {{
    background: rgba(30, 15, 45, 0.95);
    border: 1px solid var(--purple);
    color: #e9d5ff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 500;
    white-space: nowrap;
    z-index: 7;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    transform-origin: center top;
  }}
  .spell-first-badge:hover {{
    transform: scale(1.15);
    box-shadow: 0 0 14px rgba(192, 132, 252, 0.9);
    background: rgba(50, 20, 75, 1);
  }}

  /* Level 3: Deaths (Skull Icon with Tooltip & Line to Timeline) */
  .node-death {{
    position: absolute;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 8;
    pointer-events: none;
  }}
  .death-stem {{
    width: 1px;
    background: var(--crimson);
    opacity: 0.65;
    z-index: 1;
    pointer-events: none;
  }}
  .death-icon-badge {{
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: linear-gradient(135deg, #450a0a 0%, #1c0606 100%);
    border: 1.5px solid var(--crimson);
    box-shadow: 0 0 8px rgba(248, 113, 113, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    cursor: pointer;
    z-index: 8;
    pointer-events: auto;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    transform-origin: center center;
  }}
  .death-icon-badge:hover {{
    transform: scale(1.25);
    box-shadow: 0 0 14px rgba(248, 113, 113, 1);
  }}
  .node-death:hover {{
    z-index: 250 !important;
  }}
  .node-death:hover .death-tooltip {{
    display: block;
  }}
  .death-tooltip {{
    display: none;
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%);
    background: rgba(15, 20, 32, 0.98);
    border: 1px solid var(--crimson);
    border-radius: 6px;
    padding: 8px 12px;
    width: 220px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.9), 0 0 12px rgba(248, 113, 113, 0.35);
    pointer-events: none;
    white-space: normal;
    text-align: left;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    z-index: 250;
  }}
  .death-tooltip-title {{
    font-weight: 700;
    color: var(--crimson);
    font-size: 12px;
    margin-bottom: 4px;
    border-bottom: 1px solid rgba(248, 113, 113, 0.3);
    padding-bottom: 3px;
  }}
  .death-tooltip-row {{
    font-size: 11px;
    color: var(--light-gray);
    margin: 2px 0;
    display: flex;
    justify-content: space-between;
  }}
  .death-tooltip-row span {{
    color: var(--gray);
  }}

  /* Level 3: Boss Kills (Raid & PvP) with line to timeline */
  .node-boss-kill {{
    position: absolute;
    top: 240px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 9;
    pointer-events: none;
  }}
  .boss-kill-stem {{
    width: 1px;
    background: var(--cyan);
    opacity: 0.75;
    z-index: 1;
    pointer-events: none;
  }}
  .boss-kill-stem.pvp {{
    background: var(--purple);
  }}
  .boss-kill-badge {{
    background: rgba(12, 28, 48, 0.95);
    border: 1px solid var(--cyan);
    color: var(--cyan-glow);
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
    z-index: 9;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    transform-origin: center top;
  }}
  .boss-kill-badge.pvp {{
    border-color: var(--purple);
    color: #e9d5ff;
    background: rgba(30, 15, 45, 0.95);
  }}
  .boss-kill-badge:hover {{
    transform: scale(1.15);
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.9);
    background: rgba(20, 45, 75, 1);
  }}
  .boss-kill-badge.pvp:hover {{
    box-shadow: 0 0 16px rgba(192, 132, 252, 0.9);
    background: rgba(50, 20, 75, 1);
  }}
  .node-boss-kill:hover {{
    z-index: 250 !important;
  }}

  /* Macro Monthly Boss Summary */
  .node-monthly-boss {{
    position: absolute;
    top: 240px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 8;
    pointer-events: none;
  }}
  .monthly-boss-stem {{
    width: 1px;
    background: var(--cyan);
    opacity: 0.55;
    z-index: 1;
    pointer-events: none;
  }}
  .monthly-boss-badge {{
    background: rgba(10, 24, 42, 0.95);
    border: 1px solid var(--cyan);
    border-radius: 6px;
    padding: 5px 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6), 0 0 8px rgba(56, 189, 248, 0.25);
    z-index: 8;
    pointer-events: auto;
    cursor: pointer;
    text-align: center;
    white-space: nowrap;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease, background 0.15s ease;
    transform-origin: center top;
  }}
  .monthly-boss-badge:hover {{
    transform: scale(1.12);
    border-color: var(--cyan-glow);
    background: rgba(18, 42, 72, 0.98);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.9), 0 0 16px rgba(56, 189, 248, 0.85);
  }}
  .node-monthly-boss:hover {{
    z-index: 200 !important;
  }}
  .monthly-boss-count {{
    font-size: 11px;
    font-weight: 800;
    color: var(--cyan-glow);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }}
  .monthly-boss-sample {{
    font-size: 9.5px;
    font-weight: 500;
    color: var(--light-gray);
    margin-top: 2px;
    max-width: 155px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}

  /* Level 3: Daily Activity Summaries and Rezzes */
  .node-level3-summary {{
    position: absolute;
    top: 400px;
    background: rgba(20, 26, 40, 0.95);
    border: 1px solid var(--card-border);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
    width: 170px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    z-index: 6;
    pointer-events: auto;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    transform-origin: center top;
  }}
  .node-level3-summary:hover {{
    transform: scale(1.06);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.8);
  }}

  /* Mini-Map Scrubber Bar (Draggable) */
  .minimap-container {{
    background: rgba(10, 14, 22, 0.9);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 12px;
    position: relative;
    margin-top: 10px;
    user-select: none;
  }}
  .minimap-title {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--gray);
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
  }}
  .minimap-bar {{
    height: 22px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
  }}
  .minimap-viewport-box {{
    position: absolute;
    top: 0;
    bottom: 0;
    background: rgba(212, 175, 55, 0.28);
    border: 2px solid var(--gold);
    border-radius: 4px;
    cursor: grab;
    transition: background 0.15s ease;
  }}
  .minimap-viewport-box:hover {{
    background: rgba(212, 175, 55, 0.4);
  }}
  .minimap-viewport-box:active {{
    cursor: grabbing;
    background: rgba(212, 175, 55, 0.5);
  }}

  /* Event Details Modal */
  .modal-backdrop {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(4px);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }}
  .modal-card {{
    background: var(--card-bg);
    border: 2px solid var(--gold);
    border-radius: 12px;
    width: 90%;
    max-width: 580px;
    max-height: 85vh;
    overflow-y: auto;
    padding: 24px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9);
    position: relative;
  }}
  /* Modal Boss Kills List */
  .modal-kills-list {{
    margin-top: 14px;
    max-height: 380px;
    overflow-y: auto;
    border: 1px solid var(--card-border);
    border-radius: 6px;
    background: rgba(8, 12, 20, 0.6);
  }}
  .modal-kill-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 13px;
    gap: 8px;
  }}
  .modal-kill-item:last-child {{
    border-bottom: none;
  }}
  .modal-kill-name {{
    font-weight: 600;
    color: var(--cyan-glow);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .modal-kill-meta {{
    font-size: 11px;
    color: var(--gray);
    text-align: right;
    white-space: nowrap;
  }}
  .modal-kill-tag {{
    font-size: 9px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 3px;
    text-transform: uppercase;
  }}
  .modal-kill-tag.pvp {{
    background: rgba(147, 51, 234, 0.25);
    border: 1px solid var(--purple);
    color: #d8b4fe;
  }}
  .modal-kill-tag.raid {{
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid var(--cyan);
    color: var(--cyan);
  }}
  .modal-close {{
    position: absolute;
    top: 14px;
    right: 16px;
    background: transparent;
    border: none;
    color: var(--gray);
    font-size: 20px;
    cursor: pointer;
  }}
  .modal-close:hover {{ color: #fff; }}
  .modal-title {{
    font-family: Georgia, serif;
    font-size: 22px;
    color: #fff;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    padding-bottom: 8px;
  }}
  .modal-row {{
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 14px;
  }}
  .modal-label {{ color: var(--gray); }}
  .modal-val {{ color: #fff; font-weight: 600; text-align: right; }}

  /* Static Overview Mode Display */
  #overview-mode-view {{
    display: none;
  }}
  .overview-container {{
    padding: 20px 10px;
    text-align: center;
  }}

  /* Presentation Slide / Image Snapshot Mode */
  body.snapshot-mode {{
    padding: 20px 24px !important;
    background: #080a0f !important;
    min-height: auto !important;
    box-sizing: border-box !important;
  }}
  body.snapshot-mode .container {{
    width: 100% !important;
    max-width: 100% !important;
  }}
  body.snapshot-mode .timeline-header,
  body.snapshot-mode .mode-switch,
  body.snapshot-mode .controls-panel,
  body.snapshot-mode .overview-export-toolbar,
  body.snapshot-mode footer {{
    display: none !important;
  }}
  body.snapshot-mode .timeline-card {{
    margin-bottom: 0 !important;
    border: 2px double var(--gold) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 35px rgba(212, 175, 55, 0.15) !important;
    background: rgba(16, 21, 34, 0.98) !important;
    padding: 24px 28px !important;
  }}
</style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <div class="timeline-header">
    <div class="header-left">
      <div class="series-tag">Project Quarm &bull; TAKP Chronicle Engine</div>
      <h1>{char_name.upper()} TIMELINE</h1>
      <div class="subtitle">{char_desc}</div>
    </div>

    <div class="mode-switch">
      <button id="btn-mode-interactive" class="mode-btn active" onclick="switchMode('interactive')">🔍 Interactive Zoom</button>
      <button id="btn-mode-overview" class="mode-btn" onclick="switchMode('overview')">🖼️ Overview Snapshot</button>
    </div>
  </div>

  <!-- Interactive Controls Panel -->
  <div id="interactive-controls" class="controls-panel">
    <!-- Row 1: Zoom Level Selection -->
    <div class="controls-row">
      <div class="control-group">
        <span class="control-label">Zoom Level:</span>
        <button id="zoom-1" class="zoom-btn active" onclick="setZoomLevel(1)">1: Macro (All-Time)</button>
        <button id="zoom-2" class="zoom-btn" onclick="setZoomLevel(2)">2: Seasonal (1 Month)</button>
        <button id="zoom-3" class="zoom-btn" onclick="setZoomLevel(3)">3: Week Deep Dive (7 Days)</button>
      </div>

      <!-- Era Quick-Jumps -->
      <div class="control-group">
        <span class="control-label">Jump to Era:</span>
        <button class="era-btn classic" onclick="jumpToEra('Classic')">Classic</button>
        <button class="era-btn kunark" onclick="jumpToEra('Kunark')">Kunark</button>
        <button class="era-btn velious" onclick="jumpToEra('Velious')">Velious</button>
        <button class="era-btn luclin" onclick="jumpToEra('Luclin')">Luclin</button>
        <button class="era-btn pop" onclick="jumpToPoP()">Planes of Power</button>
      </div>
    </div>

    <!-- Row 2: Step Navigation Controls -->
    <div class="controls-row" id="step-nav-row" style="display:none;">
      <div class="control-group">
        <button class="step-btn" onclick="stepTime(-30)">&laquo; 1 Month</button>
        <button class="step-btn" onclick="stepTime(-7)">&lsaquo; 1 Week</button>
      </div>

      <div id="current-window-label" class="current-window-badge">
        All-Time Career ({date_range_label})
      </div>

      <div class="control-group">
        <button class="step-btn" onclick="stepTime(7)">1 Week &rsaquo;</button>
        <button class="step-btn" onclick="stepTime(30)">1 Month &raquo;</button>
        <button class="step-btn" style="border-color:var(--gold);" onclick="jumpToLatest()">Latest &raquo;|</button>
      </div>
    </div>
  </div>

  <!-- Main Timeline Card Display -->
  <div class="timeline-card">
    <div id="interactive-mode-view">
      <div class="track-wrapper" id="track-wrapper">
        <div class="timeline-axis-line" id="timeline-axis-line"></div>
        <div id="nodes-container"></div>
      </div>

      <!-- Scrubber Mini-Map (Draggable) -->
      <div class="minimap-container">
        <div class="minimap-title">
          <span>Timeline Scrubber (Drag or Click to Navigate)</span>
          <span id="minimap-dates">{date_range_label}</span>
        </div>
        <div class="minimap-bar" id="minimap-bar">
          <div class="minimap-viewport-box" id="minimap-viewport"></div>
        </div>
      </div>
    </div>

    <!-- Static Overview Mode -->
    <div id="overview-mode-view">
      <div class="overview-container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom: 14px; gap: 12px; text-align:left;">
          <div>
            <div style="font-family: Georgia, serif; font-size: 24px; color: var(--gold-soft);">
              {char_name} &mdash; Career Milestones &amp; Raid Encounters
            </div>
            <div style="color: var(--gray); font-size: 13px; margin-top: 4px;">
              Project Quarm ({date_range_label}) &bull; Level Milestones, Epic 1.0, Pinnacle Kills, AA Progression &amp; Monthly Raid Summaries
            </div>
          </div>
          <div class="overview-export-toolbar" style="display:flex; gap:8px;">
            <button class="step-btn" style="border-color:var(--gold); color:var(--gold-soft); padding: 8px 14px;" onclick="copyOverviewImage()" id="btn-copy-overview">📋 Copy Image</button>
            <button class="step-btn" style="border-color:var(--cyan); color:var(--cyan-glow); padding: 8px 14px;" onclick="downloadOverviewImage()">💾 Download PNG</button>
          </div>
        </div>
        <div class="track-wrapper" id="overview-track-wrapper" style="min-height: 490px;">
          <div class="timeline-axis-line" style="top: 200px;"></div>
          <div id="overview-nodes-container"></div>
        </div>
        <!-- Legend Footer Strip -->
        <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(212,175,55,0.2); display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; font-size: 12px; color: var(--gray);">
          <span><strong style="color:var(--gold-soft);">👑</strong> Pinnacle First Kills</span>
          <span><strong style="color:var(--gold);">✨</strong> {epic_title}</span>
          <span><strong style="color:#fbbf24;">●</strong> Milestone Dings (1&ndash;{max_lvl})</span>
          <span><strong style="color:var(--purple);">◆</strong> Alternate Advancements ({total_aas} AAs)</span>
          <span><strong style="color:var(--cyan-glow);">⚔️</strong> {total_bosses} Monthly Raid &amp; PvP Boss Kills</span>
        </div>
      </div>
    </div>
  </div>

</div>

<!-- Event Detail Modal -->
<div class="modal-backdrop" id="event-modal" onclick="closeModal(event)">
  <div class="modal-card" onclick="event.stopPropagation()">
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <div class="modal-title" id="modal-title">Event Title</div>
    <div id="modal-rows"></div>
  </div>
</div>

<footer>
  Project Quarm Chronicle &bull; Generated from TAKP Mac Client Logs &bull; Linked with <a href="https://www.pqdi.cc" target="_blank" style="color:var(--cyan); text-decoration:none;">pqdi.cc</a>
</footer>

<!-- Embedded Timeline Data -->
<script>
window.TIMELINE_DATA = {json_embedded};
</script>

<script>
// State
let currentMode = 'interactive';
let currentZoom = 1;
let currentWindowStart = null;
let currentWindowEnd = null;

// Dragging state for scrubber
let isDraggingScrubber = false;
let dragStartX = 0;
let dragStartWindowStart = 0;
let dragStartWindowEnd = 0;

// Date range from data
const minDateMs = new Date(window.TIMELINE_DATA.date_range.start_iso || (window.TIMELINE_DATA.date_range.start_date + 'T00:00:00')).getTime();
const maxDateMs = new Date(window.TIMELINE_DATA.date_range.end_iso || (window.TIMELINE_DATA.date_range.end_date + 'T23:59:59')).getTime();

const PINNACLE_NAMES = [
  'Aten Ha Ra', 'The Avatar of War', 'Vulak`Aerr', 'Phara Dar', 'Tunare',
  'Lord Nagafen', 'Lady Vox', 'Trakanon', 'Innoruuk', 'Cazic Thule',
  'Severilous', 'Talendor', 'Gorenaire', 'Faydedar', 'Venril Sathir',
  'Dozekar the Cursed', 'Aaryonar', 'Eashen of the Sky'
];

function getMonthlyBossSummaries() {{
  if (window._cachedMonthlyBossSummaries) {{
    return window._cachedMonthlyBossSummaries;
  }}

  const l3 = window.TIMELINE_DATA.events.level_3 || [];
  const bossKills = l3.filter(e => e.type === 'raid_boss_kill' || e.type === 'pvp_boss_kill');

  const monthMap = {{}};

  bossKills.forEach(k => {{
    const dt = new Date(k.iso || k.date || k.timestamp);
    const y = dt.getFullYear();
    const m = String(dt.getMonth() + 1).padStart(2, '0');
    const ym = `${{y}}-${{m}}`;

    if (!monthMap[ym]) {{
      monthMap[ym] = {{
        type: 'monthly_boss_summary',
        month_key: ym,
        year: y,
        month: dt.getMonth() + 1,
        month_name: dt.toLocaleString('en-US', {{ month: 'short' }}),
        kills: []
      }};
    }}
    monthMap[ym].kills.push(k);
  }});

  const summaries = Object.values(monthMap).map(m => {{
    m.kills.sort((a, b) => {{
      const ta = new Date(a.iso || a.date || a.timestamp).getTime();
      const tb = new Date(b.iso || b.date || b.timestamp).getTime();
      return ta - tb;
    }});

    const totalTime = m.kills.reduce((acc, k) => acc + new Date(k.iso || k.date || k.timestamp).getTime(), 0);
    const avgTime = Math.round(totalTime / m.kills.length);
    m.timestamp_ms = avgTime;
    m.iso = new Date(avgTime).toISOString();

    const uniqueBosses = Array.from(new Set(m.kills.map(k => k.boss)));
    m.unique_boss_count = uniqueBosses.length;

    const sortedBosses = [...uniqueBosses].sort((a, b) => {{
      const getPrio = (name) => {{
        for (let i = 0; i < PINNACLE_NAMES.length; i++) {{
          if (name.toLowerCase().includes(PINNACLE_NAMES[i].toLowerCase())) return i;
        }}
        return 999;
      }};
      return getPrio(a) - getPrio(b);
    }});

    const sample = sortedBosses.slice(0, 2);
    let sampleStr = sample.join(', ');
    if (uniqueBosses.length > sample.length) {{
      sampleStr += ` +${{uniqueBosses.length - sample.length}}`;
    }}
    m.sample_text = sampleStr;
    m.title = `Boss Kills — ${{m.month_name}} ${{m.year}} (${{m.kills.length}} Kills)`;

    const zoneCounts = {{}};
    m.kills.forEach(k => {{
      zoneCounts[k.zone] = (zoneCounts[k.zone] || 0) + 1;
    }});
    m.zone_breakdown = Object.entries(zoneCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([z, c]) => `${{z}} (${{c}})`)
      .join(', ');

    return m;
  }});

  summaries.sort((a, b) => a.timestamp_ms - b.timestamp_ms);

  window._cachedMonthlyBossSummaries = summaries;
  return summaries;
}}

function initTimeline() {{
  currentWindowStart = minDateMs;
  currentWindowEnd = maxDateMs;
  setupScrubberDrag();
  renderInteractiveTimeline();
  renderOverviewTimeline();

  const hash = window.location.hash;
  const params = new URLSearchParams(window.location.search);
  if (hash === '#snapshot' || params.get('snapshot') === '1') {{
    document.body.classList.add('snapshot-mode');
    switchMode('overview');
  }} else if (hash === '#overview' || params.get('mode') === 'overview') {{
    switchMode('overview');
  }}
}}

function switchMode(mode) {{
  currentMode = mode;
  document.getElementById('btn-mode-interactive').classList.toggle('active', mode === 'interactive');
  document.getElementById('btn-mode-overview').classList.toggle('active', mode === 'overview');

  document.getElementById('interactive-mode-view').style.display = mode === 'interactive' ? 'block' : 'none';
  document.getElementById('overview-mode-view').style.display = mode === 'overview' ? 'block' : 'none';
  document.getElementById('interactive-controls').style.display = mode === 'interactive' ? 'flex' : 'none';

  if (mode === 'overview') {{
    renderOverviewTimeline();
  }} else {{
    renderInteractiveTimeline();
  }}
}}

function setZoomLevel(lvl) {{
  currentZoom = lvl;
  document.querySelectorAll('.zoom-btn').forEach((b, idx) => {{
    b.classList.toggle('active', (idx + 1) === lvl);
  }});

  const stepNav = document.getElementById('step-nav-row');

  if (lvl === 1) {{
    // Macro View: Entire playspan
    currentWindowStart = minDateMs;
    currentWindowEnd = maxDateMs;
    stepNav.style.display = 'none';
  }} else if (lvl === 2) {{
    // Seasonal Horizon: 1 Month (30 days)
    stepNav.style.display = 'flex';
    const monthSpan = 30 * 24 * 60 * 60 * 1000;
    const currentCenter = (currentWindowStart + currentWindowEnd) / 2;
    let newStart = currentCenter - (monthSpan / 2);
    let newEnd = currentCenter + (monthSpan / 2);

    if (newStart < minDateMs) {{
      newStart = minDateMs;
      newEnd = Math.min(maxDateMs, newStart + monthSpan);
    }}
    if (newEnd > maxDateMs) {{
      newEnd = maxDateMs;
      newStart = Math.max(minDateMs, newEnd - monthSpan);
    }}
    currentWindowStart = newStart;
    currentWindowEnd = newEnd;
  }} else if (lvl === 3) {{
    // Week View: 7 days window
    stepNav.style.display = 'flex';
    const weekSpan = 7 * 24 * 60 * 60 * 1000;
    const currentCenter = (currentWindowStart + currentWindowEnd) / 2;
    let newStart = currentCenter - (weekSpan / 2);
    let newEnd = currentCenter + (weekSpan / 2);

    if (newStart < minDateMs) {{
      newStart = minDateMs;
      newEnd = Math.min(maxDateMs, newStart + weekSpan);
    }}
    if (newEnd > maxDateMs) {{
      newEnd = maxDateMs;
      newStart = Math.max(minDateMs, newEnd - weekSpan);
    }}
    currentWindowStart = newStart;
    currentWindowEnd = newEnd;
  }}

  updateWindowLabel();
  renderInteractiveTimeline();
}}

function stepTime(days) {{
  const span = currentWindowEnd - currentWindowStart;
  const delta = days * 24 * 60 * 60 * 1000;

  let newStart = currentWindowStart + delta;
  let newEnd = currentWindowEnd + delta;

  if (newStart < minDateMs) {{
    newStart = minDateMs;
    newEnd = newStart + span;
  }}
  if (newEnd > maxDateMs) {{
    newEnd = maxDateMs;
    newStart = Math.max(minDateMs, newEnd - span);
  }}

  currentWindowStart = newStart;
  currentWindowEnd = newEnd;
  updateWindowLabel();
  renderInteractiveTimeline();
}}

function jumpToDate(dateStr) {{
  const targetMs = new Date(dateStr).getTime();
  const span = (currentZoom === 1) ? (30 * 24 * 3600 * 1000) : (currentZoom === 2 ? 30 * 24 * 3600 * 1000 : 7 * 24 * 3600 * 1000);

  currentWindowStart = Math.max(minDateMs, targetMs);
  currentWindowEnd = Math.min(maxDateMs, currentWindowStart + span);

  if (currentZoom === 1) {{
    setZoomLevel(2);
  }} else {{
    updateWindowLabel();
    renderInteractiveTimeline();
  }}
}}

function jumpToLatest() {{
  const span = currentWindowEnd - currentWindowStart;
  currentWindowEnd = maxDateMs;
  currentWindowStart = Math.max(minDateMs, maxDateMs - span);
  updateWindowLabel();
  renderInteractiveTimeline();
}}

function jumpToPoP() {{
  alert("Planes of Power is coming soon! " + (window.TIMELINE_DATA.character || "Your character") + " is primed and ready.");
}}

function jumpToEra(eraName) {{
  const eras = window.TIMELINE_DATA.eras || [];
  const eraObj = eras.find(e => e.era && e.era.toLowerCase() === eraName.toLowerCase());
  if (eraObj && eraObj.date) {{
    jumpToDate(eraObj.date);
  }} else if (eraName.toLowerCase() === 'classic') {{
    jumpToDate(window.TIMELINE_DATA.date_range.start_date || '2024-07-06');
  }} else {{
    alert("No recorded entries for " + eraName + " found in this character's chronicle.");
  }}
}}

function updateWindowLabel() {{
  const sStr = new Date(currentWindowStart).toLocaleDateString('en-US', {{ month: 'short', day: 'numeric', year: 'numeric' }});
  const eStr = new Date(currentWindowEnd).toLocaleDateString('en-US', {{ month: 'short', day: 'numeric', year: 'numeric' }});
  document.getElementById('current-window-label').textContent = `${{sStr}} \u2013 ${{eStr}}`;
}}

/* Date Ticks on Timeline Axis */
function renderAxisTicks(wStart, wEnd, width, container) {{
  const totalMs = wEnd - wStart;
  if (totalMs <= 0) return;

  const ticksContainer = document.createElement('div');
  ticksContainer.id = 'axis-ticks-container';
  ticksContainer.style.position = 'absolute';
  ticksContainer.style.top = '0';
  ticksContainer.style.left = '0';
  ticksContainer.style.width = '100%';
  ticksContainer.style.height = '100%';
  ticksContainer.style.pointerEvents = 'none';
  ticksContainer.style.zIndex = '2';

  const ticks = [];

  if (currentZoom === 1) {{
    // Level 1: Regular month interval (10/24, 11/24, 12/24 etc.)
    let cur = new Date(wStart);
    cur.setDate(1);
    cur.setHours(0, 0, 0, 0);
    while (cur.getTime() < wStart) {{
      cur.setMonth(cur.getMonth() + 1);
    }}
    while (cur.getTime() <= wEnd) {{
      const m = cur.getMonth() + 1;
      const yy = String(cur.getFullYear()).slice(-2);
      ticks.push({{
        time: cur.getTime(),
        label: `${{m}}/${{yy}}`
      }});
      cur.setMonth(cur.getMonth() + 1);
    }}
  }} else if (currentZoom === 2) {{
    // Level 2: Start of every week (Sunday)
    let cur = new Date(wStart);
    cur.setHours(0, 0, 0, 0);
    while (cur.getDay() !== 0) {{
      cur.setDate(cur.getDate() + 1);
    }}
    while (cur.getTime() <= wEnd) {{
      if (cur.getTime() >= wStart) {{
        const m = cur.getMonth() + 1;
        const d = cur.getDate();
        ticks.push({{
          time: cur.getTime(),
          label: `${{m}}/${{d}}`
        }});
      }}
      cur.setDate(cur.getDate() + 7);
    }}
  }} else if (currentZoom === 3) {{
    // Level 3: Every single day
    let cur = new Date(wStart);
    cur.setHours(0, 0, 0, 0);
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    while (cur.getTime() <= wEnd) {{
      if (cur.getTime() >= wStart) {{
        const dayStr = dayNames[cur.getDay()];
        const m = cur.getMonth() + 1;
        const d = cur.getDate();
        ticks.push({{
          time: cur.getTime(),
          label: `${{dayStr}} ${{m}}/${{d}}`
        }});
      }}
      cur.setDate(cur.getDate() + 1);
    }}
  }}

  ticks.forEach(t => {{
    const pct = (t.time - wStart) / totalMs;
    const posX = Math.round(pct * (width - 100)) + 50;

    const tickLine = document.createElement('div');
    tickLine.className = 'axis-tick';
    tickLine.style.left = posX + 'px';
    ticksContainer.appendChild(tickLine);

    const tickLabel = document.createElement('div');
    tickLabel.className = 'axis-tick-label';
    tickLabel.style.left = posX + 'px';
    tickLabel.textContent = t.label;
    ticksContainer.appendChild(tickLabel);
  }});

  container.appendChild(ticksContainer);
}}

function renderInteractiveTimeline() {{
  const container = document.getElementById('nodes-container');
  container.innerHTML = '';

  const wStart = currentWindowStart;
  const wEnd = currentWindowEnd;
  const totalMs = wEnd - wStart;
  if (totalMs <= 0) return;

  const trackWrapper = document.getElementById('track-wrapper');
  const width = trackWrapper.clientWidth;
  container.style.width = width + 'px';

  // Render date ticks along timeline axis line
  renderAxisTicks(wStart, wEnd, width, container);

  // Gather active events by zoom level
  let activeEvents = [];
  activeEvents.push(...window.TIMELINE_DATA.events.level_1);
  if (currentZoom === 1) {{
    activeEvents.push(...getMonthlyBossSummaries());
    const aas = (window.TIMELINE_DATA.events.level_2 || []).filter(e => e.type === 'aa_gain');
    activeEvents.push(...aas);
  }} else if (currentZoom >= 2) {{
    activeEvents.push(...window.TIMELINE_DATA.events.level_2);
  }}
  if (currentZoom >= 3) {{
    activeEvents.push(...window.TIMELINE_DATA.events.level_3.filter(e => e.type !== 'rez_accepted'));
  }}

  // Filter events within window
  const inWindow = activeEvents.filter(e => {{
    const t = new Date(e.iso || e.date || e.timestamp).getTime();
    return t >= wStart && t <= wEnd;
  }});

  // Sort chronologically for clean staggered stacking
  inWindow.sort((a, b) => {{
    const ta = new Date(a.iso || a.date || a.timestamp).getTime();
    const tb = new Date(b.iso || b.date || b.timestamp).getTime();
    return ta - tb;
  }});

  // Stagger tracking state
  let lastZonePosX = -999;
  let zoneStaggerIdx = 0;

  let lastSpellPosX = -999;
  let spellStaggerIdx = 0;

  let lastDeathPosX = -999;
  let deathStaggerIdx = 0;

  let lastBossPosX = -999;
  let bossStaggerIdx = 0;

  let lastMonthPosX = -999;
  let monthStaggerIdx = 0;

  // Render nodes
  inWindow.forEach(e => {{
    const t = new Date(e.iso || e.date || e.timestamp).getTime();
    const pct = (t - wStart) / totalMs;
    const posX = Math.round(pct * (width - 100)) + 50;

    const node = document.createElement('div');
    node.className = 'timeline-node';
    node.style.left = posX + 'px';

    if (e.type === 'level_ding') {{
      const isKey = (e.ding_level % 10 === 0) || e.ding_level === 60;
      node.className += ' node-level-ding' + (isKey ? ' key-level' : '');
      node.textContent = e.badge;
      node.title = `Level ${{e.ding_level}} reached in ${{e.zone}} on ${{e.date}}`;
    }} else if (e.type === 'pinnacle_first') {{
      node.className += ' node-pinnacle';
      node.innerHTML = `
        <div class="pinnacle-badge">👑 ${{e.boss}}</div>
        <div class="pinnacle-stem"></div>
      `;
    }} else if (e.type === 'epic_acquired') {{
      node.className += ' node-epic';
      node.innerHTML = `
        <div class="epic-badge">✨ ${{e.title}}</div>
        <div class="epic-stem"></div>
      `;
    }} else if (e.type === 'guild_join' || e.type === 'guild_leave') {{
      node.className += ' node-guild';
      node.innerHTML = `
        <div class="guild-stem"></div>
        <div class="guild-badge">${{e.type === 'guild_join' ? '🛡️ Joined' : '🚪 Left'}} &lt;${{e.guild}}&gt;</div>
      `;
    }} else if (e.type === 'zone_first') {{
      // Stagger vertical distance so nearby zone first entries don't collide
      if (Math.abs(posX - lastZonePosX) < 85) {{
        zoneStaggerIdx = (zoneStaggerIdx + 1) % 4;
      }} else {{
        zoneStaggerIdx = 0;
      }}
      lastZonePosX = posX;

      const stemHeight = 35 + (zoneStaggerIdx * 30); // 35px, 65px, 95px, 125px
      node.className = 'timeline-node node-zone-first';
      node.style.top = '240px';
      node.innerHTML = `
        <div class="zone-first-stem" style="height: ${{stemHeight}}px;"></div>
        <div class="zone-first-badge">🧭 ${{e.zone}}</div>
      `;
    }} else if (e.type === 'aa_gain') {{
      if (currentZoom === 1) {{
        node.className = 'timeline-node node-aa-gain-macro';
        node.title = `${{e.title}} (${{e.date}})`;
      }} else {{
        node.className = 'timeline-node node-aa-gain';
        node.title = `${{e.title}} in ${{e.zone}} (${{e.date}})`;
      }}
    }} else if (e.type === 'monthly_boss_summary') {{
      if (Math.abs(posX - lastMonthPosX) < 110) {{
        monthStaggerIdx = (monthStaggerIdx + 1) % 3;
      }} else {{
        monthStaggerIdx = 0;
      }}
      lastMonthPosX = posX;

      const stemHeight = 70 + (monthStaggerIdx * 52); // 70px, 122px, 174px
      node.className = 'timeline-node node-monthly-boss';
      node.style.top = '240px';
      node.innerHTML = `
        <div class="monthly-boss-stem" style="height: ${{stemHeight}}px;"></div>
        <div class="monthly-boss-badge" title="Click to view all ${{e.kills.length}} boss kills in ${{e.month_name}} ${{e.year}}">
          <div class="monthly-boss-count">⚔️ ${{e.kills.length}} ${{e.kills.length === 1 ? 'Boss Kill' : 'Boss Kills'}}</div>
          <div class="monthly-boss-sample">${{e.sample_text}}</div>
        </div>
      `;
    }} else if (e.type === 'spell_first') {{
      // Stagger vertical distance so multiple spells don't stack
      if (Math.abs(posX - lastSpellPosX) < 80) {{
        spellStaggerIdx = (spellStaggerIdx + 1) % 5;
      }} else {{
        spellStaggerIdx = 0;
      }}
      lastSpellPosX = posX;

      const stemHeight = 45 + (spellStaggerIdx * 30); // 45px, 75px, 105px, 135px, 165px
      node.className = 'timeline-node node-spell-first';
      node.style.top = '240px';
      node.innerHTML = `
        <div class="spell-first-stem" style="height: ${{stemHeight}}px;"></div>
        <div class="spell-first-badge">🪄 ${{e.spell}}</div>
      `;
    }} else if (e.type === 'death') {{
      // Skull icon with line to timeline, staggered heights, and hover tooltip
      if (Math.abs(posX - lastDeathPosX) < 35) {{
        deathStaggerIdx = (deathStaggerIdx + 1) % 4;
      }} else {{
        deathStaggerIdx = 0;
      }}
      lastDeathPosX = posX;

      const stemHeight = 35 + (deathStaggerIdx * 25); // 35px, 60px, 85px, 110px
      const topPos = 240 - stemHeight - 22;

      node.className = 'timeline-node node-death';
      node.style.top = topPos + 'px';
      node.innerHTML = `
        <div class="death-icon-badge" title="${{e.title}}">☠️</div>
        <div class="death-stem" style="height: ${{stemHeight}}px;"></div>
        <div class="death-tooltip">
          <div class="death-tooltip-title">☠️ ${{e.title}}</div>
          <div class="death-tooltip-row"><span>Zone:</span> <strong>${{e.zone}}</strong></div>
          <div class="death-tooltip-row"><span>Time:</span> <strong>${{e.timestamp}}</strong></div>
          ${{e.killer ? `<div class="death-tooltip-row"><span>Killer:</span> <strong>${{e.killer}}</strong></div>` : ''}}
        </div>
      `;
    }} else if (e.type === 'raid_boss_kill' || e.type === 'pvp_boss_kill') {{
      const isPvP = e.is_pvp || e.type === 'pvp_boss_kill';
      if (Math.abs(posX - lastBossPosX) < 90) {{
        bossStaggerIdx = (bossStaggerIdx + 1) % 5;
      }} else {{
        bossStaggerIdx = 0;
      }}
      lastBossPosX = posX;

      const stemHeight = 35 + (bossStaggerIdx * 28);
      node.className = 'timeline-node node-boss-kill';
      node.style.top = '240px';
      const pvpClass = isPvP ? ' pvp' : '';
      const labelPrefix = isPvP ? '[PvP] ' : '';
      node.innerHTML = `
        <div class="boss-kill-stem${{pvpClass}}" style="height: ${{stemHeight}}px;"></div>
        <div class="boss-kill-badge${{pvpClass}}" title="${{e.title}}">⚔️ ${{labelPrefix}}${{e.boss}}</div>
    }} else if (e.type === 'daily_zone_activity') {{
      node.className += ' node-level3-summary';
      node.style.top = '425px';
      node.style.left = Math.min(posX, width - 185) + 'px';
      node.innerHTML = `<strong style="color:var(--gold-soft);">🗺️ ${{e.total_transitions}} Transitions</strong><div style="color:var(--gray); font-size:10px;">${{e.summary}}</div>`;
    }}

    if (!(e.type === 'aa_gain' && currentZoom === 1)) {{
      node.onclick = () => openEventModal(e);
    }}
    container.appendChild(node);
  }});

  // Update Mini-Map
  updateMinimap();
}}

/* Draggable Scrubber Logic */
function setupScrubberDrag() {{
  const bar = document.getElementById('minimap-bar');
  const box = document.getElementById('minimap-viewport');

  box.addEventListener('mousedown', (e) => {{
    isDraggingScrubber = true;
    dragStartX = e.clientX;
    dragStartWindowStart = currentWindowStart;
    dragStartWindowEnd = currentWindowEnd;
    document.body.style.userSelect = 'none';
    box.style.cursor = 'grabbing';
    e.stopPropagation();
  }});

  bar.addEventListener('mousedown', (e) => {{
    const rect = bar.getBoundingClientRect();
    const clickPct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const fullMs = maxDateMs - minDateMs;
    const clickedTime = minDateMs + clickPct * fullMs;
    const span = currentWindowEnd - currentWindowStart;

    let newStart = clickedTime - span / 2;
    let newEnd = clickedTime + span / 2;
    if (newStart < minDateMs) {{
      newStart = minDateMs;
      newEnd = newStart + span;
    }}
    if (newEnd > maxDateMs) {{
      newEnd = maxDateMs;
      newStart = Math.max(minDateMs, newEnd - span);
    }}
    currentWindowStart = newStart;
    currentWindowEnd = newEnd;
    updateWindowLabel();
    renderInteractiveTimeline();

    isDraggingScrubber = true;
    dragStartX = e.clientX;
    dragStartWindowStart = currentWindowStart;
    dragStartWindowEnd = currentWindowEnd;
    document.body.style.userSelect = 'none';
    box.style.cursor = 'grabbing';
  }});

  window.addEventListener('mousemove', (e) => {{
    if (!isDraggingScrubber) return;
    const barRect = bar.getBoundingClientRect();
    const deltaPx = e.clientX - dragStartX;
    const fullMs = maxDateMs - minDateMs;
    const deltaMs = (deltaPx / barRect.width) * fullMs;
    const span = dragStartWindowEnd - dragStartWindowStart;

    let newStart = dragStartWindowStart + deltaMs;
    let newEnd = newStart + span;

    if (newStart < minDateMs) {{
      newStart = minDateMs;
      newEnd = newStart + span;
    }}
    if (newEnd > maxDateMs) {{
      newEnd = maxDateMs;
      newStart = Math.max(minDateMs, newEnd - span);
    }}

    currentWindowStart = newStart;
    currentWindowEnd = newEnd;
    updateWindowLabel();
    renderInteractiveTimeline();
  }});

  window.addEventListener('mouseup', () => {{
    if (isDraggingScrubber) {{
      isDraggingScrubber = false;
      document.body.style.userSelect = '';
      box.style.cursor = 'grab';
    }}
  }});

  // Touch support for mobile/tablets
  box.addEventListener('touchstart', (e) => {{
    if (e.touches.length === 1) {{
      isDraggingScrubber = true;
      dragStartX = e.touches[0].clientX;
      dragStartWindowStart = currentWindowStart;
      dragStartWindowEnd = currentWindowEnd;
    }}
  }}, {{ passive: true }});

  window.addEventListener('touchmove', (e) => {{
    if (!isDraggingScrubber || e.touches.length !== 1) return;
    const barRect = bar.getBoundingClientRect();
    const deltaPx = e.touches[0].clientX - dragStartX;
    const fullMs = maxDateMs - minDateMs;
    const deltaMs = (deltaPx / barRect.width) * fullMs;
    const span = dragStartWindowEnd - dragStartWindowStart;

    let newStart = dragStartWindowStart + deltaMs;
    let newEnd = newStart + span;

    if (newStart < minDateMs) {{
      newStart = minDateMs;
      newEnd = newStart + span;
    }}
    if (newEnd > maxDateMs) {{
      newEnd = maxDateMs;
      newStart = Math.max(minDateMs, newEnd - span);
    }}

    currentWindowStart = newStart;
    currentWindowEnd = newEnd;
    updateWindowLabel();
    renderInteractiveTimeline();
  }}, {{ passive: true }});

  window.addEventListener('touchend', () => {{
    isDraggingScrubber = false;
  }});
}}

function updateMinimap() {{
  const fullMs = maxDateMs - minDateMs;
  const startPct = ((currentWindowStart - minDateMs) / fullMs) * 100;
  const widthPct = Math.max(1.5, ((currentWindowEnd - currentWindowStart) / fullMs) * 100);

  const box = document.getElementById('minimap-viewport');
  box.style.left = startPct + '%';
  box.style.width = widthPct + '%';
}}

function renderOverviewTimeline() {{
  const container = document.getElementById('overview-nodes-container');
  container.innerHTML = '';

  const fullMs = maxDateMs - minDateMs;
  const trackWrapper = document.getElementById('overview-track-wrapper');
  const width = trackWrapper.clientWidth;
  container.style.width = width + 'px';

  // Overview month ticks
  let cur = new Date(minDateMs);
  cur.setDate(1);
  cur.setHours(0, 0, 0, 0);
  while (cur.getTime() < minDateMs) {{
    cur.setMonth(cur.getMonth() + 1);
  }}
  while (cur.getTime() <= maxDateMs) {{
    const pct = (cur.getTime() - minDateMs) / fullMs;
    const posX = Math.round(pct * (width - 100)) + 50;

    const tickLine = document.createElement('div');
    tickLine.className = 'axis-tick';
    tickLine.style.top = '196px';
    tickLine.style.left = posX + 'px';
    container.appendChild(tickLine);

    const tickLabel = document.createElement('div');
    tickLabel.className = 'axis-tick-label';
    tickLabel.style.top = '212px';
    tickLabel.style.left = posX + 'px';
    const m = cur.getMonth() + 1;
    const yy = String(cur.getFullYear()).slice(-2);
    tickLabel.textContent = `${{m}}/${{yy}}`;
    container.appendChild(tickLabel);

    cur.setMonth(cur.getMonth() + 1);
  }}

  // Track stagger states using 2D collision avoidance
  const placedPinnacles = [];
  const placedGuilds = [];

  // Only Level 1 events
  const l1Events = window.TIMELINE_DATA.events.level_1;

  l1Events.forEach(e => {{
    const t = new Date(e.iso || e.date || e.timestamp).getTime();
    const pct = Math.max(0, Math.min(1, (t - minDateMs) / fullMs));
    const posX = Math.round(pct * (width - 100)) + 50;

    const node = document.createElement('div');
    node.className = 'timeline-node';
    node.style.left = posX + 'px';

    if (e.type === 'level_ding') {{
      const isKey = (e.ding_level === 1 || e.ding_level === 50 || e.ding_level === 60);
      if (!isKey) return; // Keep overview clean & legible: iconic milestone dings (1, 50, 60)
      node.className += ' node-level-ding key-level';
      node.textContent = e.badge;
      node.style.top = '183px';
      node.title = `Level ${{e.ding_level}} (${{e.date}})`;
    }} else if (e.type === 'pinnacle_first') {{
      const candidateTops = [145, 100, 55, 10];
      let chosenTop = candidateTops[0];
      for (const ct of candidateTops) {{
        const collides = placedPinnacles.some(p => Math.abs(p.x - posX) < 130 && Math.abs(p.top - ct) < 35);
        if (!collides) {{
          chosenTop = ct;
          break;
        }}
      }}
      placedPinnacles.push({{ x: posX, top: chosenTop }});

      const topPos = chosenTop;
      const stemHeight = (200 - topPos) - 24;

      node.className += ' node-pinnacle';
      node.style.top = topPos + 'px';
      node.innerHTML = `
        <div class="pinnacle-badge">👑 ${{e.boss}}</div>
        <div class="pinnacle-stem" style="height: ${{stemHeight}}px;"></div>
      `;
    }} else if (e.type === 'epic_acquired') {{
      node.className += ' node-epic';
      node.style.top = '15px';
      node.innerHTML = `
        <div class="epic-badge">✨ ${{e.title || 'Epic 1.0'}}</div>
        <div class="epic-stem" style="height: 161px;"></div>
      `;
    }} else if (e.type === 'guild_join' || e.type === 'guild_leave') {{
      const candidateStems = [35, 65, 95];
      let chosenStem = candidateStems[0];
      for (const cs of candidateStems) {{
        const collides = placedGuilds.some(g => Math.abs(g.x - posX) < 120 && Math.abs(g.stem - cs) < 25);
        if (!collides) {{
          chosenStem = cs;
          break;
        }}
      }}
      placedGuilds.push({{ x: posX, stem: chosenStem }});

      const stemHeight = chosenStem;
      node.className += ' node-guild';
      node.style.top = '200px';
      node.innerHTML = `
        <div class="guild-stem" style="height: ${{stemHeight}}px;"></div>
        <div class="guild-badge">${{e.type === 'guild_join' ? '🛡️' : '🚪'}} &lt;${{e.guild}}&gt;</div>
      `;
    }}

    node.onclick = () => openEventModal(e);
    container.appendChild(node);
  }});

  // AA progression dots (non-clickable, small)
  const aas = (window.TIMELINE_DATA.events.level_2 || []).filter(e => e.type === 'aa_gain');
  aas.forEach(e => {{
    const t = new Date(e.iso || e.date || e.timestamp).getTime();
    const pct = Math.max(0, Math.min(1, (t - minDateMs) / fullMs));
    const posX = Math.round(pct * (width - 100)) + 50;

    const node = document.createElement('div');
    node.className = 'timeline-node node-aa-gain-macro overview';
    node.style.left = posX + 'px';
    container.appendChild(node);
  }});

  // Monthly boss summaries
  const monthlyBossSummaries = getMonthlyBossSummaries();
  let lastOverviewMonthPosX = -999;
  let overviewMonthStaggerIdx = 0;

  monthlyBossSummaries.forEach(e => {{
    const t = e.timestamp_ms || new Date(e.iso || e.date).getTime();
    const pct = Math.max(0, Math.min(1, (t - minDateMs) / fullMs));
    const posX = Math.round(pct * (width - 100)) + 50;

    if (Math.abs(posX - lastOverviewMonthPosX) < 110) {{
      overviewMonthStaggerIdx = (overviewMonthStaggerIdx + 1) % 3;
    }} else {{
      overviewMonthStaggerIdx = 0;
    }}
    lastOverviewMonthPosX = posX;

    const stemHeight = 95 + (overviewMonthStaggerIdx * 50); // 95px, 145px, 195px
    const node = document.createElement('div');
    node.className = 'timeline-node node-monthly-boss';
    node.style.top = '200px';
    node.style.left = posX + 'px';
    node.innerHTML = `
      <div class="monthly-boss-stem" style="height: ${{stemHeight}}px;"></div>
      <div class="monthly-boss-badge" title="Click to view all ${{e.kills.length}} boss kills in ${{e.month_name}} ${{e.year}}">
        <div class="monthly-boss-count">⚔️ ${{e.kills.length}} ${{e.kills.length === 1 ? 'Boss Kill' : 'Boss Kills'}}</div>
        <div class="monthly-boss-sample">${{e.sample_text}}</div>
      </div>
    `;
    node.onclick = () => openEventModal(e);
    container.appendChild(node);
  }});
}}

function openEventModal(e) {{
  const modal = document.getElementById('event-modal');
  const rows = document.getElementById('modal-rows');
  rows.innerHTML = '';

  const addRow = (label, val) => {{
    const r = document.createElement('div');
    r.className = 'modal-row';
    r.innerHTML = `<span class="modal-label">${{label}}</span><span class="modal-val">${{val}}</span>`;
    rows.appendChild(r);
  }};

  if (e.type === 'monthly_boss_summary') {{
    document.getElementById('modal-title').innerHTML = `👑 Boss Kills &mdash; ${{e.month_name}} ${{e.year}}`;

    addRow('Total Boss Kills', `${{e.kills.length}} (${{e.unique_boss_count}} unique bosses)`);
    addRow('Active Zones', e.zone_breakdown || 'Various');

    const killsContainer = document.createElement('div');
    killsContainer.className = 'modal-kills-list';

    e.kills.forEach(k => {{
      const item = document.createElement('div');
      item.className = 'modal-kill-item';

      const isPvP = k.is_pvp || k.type === 'pvp_boss_kill';
      const tagClass = isPvP ? 'pvp' : 'raid';
      const tagText = isPvP ? 'PvP' : 'Raid';

      const url = k.url || (k.id ? `https://www.pqdi.cc/npc/${{k.id}}` : null);
      const bossLink = url ? `<a href="${{url}}" target="_blank" style="color:var(--cyan); text-decoration:none;">${{k.boss}} &nearr;</a>` : k.boss;

      item.innerHTML = `
        <div class="modal-kill-name">
          <span class="modal-kill-tag ${{tagClass}}">${{tagText}}</span>
          <span>${{bossLink}}</span>
        </div>
        <div class="modal-kill-meta">
          <div>${{k.zone}}</div>
          <div style="font-size: 10px; color: var(--gray);">${{k.timestamp}}</div>
        </div>
      `;
      killsContainer.appendChild(item);
    }});

    rows.appendChild(killsContainer);
    modal.style.display = 'flex';
    return;
  }}

  document.getElementById('modal-title').textContent = e.title || e.type;

  // Significance Tier and Date are removed as requested. Exact timestamp preserved.
  if (e.timestamp) {{
    addRow('Exact Timestamp', e.timestamp);
  }} else if (e.iso) {{
    addRow('Exact Timestamp', e.iso.replace('T', ' '));
  }} else if (e.date) {{
    addRow('Exact Timestamp', e.date);
  }}

  const eventTypeLabel = e.is_pvp ? 'PvP Boss Kill' : (e.type === 'raid_boss_kill' ? 'Raid Boss Kill' : (e.type === 'pinnacle_first' ? 'Pinnacle Boss (First Kill)' : e.type.replace('_', ' ').toUpperCase()));
  addRow('Event Type', eventTypeLabel);
  if (e.zone) addRow('Zone', e.zone);
  if (e.guild) addRow('Guild', `&lt;${{e.guild}}&gt;`);
  if (e.boss) {{
    const url = e.url || (e.id ? `https://www.pqdi.cc/npc/${{e.id}}` : null);
    const linkStr = url ? `<a href="${{url}}" target="_blank" style="color:var(--cyan); text-decoration:none;">${{e.boss}} (pqdi.cc &nearr;)</a>` : e.boss;
    addRow('Boss', linkStr);
  }}
  if (e.killer) addRow('Killer', e.killer);
  if (e.effect) addRow('Epic Effect', e.effect);
  if (e.total_transitions) {{
    addRow('Total Transitions', e.total_transitions);
    if (e.breakdown) {{
      const bStr = Object.entries(e.breakdown).map(([z, c]) => `${{z}}: ${{c}}`).join('<br>');
      addRow('Breakdown', bStr);
    }}
  }}

  modal.style.display = 'flex';
}}

function closeModal(event) {{
  if (event && event.target && event.target.id !== 'event-modal' && !event.target.classList.contains('modal-close')) {{
    return;
  }}
  document.getElementById('event-modal').style.display = 'none';
}}

function copyOverviewImage() {{
  const btn = document.getElementById('btn-copy-overview');
  const target = document.getElementById('overview-mode-view');
  if (!target) return;

  btn.textContent = '⏳ Rendering...';

  if (window.html2canvas) {{
    html2canvas(target, {{ backgroundColor: '#101522', scale: 2 }}).then(canvas => {{
      canvas.toBlob(blob => {{
        if (navigator.clipboard && navigator.clipboard.write) {{
          navigator.clipboard.write([new ClipboardItem({{ 'image/png': blob }})]).then(() => {{
            btn.textContent = '✅ Copied to Clipboard!';
            setTimeout(() => {{ btn.textContent = '📋 Copy Image'; }}, 2500);
          }}).catch(err => {{
            downloadCanvas(canvas, 'tweedlede_timeline_overview.png');
            btn.textContent = '💾 Downloaded PNG';
            setTimeout(() => {{ btn.textContent = '📋 Copy Image'; }}, 2500);
          }});
        }} else {{
          downloadCanvas(canvas, 'tweedlede_timeline_overview.png');
          btn.textContent = '💾 Downloaded PNG';
          setTimeout(() => {{ btn.textContent = '📋 Copy Image'; }}, 2500);
        }}
      }}, 'image/png');
    }}).catch(err => {{
      console.error('html2canvas error:', err);
      downloadOverviewImage();
      btn.textContent = '📋 Copy Image';
    }});
  }} else {{
    downloadOverviewImage();
    btn.textContent = '📋 Copy Image';
  }}
}}

function downloadCanvas(canvas, filename) {{
  const a = document.createElement('a');
  a.href = canvas.toDataURL('image/png');
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}}

function downloadOverviewImage() {{
  const a = document.createElement('a');
  a.href = 'file:///C:/code/quarm-chronicle/data/sample_output/tweedlede_timeline_overview.png';
  a.download = 'tweedlede_timeline_overview.png';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}}

window.addEventListener('resize', () => {{
  if (currentMode === 'interactive') {{
    renderInteractiveTimeline();
  }} else {{
    renderOverviewTimeline();
  }}
}});

window.addEventListener('DOMContentLoaded', initTimeline);
</script>

</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Timeline HTML successfully created at {output_html}!")
    if char_key == "tweedlede":
        default_html = os.path.join(PROJECT_ROOT, "src", "cards", "timeline_card.html")
        with open(default_html, "w", encoding="utf-8") as f:
            f.write(html_content)

    return output_html

if __name__ == "__main__":
    char = sys.argv[1] if len(sys.argv) > 1 else "Tweedlede"
    build_timeline_card(char)
