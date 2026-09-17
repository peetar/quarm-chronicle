import os
import json
from PIL import Image, ImageDraw, ImageFont

def create_tweedlede_card(summary_json_path: str, output_image_path: str):
    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Card dimensions: 1000 x 1500 (Comprehensive Discord Chronicle Card)
    width = 1000
    height = 1500
    
    img = Image.new("RGBA", (width, height), (15, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(height):
        r = int(12 + (y / height) * 14)
        g = int(16 + (y / height) * 12)
        b = int(26 + (y / height) * 16)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Color Palette
    gold = (212, 175, 55, 255)
    gold_dark = (130, 100, 30, 255)
    gold_soft = (240, 215, 120, 255)
    cyan_glow = (56, 189, 248, 255)
    purple_glow = (192, 132, 252, 255)
    crimson = (248, 113, 113, 255)
    emerald = (74, 222, 128, 255)
    white = (248, 250, 252, 255)
    gray = (148, 163, 184, 255)
    card_bg = (22, 28, 42, 235)

    # Borders
    draw.rectangle([14, 14, width - 14, height - 14], outline=gold_dark, width=2)
    draw.rectangle([20, 20, width - 20, height - 20], outline=gold, width=3)
    draw.rectangle([26, 26, width - 26, height - 26], outline=gold_dark, width=1)

    # Corner decorations
    def draw_corner(cx, cy):
        draw.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=gold, outline=gold_dark, width=1)
        draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(15, 18, 25, 255))

    draw_corner(20, 20)
    draw_corner(width - 20, 20)
    draw_corner(20, height - 20)
    draw_corner(width - 20, height - 20)

    # Fonts
    try:
        font_tag = ImageFont.truetype("arial.ttf", 16)
        font_name = ImageFont.truetype("georgia.ttf", 54)
        font_sub = ImageFont.truetype("georgia.ttf", 23)
        font_sec = ImageFont.truetype("georgia.ttf", 22)
        font_body = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arialbd.ttf", 19)
        font_stat_big = ImageFont.truetype("georgia.ttf", 34)
        font_caption = ImageFont.truetype("arial.ttf", 15)
        font_small = ImageFont.truetype("arial.ttf", 13)
    except IOError:
        font_tag = font_name = font_sub = font_sec = font_body = font_bold = font_stat_big = font_caption = font_small = ImageFont.load_default()

    # Header
    draw.text((width // 2, 54), "PROJECT QUARM CHRONICLE", fill=gold_soft, font=font_tag, anchor="mm")
    draw.line([(220, 70), (width - 220, 70)], fill=gold_dark, width=2)

    # Title & Subtitle
    draw.text((width // 2, 112), "TWEEDLEDE", fill=white, font=font_name, anchor="mm")
    draw.text((width // 2, 155), "Level 60 Enchanter • <Dungeons and Dragons>", fill=cyan_glow, font=font_sub, anchor="mm")
    draw.text((width // 2, 183), "Jul 23, 2024 — Sep 16, 2026 • Norrathian Career Chronicle", fill=gray, font=font_caption, anchor="mm")

    # Helper: draw a framed panel
    def draw_panel(x1, y1, x2, y2, title, accent=gold):
        draw.rectangle([x1, y1, x2, y2], fill=card_bg, outline=gold_dark, width=1)
        draw.line([x1, y1, x2, y1], fill=accent, width=3)
        draw.text((x1 + 18, y1 + 12), title, fill=accent, font=font_sec)

    # Top Metric Boxes (4 Boxes)
    y_m = 205
    h_m = 100
    w_m = 215
    spacing = 15
    x_start = 40

    # Box 1: AAs
    b1_x = x_start
    draw_panel(b1_x, y_m, b1_x + w_m, y_m + h_m, "AA HARVEST", gold)
    draw.text((b1_x + w_m//2, y_m + 52), "49 AAs", fill=gold_soft, font=font_stat_big, anchor="mm")
    draw.text((b1_x + w_m//2, y_m + 80), "33 in Fungus Grove", fill=gray, font=font_small, anchor="mm")

    # Box 2: Raid Bosses
    b2_x = b1_x + w_m + spacing
    draw_panel(b2_x, y_m, b2_x + w_m, y_m + h_m, "PINNACLE BOSSES", cyan_glow)
    draw.text((b2_x + w_m//2, y_m + 52), "6 Defeated", fill=white, font=font_stat_big, anchor="mm")
    draw.text((b2_x + w_m//2, y_m + 80), "Nagafen, Vox, Phara, AoW, Vulak, Aten", fill=gray, font=font_small, anchor="mm")

    # Box 3: Chardok Entries
    b3_x = b2_x + w_m + spacing
    draw_panel(b3_x, y_m, b3_x + w_m, y_m + h_m, "CHARDOK VISITS", purple_glow)
    draw.text((b3_x + w_m//2, y_m + 52), "2,517", fill=purple_glow, font=font_stat_big, anchor="mm")
    draw.text((b3_x + w_m//2, y_m + 80), "Zone Transitions", fill=gray, font=font_small, anchor="mm")

    # Box 4: Deaths & Rezzes
    b4_x = b3_x + w_m + spacing
    draw_panel(b4_x, y_m, b4_x + w_m, y_m + h_m, "DEATH & REZ", crimson)
    draw.text((b4_x + w_m//2, y_m + 52), "561 / 225", fill=crimson, font=font_stat_big, anchor="mm")
    draw.text((b4_x + w_m//2, y_m + 80), "Deaths / Rezzes Accepted", fill=gray, font=font_small, anchor="mm")

    # Section 1: Pinnacle Bosses by Era (Left) & Top Raid Kills (Right)
    y_r1 = 320
    h_r1 = 265
    w_half = 445

    # Left: Pinnacle Bosses (Era First Kills)
    draw_panel(40, y_r1, 40 + w_half, y_r1 + h_r1, "👑 PINNACLE RAID BOSSES (FIRST KILLS)", gold)
    pinnacle_rows = [
        ("Classic", "Lord Nagafen", "Dec 02, 2024", "17 Kills"),
        ("Classic", "Lady Vox", "Dec 13, 2024", "17 Kills"),
        ("Kunark", "Phara Dar", "Sep 20, 2024", "27 Kills"),
        ("Velious", "The Avatar of War", "May 19, 2025", "5 Kills"),
        ("Velious", "Vulak`Aerr", "Aug 30, 2025", "2 Kills"),
        ("Luclin", "Aten Ha Ra", "Sep 15, 2026", "2 Kills")
    ]
    py = y_r1 + 44
    for era, bname, fdate, tkills in pinnacle_rows:
        draw.text((58, py), f"★ {bname}", fill=gold_soft, font=font_bold)
        draw.text((260, py), era, fill=gray, font=font_caption)
        draw.text((320, py), fdate, fill=white, font=font_caption)
        draw.text((40 + w_half - 18, py), tkills, fill=cyan_glow, font=font_bold, anchor="ra")
        py += 35

    # Right: Other Top Raid Boss Kills (Total Count)
    draw_panel(width - 40 - w_half, y_r1, width - 40, y_r1 + h_r1, "⚔️ TOP RAID BOSS TOTAL KILLS", cyan_glow)
    other_raids = [
        ("Venril Sathir (Karnor / HS)", "58 kills"),
        ("Cazic Thule (Plane of Fear)", "45 kills"),
        ("a dracoliche (Plane of Fear)", "45 kills"),
        ("Terror / Dread / Fright (Fear Golems)", "44 kills each"),
        ("Trakanon (Ruins of Sebilis)", "31 kills"),
        ("King Tranix & Silverwing", "42 kills combined")
    ]
    ry = y_r1 + 44
    for rname, rcount in other_raids:
        draw.text((width - 40 - w_half + 18, ry), rname, fill=white, font=font_body)
        draw.text((width - 58, ry), rcount, fill=cyan_glow, font=font_bold, anchor="ra")
        ry += 35

    # Section 2: Signature Spells (Left) & AA Harvest (Right)
    y_r2 = 600
    h_r2 = 230
    draw_panel(40, y_r2, 40 + w_half, y_r2 + h_r2, "🔮 SIGNATURE INCANTATIONS", purple_glow)
    spells = [
        ("Shallow Breath (Fast Tag/Pull)", "11,239"),
        ("Pacify (Calm Harmony)", "7,540"),
        ("Mesmerize (Crowd Control)", "6,124"),
        ("Minor Shielding (Cycle/GCD)", "5,795"),
        ("Boltran's Agacerie (Charm)", "5,537")
    ]
    sy = y_r2 + 44
    for sname, scnt in spells:
        draw.text((58, sy), sname, fill=white, font=font_body)
        draw.text((40 + w_half - 18, sy), scnt, fill=gold_soft, font=font_bold, anchor="ra")
        sy += 35

    draw_panel(width - 40 - w_half, y_r2, width - 40, y_r2 + h_r2, "🌟 AA POINTS BY ZONE", gold)
    aa_zones = [
        ("The Fungus Grove (AE Farm)", "33 AAs"),
        ("Veksar (Deep Crypts)", "9 AAs"),
        ("Ssraeshza Temple", "2 AAs"),
        ("Siren's Grotto", "2 AAs"),
        ("Acrylia / Deep / Maiden's Eye", "3 AAs")
    ]
    ay = y_r2 + 44
    for zname, acnt in aa_zones:
        draw.text((width - 40 - w_half + 18, ay), zname, fill=white, font=font_body)
        draw.text((width - 58, ay), acnt, fill=gold_soft, font=font_bold, anchor="ra")
        ay += 35

    # Section 3: Nemesis & Mortality (Left) & Top NPCs Slain (Right)
    y_r3 = 845
    h_r3 = 235
    draw_panel(40, y_r3, 40 + w_half, y_r3 + h_r3, "☠️ MORTALITY & NEMESIS", crimson)
    nemesis_lines = [
        ("PvP Arena Rival: Xebobn", "227 deaths"),
        ("Gravity / Falling Damage", "16 deaths"),
        ("Kenekn", "12 deaths"),
        ("Di`zok Royal Guards & Sages (Chardok)", "26 deaths"),
        ("Total Accepted Resurrections", "225 rezzes")
    ]
    ny = y_r3 + 44
    for nname, ncount in nemesis_lines:
        color = emerald if "Resurrections" in nname else (crimson if "227" in ncount else white)
        draw.text((58, ny), nname, fill=color, font=font_body)
        draw.text((40 + w_half - 18, ny), ncount, fill=color, font=font_bold, anchor="ra")
        ny += 35

    draw_panel(width - 40 - w_half, y_r3, width - 40, y_r3 + h_r3, "🗡️ TOP NPCS PERSONALLY SLAIN", emerald)
    slain_mobs = [
        ("escaped slave (Chardok / Droga)", "122 kills"),
        ("goblin guard", "57 kills"),
        ("bat & kobold runt", "63 kills"),
        ("wretched vanguard", "39 kills"),
        ("shackled champion & knave", "47 kills")
    ]
    sly = y_r3 + 44
    for mname, mcount in slain_mobs:
        draw.text((width - 40 - w_half + 18, sly), mname, fill=white, font=font_body)
        draw.text((width - 58, sly), mcount, fill=emerald, font=font_bold, anchor="ra")
        sly += 35

    # Section 4: Social & Companions (Full Width)
    y_r4 = 1095
    h_r4 = 175
    draw_panel(40, y_r4, width - 40, y_r4 + h_r4, "💬 COMPANIONS IN ARMS & SOCIAL CIRCLE", cyan_glow)
    
    # Left column: Group Companions & Tell Partner
    draw.text((58, y_r4 + 44), "Top Group Chat Companions:", fill=gold_soft, font=font_bold)
    draw.text((58, y_r4 + 72), "• Destu (372 msgs)   • Buffin (336 msgs)   • Tsalwin (260 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 98), "• Asirk (197 msgs)   • Thebrain (192 msgs) • Olboy (188 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 130), "Partner in Crime: Tweedledum (480 direct tells exchanged)", fill=cyan_glow, font=font_bold)

    # Right column: Raid Companions & Guild
    draw.text((540, y_r4 + 44), "Top Raid Chat Companions:", fill=gold_soft, font=font_bold)
    draw.text((540, y_r4 + 72), "• Tsalwin (2,482 msgs) • Lyric (2,395 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 98), "• Soulys (2,237 msgs)  • Poep (1,936 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 130), "Guild: <Dungeons and Dragons> (Joined Dec 17, 2024)", fill=gold_soft, font=font_bold)

    # Section 5: Expansion Firsts & Epic Quest (Full Width)
    y_r5 = 1285
    h_r5 = 150
    draw_panel(40, y_r5, width - 40, y_r5 + h_r5, "🏆 MILESTONES & EXPANSION FIRSTS", gold)
    milestones = [
        ("Staff of the Serpent (Epic 1.0)", "Sun Jan 05, 2025", "The Burning Wood / Overthere"),
        ("Ding 60 (Max Level Milestone)", "Sat Sep 28, 2024", "Skyfire Mountains (2 mos 5 days)"),
        ("First Kunark Footstep", "Thu Aug 01, 2024", "Timorous Deep"),
        ("First Velious Footstep", "Tue Apr 01, 2025", "Kael Drakkel"),
        ("First Luclin Footstep", "Sat Jul 26, 2025", "Ssraeshza Temple")
    ]
    my = y_r5 + 42
    for mtitle, mdate, mzone in milestones:
        color = gold_soft if "Epic" in mtitle or "Ding 60" in mtitle else white
        draw.text((58, my), f"★ {mtitle}", fill=color, font=font_bold)
        draw.text((430, my), mdate, fill=gray, font=font_caption)
        draw.text((width - 58, my), mzone, fill=cyan_glow, font=font_caption, anchor="ra")
        my += 20

    # Footer
    draw.text((width // 2, height - 28), "Project Quarm Chronicle • Client Logs from C:\\TAKPv22\\ • Powered by Quarm Chronicle Engine", fill=gray, font=font_caption, anchor="mm")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    img.save(output_image_path, "PNG")
    print(f"Updated card saved to {output_image_path}!")

if __name__ == "__main__":
    create_tweedlede_card(
        r"C:\code\quarm-chronicle\data\sample_output\tweedlede_summary.json",
        r"C:\code\quarm-chronicle\data\sample_output\tweedlede_chronicle_card.png"
    )
