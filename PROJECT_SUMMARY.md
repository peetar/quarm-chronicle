# Project Quarm Chronicle - Project Summary

**Quick Context Document for AI Assistants**

## TL;DR

EverQuest log parser and milestone storybook / "Wrapped" generator | Project Quarm (TAKP client) | Fast deterministic parsing + shareable social cards (Discord / Web) | Python / TypeScript

## Core Concept

Players on Project Quarm (a classic EverQuest emulated progression server) accumulate multi-gigabyte client log files spanning months or years. **Project Quarm Chronicle** extracts a player's journey from these logs and generates:
1. **Milestone Timeline**: Level dings, NG+ resets, first-time raid boss encounters/kills, epic quest item hand-ins.
2. **Combat Highlights**: Total damage dealt/healed, record critical hits, memorable deaths, falling damage tally.
3. **Social & Community Stats**: Top tell partners, favorite group members, guild joining/promotions, rivals.
4. **Shareable Output**: Discord-ready summary graphics (PNG cards), web recap slideshow, and optional narrative flavor text.

## Tech Stack

- **Core Parsing Engine**: Python 3.12 (high-throughput streaming regex line scanner for multi-GB logs) / JavaScript Web Worker for client-side web mode.
- **Data Models**: Typed event schemas for milestones, dings, combat records, and social interactions.
- **Card Generation**: HTML Canvas / SVG / Satori / Pillow for high-res Discord social cards.
- **Presentation Layer**: Interactive web timeline / slideshow (React / Vite or standalone static HTML).

## Project Structure (Key Paths)

```
c:\code\quarm-chronicle\
├── docs/                 # Architectural specs & design guides
│   ├── ARCHITECTURE.md   # System pipeline (Parser -> Event Summary JSON -> Card Exporter)
│   ├── LOG_SPECIFICATION.md # EQ TAKP log formats & Quarm-specific syntax
│   └── MILESTONE_IDEAS.md # Card concepts & milestone catalog
├── src/                  # Source code
│   ├── parser/           # Streaming log parser & regex matchers
│   ├── models/           # Data models (Event, Milestone, CharacterProfile)
│   └── cards/            # Card rendering & layout templates
├── tools/                # Analysis & log inspection utilities
├── tests/                # Unit tests for log parsing & edge cases
├── data/                 # Sample fixtures & reference dictionaries
│   ├── reference/        # Zone names, boss lists, item databases
│   └── sample_output/    # Generated JSON / card outputs
├── todos.md              # Current task tracking
├── AGENTS.md             # Guidelines for AI coding agents
├── PROJECT_SUMMARY.md    # Quick context overview (this file)
└── README.md             # Public project overview
```

## Data Sources & Local Paths

- **TAKP / Quarm Game Client Directory**: `C:\TAKPv22\`
- **Key Character Logs**:
  - `eqlog_Steps_pq.proj.txt` (~1.03 GB) — Bard
  - `eqlog_Thebrain_pq.proj.txt` (~455 MB + 819 MB archive)
  - `eqlog_Tweedlede_pq.proj.txt` (~285 MB)
  - `eqlog_Zondro_pq.proj.txt` (~264 MB)

## Session History & Context

- **Mac Origin Session**: `45637361-1200-43de-aa76-3df4f9bbbcf1` (`\\192.168.68.100\antigravity\brain\45637361-1200-43de-aa76-3df4f9bbbcf1`)
- **Desktop Transfer Session**: `ab791cd5-9ea6-4f6f-a1f7-1a8cf97ee98a`
