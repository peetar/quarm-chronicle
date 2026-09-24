import os
import re
import glob
from datetime import datetime
from typing import List, Dict, Generator, Tuple

TS_RE = re.compile(r"^\[(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})\]")
TIME_FORMAT = "%a %b %d %H:%M:%S %Y"

class LogFileInfo:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.size_bytes = os.path.getsize(file_path)
        self.first_dt = None
        self.last_dt = None
        self.first_ts_str = None
        self.last_ts_str = None
        self._inspect_timestamps()

    def _inspect_timestamps(self):
        if self.size_bytes == 0:
            return
        
        # Read first timestamp
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = TS_RE.match(line)
                if m:
                    self.first_ts_str = m.group("ts")
                    try:
                        self.first_dt = datetime.strptime(self.first_ts_str, TIME_FORMAT)
                    except ValueError:
                        pass
                    break
        
        # Read last timestamp by seeking near end of file
        with open(self.file_path, "rb") as f:
            seek_pos = max(0, self.size_bytes - 65536)
            f.seek(seek_pos)
            tail_lines = f.read().decode("utf-8", errors="replace").splitlines()
            for line in reversed(tail_lines):
                m = TS_RE.match(line)
                if m:
                    self.last_ts_str = m.group("ts")
                    try:
                        self.last_dt = datetime.strptime(self.last_ts_str, TIME_FORMAT)
                    except ValueError:
                        pass
                    break

    def __repr__(self):
        return (f"<LogFileInfo {os.path.basename(self.file_path)}: "
                f"{self.first_ts_str} -> {self.last_ts_str} ({self.size_bytes / (1024*1024):.1f} MB)>")


class LogStitcher:
    """
    Discovers, chronologically sorts, and seamlessly stitches together split and archived
    character log files without reading full gigabytes into memory.
    """
    def __init__(self, base_dir: str, character_name: str):
        self.base_dir = base_dir
        self.character_name = character_name
        self.file_infos: List[LogFileInfo] = []
        self._discover_files()

    def _discover_files(self):
        patterns = [
            os.path.join(self.base_dir, f"eqlog_{self.character_name}_pq.proj*.txt"),
            os.path.join(self.base_dir, "log_archive", f"eqlog_{self.character_name}_*.txt")
        ]
        
        found_paths = set()
        for pat in patterns:
            for p in glob.glob(pat):
                if " - Copy" in p:
                    continue
                found_paths.add(p)

        infos = []
        for p in found_paths:
            try:
                info = LogFileInfo(p)
                if info.first_dt and info.last_dt:
                    infos.append(info)
            except (PermissionError, OSError):
                continue

        # Sort chronologically by first timestamp
        infos.sort(key=lambda x: x.first_dt)
        self.file_infos = infos

    def get_summary(self) -> List[Dict]:
        return [
            {
                "file": os.path.basename(fi.file_path),
                "path": fi.file_path,
                "size_mb": round(fi.size_bytes / (1024 * 1024), 2),
                "start": fi.first_ts_str,
                "end": fi.last_ts_str
            }
            for fi in self.file_infos
        ]

    def stream_lines(self) -> Generator[str, None, None]:
        """
        Yields lines across all files in chronological order.
        Only de-duplicates across file transitions (if file N+1 begins before file N ended).
        """
        prev_file_end_dt = None

        for fi in self.file_infos:
            print(f"[LogStitcher] Streaming {os.path.basename(fi.file_path)}...")
            with open(fi.file_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if prev_file_end_dt:
                        m = TS_RE.match(line)
                        if m:
                            try:
                                dt = datetime.strptime(m.group("ts"), TIME_FORMAT)
                                if dt <= prev_file_end_dt:
                                    continue
                            except ValueError:
                                pass
                    yield line
            prev_file_end_dt = fi.last_dt
