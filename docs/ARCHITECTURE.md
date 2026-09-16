# System Architecture

## Overview

Project Quarm Chronicle is designed to transform massive raw EverQuest chat/combat logs into digestible, shareable story highlights and social graphics.

```
┌────────────────────────────────────────────────────────┐
│                   Raw EverQuest Logs                   │
│          (C:\TAKPv22\eqlog_<Character>_pq.proj.txt)    │
│                     (Hundreds of MB - GBs)             │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              High-Throughput Stream Parser             │
│        (Regex line matching, timestamp parsing,        │
│          sliding windows for multi-line events)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               Aggregator & Event Engine                │
│   • Level progression milestones (Dings, NG+ resets)   │
│   • Boss slain & first kills                           │
│   • Tell frequency & social graphs                     │
│   • Damage / Healing / Critical records                │
│   • Death records & falling damage tally               │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Event Summary JSON                     │
│     (Compact ~10-50 KB dataset describing the journey) │
└───────────────────────────┬────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│   Discord Card Exporter   │ │  Web Slideshow Viewer    │
│  (PNG cards: Stats, Ding  │ │ (Interactive timeline,   │
│   Milestones, Social Top) │ │  sound FX, full journey) │
└───────────────────────────┘ └──────────────────────────┘
```

## Key Principles

1. **Local-First Processing**: Multi-gigabyte logs are never uploaded over the network. All raw text parsing happens locally on the player's desktop machine.
2. **Deterministic Mathematical Accuracy**: Counts, damage numbers, kill lists, and timestamps are calculated with deterministic code, not probabilistic models.
3. **Structured Interchange Format**: The parser yields a clean JSON schema (`ChronicleSummary`) that powers both image export and web interfaces.
4. **Rich Visual Styling**: The visual output draws inspiration from classic EverQuest aesthetic—dark velvet UI, parchment paper, brass/gold borders, spell gem accents, and retro pixel icons.
