import os
import sys
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HTML_FILE = os.path.join(PROJECT_ROOT, "src", "cards", "timeline_card.html")
OUTPUT_PNG = os.path.join(PROJECT_ROOT, "data", "sample_output", "tweedlede_timeline_overview.png")
ARTIFACT_DIR = r"C:\Users\peter\.gemini\antigravity\brain\371e81b8-9bbf-4304-ab1d-2b4451b7966d"
ARTIFACT_PNG = os.path.join(ARTIFACT_DIR, "tweedlede_timeline_overview.png")

POSSIBLE_BROWSER_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]

def find_browser():
    for p in POSSIBLE_BROWSER_PATHS:
        if os.path.exists(p):
            return p
    return None

def render_overview_image(character_name: str = "Tweedlede"):
    browser = find_browser()
    if not browser:
        print("Error: Chrome or Edge browser executable not found.")
        sys.exit(1)

    char_key = character_name.lower()
    html_file = os.path.join(PROJECT_ROOT, "src", "cards", f"{char_key}_timeline.html")
    output_png = os.path.join(PROJECT_ROOT, "data", "sample_output", f"{char_key}_timeline_overview.png")
    artifact_png = os.path.join(ARTIFACT_DIR, f"{char_key}_timeline_overview.png")

    if not os.path.exists(html_file):
        print(f"{html_file} not found. Running build_timeline_html.py for {character_name}...")
        from build_timeline_html import build_timeline_card
        build_timeline_card(character_name)

    os.makedirs(os.path.dirname(output_png), exist_ok=True)

    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1600,770",
        f"--screenshot={output_png}",
        f"file:///{os.path.abspath(html_file)}#snapshot"
    ]

    print(f"Rendering timeline overview snapshot for {character_name} using {os.path.basename(browser)}...")
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode == 0 and os.path.exists(output_png):
        size_kb = os.path.getsize(output_png) / 1024
        print(f"Snapshot image successfully generated at {output_png} ({size_kb:.1f} KB)")
        if os.path.exists(ARTIFACT_DIR):
            shutil.copy(output_png, artifact_png)
            print(f"Copied snapshot image to artifacts: {artifact_png}")
        return output_png
    else:
        print(f"Error rendering image. Return code: {res.returncode}")
        if res.stderr:
            print(res.stderr)
        sys.exit(1)

if __name__ == "__main__":
    char = sys.argv[1] if len(sys.argv) > 1 else "Tweedlede"
    render_overview_image(char)
