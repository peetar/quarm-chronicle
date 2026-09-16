# Project Guidelines for Quarm Chronicle

## Workspace & Development
- **Project Root**: `C:\code\quarm-chronicle`
- **Running Tests**: Run unit tests using `python -m unittest discover tests` or `pytest`.
- **Python Environment**: Python 3.12+

## Log File Rules & Safety
- **Read-Only**: Files in `C:\TAKPv22\` are active EverQuest client logs. **NEVER modify, delete, or overwrite any file in `C:\TAKPv22\`.** Always open in read-only mode (`'r'`, `encoding='utf-8', errors='replace'`).
- **Streaming Only**: Character logs can exceed 1 GB in size. Never call `.read()` or `.readlines()` on full log files. Always stream line-by-line using chunked/buffered readers.
- **Log Format**: Project Quarm uses the TAKP / Mac client logging format:
  `[Sat Jul 06 10:11:41 2024] Event text here...`

## Code Structure Conventions
- Follow the structure modeled after `EDB` and `OneHealth`:
  - Keep architectural documentation in `docs/`.
  - Keep active tasks and progress updated in `todos.md`.
  - Put reusable parsing logic in `src/parser/` and data structures in `src/models/`.
  - Put offline exploratory scripts in `tools/`.
