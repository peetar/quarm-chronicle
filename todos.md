# Quarm Chronicle - TODOs & Roadmap

## Active Tasks
- [x] Establish project directory in `C:\code\quarm-chronicle` following EDB / OneHealth conventions.
- [x] Carry over context from previous sessions (`45637361-1200-43de-aa76-3df4f9bbbcf1` and `ab791cd5-9ea6-4f6f-a1f7-1a8cf97ee98a`).
- [x] Inspect and analyze all 4 primary character logs (`Steps`, `Thebrain`, `Tweedlede`, `Zondro`):
  - [x] `Tweedlede` (Enchanter, 272 MB, 3.68M lines) - 49 AAs, 2.5k Chardok runs, Epic Staff of the Serpent.
  - [x] `Steps` (Bard, 990 MB, 12.95M lines) - 226 AAs, 178k songs twisted, 80 Aten kills, Epic Singing Short Sword.
  - [x] `Thebrain` (Cleric, 1.22 GB, 16.03M lines) - 158 AAs, 23.6k CHs, 4.1k Rezzes, 252 Aten kills.
  - [x] `Zondro` (Necromancer, 370 MB, 4.98M lines) - 112 AAs, 17k DoTs, 1.3k FDs, 108 Aten kills, Epic Scythe.
- [x] Build core streaming parser and archive stitcher in `src/parser/` for high-speed local processing (stitching split files without high RAM usage).
- [x] Import NPC Database from `eqpetfinder` and link mobs/bosses to `https://www.pqdi.cc/npc/<id>`.
- [x] Fix Boss Overcounting: Exact canonical matching & 10-minute sliding window clustering (Aten Ha Ra: 18 for Thebrain, 9 for Zondro, 6 for Steps = 34 unique weekly guild clears).
- [x] Prototype Discord summary card template generator (`render_discord_card.py`) & re-render all 4 PNG cards.
- [x] Build unified interactive web presentation / slideshow viewer (`src/cards/roster_chronicle.html`) with live tab switching and `pqdi.cc` links.
- [x] Build multi-tier interactive timeline application (`src/cards/timeline_card.html`) with draggable mini-map scrubber, 3 zoom horizons, and date markers.
- [x] Eliminate phantom Aten Ha Ra kill for Tweedlede by enforcing in-zone verification for guild-wide broadcasts and fixing UTC date clipping.
- [x] Integrate full history of raid and PvP boss kills along the timeline axis with staggered stems and pqdi.cc tooltips in Deep Dive view.
- [x] Render high-res presentation overview snapshot image (`tools/render_timeline_image.py`) and add one-click copy-paste clipboard export.
- [x] Generalize timeline pipeline for any character (`Steps`, `Thebrain`, `Zondro`) with 2D collision avoidance and generate Steps's interactive timeline card & high-res presentation graphic.

- [x] Refactor architecture into a unified event-sourced parsing engine and Web App deployable to Vercel:
  - [x] Stream multi-gigabyte TAKP logs client-side via File System Access API (`showDirectoryPicker`) and Web Worker chunked line streamer (`src/workers/logParser.worker.ts`).
  - [x] Store parsed character bundles persistently across browser sessions in IndexedDB (`idb`).
  - [x] Build modular card registry (`src/cards/registry.ts`) and React cards (`Header`, `TopStats`, `PinnacleBosses`, `TopRaidKills`, `ClassMastery`, `AAPoints`, `MortalityNemesis`, `SecondaryClass`, `SocialCircle`, `Milestones`, `InteractiveTimeline`).
  - [x] Build 3 projection engines:
    - [x] **Chronicle Dashboard** (`SummaryProjector.tsx`): 3-column gold-bordered chronicle card grid matching original layout with high-res PNG clipboard export and standalone HTML download.
    - [x] **Card Slideshow** (`SlideshowProjector.tsx`): 1-at-a-time slide presentation with keyboard navigation.
    - [x] **Interactive Timeline** (`TimelineProjector.tsx`): Standalone full-width 3-tier timeline with mini-map scrubber and monthly kill cards.
  - [x] Pre-load demo character bundles (`Steps` and `Tweedlede`) for instant evaluation without uploading logs.
  - [x] Add Privacy & Security Modal with browser sandbox verification, read-only guarantees, and neutral MDN documentation link.
  - [x] Fix Class & Identity parsing with 3-tier detection hierarchy (/who extraction, Epic 1.0 weapon, weighted ability frequency scoring) and auto-detect race, max level, and guild.
  - [x] Isolate timeline hover effects and click triggers strictly to text boxes and badges, keeping connector stems static with zero phantom mouse interaction.
  - [x] Replace separate Overview Snapshot mode with direct 📋 Copy Image and 💾 Download PNG buttons on the interactive timeline header.
  - [x] Add monk martial arts, feign death failure tracking, and melee disciplines (Kicks landed, Mend success/fail ratio, Bandages, FD fail/spell break, and deaths immediately following failed FD).
  - [x] Add Class-based and specialized PoP AA learn/improvement milestones across week and month timeline views and chronicle dashboard with TAKP wiki database.
  - [x] Verify production Vite build (`dist/` bundle) and Python unit tests.

## Backlog Ideas
- [ ] Quarm-specific NG+ milestone tracking (Level 50 -> 1 reset detection).
- [ ] "Healer MVP" / "DPS God" card: Total healing landed / peak damage numbers.
- [ ] Item drops & iconic quest turns-ins (Epics, JBoots, Manastone, Guise, etc.).
- [ ] Cloud sync or URL sharing of parsed character bundle JSONs.
