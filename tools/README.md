# Quarm Chronicle - Offline Tooling & Exploratory Scripts

This directory contains offline Python tools and scripts used for deep log exploration, reference implementations, data extraction, and offline visualization pipelines.

---

## 🛠️ Primary Utilities

### `analyze_character.py`
**Universal Character Log Analyzer CLI**
- Streams multi-gigabyte Project Quarm (TAKP) logs line-by-line with bounded memory.
- Performs multi-file chronological stitching and boundary de-duplication.
- Executes **3-Tier Character Class & Identity Resolution**:
  1. Direct `/who` entry extraction (highest authority).
  2. Epic 1.0 weapon acquisition detection.
  3. Weighted ability and signature spell frequency scoring across all 15 classes.
- Detects level milestones (1–60), AA point gains, guild history, and mortality / nemesis statistics.
- Clusters raid boss encounters using exact canonical NPC database matching and a 10-minute sliding lockout window.
- **Usage**:
  ```bash
  python tools/analyze_character.py --char Steps --log C:\TAKPv22\eqlog_Steps_pq.proj.txt --out data/sample_output/steps_summary.json
  ```

### `extract_timeline_events.py`
**3-Tier Timeline Event Generator**
- Transforms parsed summary JSON into a structured timeline schema:
  - **Tier 1 (Macro / All-Time)**: Key level dings (10, 20, 30, 40, 50, 60), Epic 1.0, Pinnacle first-time boss kills, Era transitions.
  - **Tier 2 (Seasonal / Monthly)**: All level dings, monthly raid summaries, AA point gains, first spell casts, guild joins/leaves.
  - **Tier 3 (Deep Dive / Daily)**: Full chronological raid boss kills, PvP encounters, character deaths, and casualty details.
- **Usage**:
  ```bash
  python tools/extract_timeline_events.py --summary data/sample_output/steps_summary.json --out data/sample_output/steps_timeline.json
  ```

### `build_timeline_html.py`
**Standalone Timeline HTML Builder**
- Injects character metadata, events, and era transitions into `src/cards/timeline_card.html` to generate a self-contained, portable HTML timeline with interactive zoom, scrubbing, and event inspection.
- **Usage**:
  ```bash
  python tools/build_timeline_html.py --data data/sample_output/steps_timeline.json --out dist/steps_timeline.html
  ```

### `render_timeline_image.py`
**Timeline Presentation Graphic Renderer**
- Headless snapshot generator that renders high-resolution (2x) PNG presentation cards of the timeline overview using Playwright / headless Chromium.
- **Usage**:
  ```bash
  python tools/render_timeline_image.py --html dist/steps_timeline.html --out data/sample_output/steps_timeline_overview.png
  ```

---

## 🔬 Exploratory & Verification Scripts

| Script | Purpose |
| :--- | :--- |
| `inspect_logs.py` | Inspects the first/last 64 KB of active and archived TAKP logs to detect date bounds and file seams without loading multi-gigabyte files. |
| `search_patterns.py` | Fast regex search utility for probing TAKP log syntax, channel formats, and unusual message variants. |
| `explore_social_and_kills.py` | Extracts tell networks, guild roster interactions, and kill participation across multi-gigabyte character histories. |
| `test_npc_db.py` | Verifies mob name matching, alias resolution, and pqdi.cc database URL generation against the canonical NPC database. |
| `test_raid_involvement.py` | Tests raid kill attribution rules (in-zone verification, death broadcasts vs. personal melee involvement) and clustering time windows. |
| `verify_nuances.py` | Validates edge-case log conditions: anonymous players, roleplay tags, death loop edge cases, and zone transition stamps. |
| `inspect_sql_dump.py` | Inspects and extracts NPC tables from Project Quarm / TAKP database dumps. |
| `analyze_tweedlede.py` | Initial prototype analyzer for Tweedlede, preserved as a historical reference implementation. |
