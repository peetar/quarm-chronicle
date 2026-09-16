import os
import json
from PIL import Image, ImageDraw, ImageFont

def create_tweedlede_card(summary_json_path: str, output_image_path: str):
    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Card dimensions: 1000 x 1400 (Rich detailed Discord card)
    width = 1000
    height = 1400
    
    img = Image.new("RGBA", (width, height), (15, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(height):
        r = int(13 + (y / height) * 14)
        g = int(17 + (y / height) * 12)
        b = int(27 + (y / height) * 15)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Color Palette
    gold = (212, 175, 55, 255)
    gold_dark = (130, 100, 30, 255)
    gold_soft = (240, 215, 120, 255)
    cyan_glow = (56, 189, 248, 255)
    purple_glow = (192, 132, 252, 255)
    crimson = (248, 113, 113, 255)
    white = (248, 250, 252, 255)
    gray = (148, 163, 184, 255)
    card_bg = (22, 28, 42, 235)

    # Outer and Inner Gold Borders
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
        font_name = ImageFont.truetype("georgia.ttf", 56)
        font_sub = ImageFont.truetype("georgia.ttf", 24)
        font_sec = ImageFont.truetype("georgia.ttf", 24)
        font_body = ImageFont.truetype("arial.ttf", 19)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
        font_stat_big = ImageFont.truetype("georgia.ttf", 36)
        font_caption = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font_tag = font_name = font_sub = font_sec = font_body = font_bold = font_stat_big = font_caption = ImageFont.load_default()

    # Header
    draw.text((width // 2, 55), "PROJECT QUARM CHRONICLE", fill=gold_soft, font=font_tag, anchor="mm")
    draw.line([(220, 72), (width - 220, 72)], fill=gold_dark, width=2)

    # Title & Subtitle
    draw.text((width // 2, 115), "TWEEDLEDE", fill=white, font=font_name, anchor="mm")
    draw.text((width // 2, 160), "Level 60 Enchanter • <Dungeons and Dragons>", fill=cyan_glow, font=font_sub, anchor="mm")
    draw.text((width // 2, 190), "Jul 23, 2024 — Sep 16, 2026 • Norrathian Journey & Milestone Deck", fill=gray, font=font_caption, anchor="mm")

    # Helper: draw a framed panel
    def draw_panel(x1, y1, x2, y2, title, accent=gold):
        draw.rectangle([x1, y1, x2, y2], fill=card_bg, outline=gold_dark, width=1)
        draw.line([x1, y1, x2, y1], fill=accent, width=3)
        draw.text((x1 + 18, y1 + 14), title, fill=accent, font=font_sec)

    # Top Metric Boxes (4 Boxes)
    y_m = 215
    h_m = 110
    w_m = 215
    spacing = 15
    x_start = 40

    # Box 1: AAs Earned
    b1_x = x_start
    draw_panel(b1_x, y_m, b1_x + w_m, y_m + h_m, "AA HARVEST", gold)
    draw.text((b1_x + w_m//2, y_m + 55), "49 AAs", fill=gold_soft, font=font_stat_big, anchor="mm")
    draw.text((b1_x + w_m//2, y_m + 88), "33 in Fungus Grove", fill=gray, font=font_caption, anchor="mm")

    # Box 2: Raid Bosses
    b2_x = b1_x + w_m + spacing
    draw_panel(b2_x, y_m, b2_x + w_m, y_m + h_m, "RAID VICTORIES", cyan_glow)
    draw.text((b2_x + w_m//2, y_m + 55), "71 Bosses", fill=white, font=font_stat_big, anchor="mm")
    draw.text((b2_x + w_m//2, y_m + 88), "558 Lockouts Incurred", fill=gray, font=font_caption, anchor="mm")

    # Box 3: Chardok Entries
    b3_x = b2_x + w_m + spacing
    draw_panel(b3_x, y_m, b3_x + w_m, y_m + h_m, "TOP HAUNT", purple_glow)
    draw.text((b3_x + w_m//2, y_m + 55), "2,517", fill=purple_glow, font=font_stat_big, anchor="mm")
    draw.text((b3_x + w_m//2, y_m + 88), "Chardok Zone Transitions", fill=gray, font=font_caption, anchor="mm")

    # Box 4: Deaths
    b4_x = b3_x + w_m + spacing
    draw_panel(b4_x, y_m, b4_x + w_m, y_m + h_m, "TOTAL DEATHS", crimson)
    draw.text((b4_x + w_m//2, y_m + 55), "561", fill=crimson, font=font_stat_big, anchor="mm")
    draw.text((b4_x + w_m//2, y_m + 88), "229 in Arena PvP", fill=gray, font=font_caption, anchor="mm")

    # Row 2 Left: Signature Spells & Weaving
    y_r2 = 345
    h_r2 = 230
    w_half = 445
    draw_panel(40, y_r2, 40 + w_half, y_r2 + h_r2, "🔮 SIGNATURE INCANTATIONS", purple_glow)
    spells = [
        ("Shallow Breath (Fast Tag/Pull)", "11,239"),
        ("Pacify (Calm Harmony)", "7,540"),
        ("Mesmerize (Crowd Control)", "6,124"),
        ("Minor Shielding (Cycle/GCD)", "5,795"),
        ("Boltran's Agacerie (Charm)", "5,537")
    ]
    sy = y_r2 + 48
    for sname, scnt in spells:
        draw.text((58, sy), sname, fill=white, font=font_body)
        draw.text((40 + w_half - 18, sy), scnt, fill=gold_soft, font=font_bold, anchor="ra")
        sy += 33

    # Row 2 Right: AA Distribution by Zone
    draw_panel(width - 40 - w_half, y_r2, width - 40, y_r2 + h_r2, "🌟 AA POINTS BY ZONE", gold)
    aa_zones = [
        ("The Fungus Grove (AE Grind)", "33 AAs"),
        ("Veksar (Deep Crypts)", "9 AAs"),
        ("Ssraeshza Temple", "2 AAs"),
        ("Siren's Grotto", "2 AAs"),
        ("Acrylia / Deep / Maiden's Eye", "3 AAs")
    ]
    ay = y_r2 + 48
    for zname, acnt in aa_zones:
        draw.text((width - 40 - w_half + 18, ay), zname, fill=white, font=font_body)
        draw.text((width - 58, ay), acnt, fill=gold_soft, font=font_bold, anchor="ra")
        ay += 33

    # Row 3 Left: Guild & Social History
    y_r3 = 590
    h_r3 = 245
    draw_panel(40, y_r3, 40 + w_half, y_r3 + h_r3, "🛡️ GUILD & SOCIAL CIRCLE", cyan_glow)
    gh = [
        ("Dungeons and Dragons (Current)", "Dec 2024 – Present"),
        ("Haven (Former)", "Oct – Dec 2024"),
        ("Project Faceless (Former)", "Sep – Oct 2024"),
        ("Tweedledum (Partner in Crime)", "480 tells"),
        ("Olboy & Pinkiy", "170 tells")
    ]
    gy = y_r3 + 48
    for gname, gtime in gh:
        color = cyan_glow if "Current" in gname or "Partner" in gname else white
        draw.text((58, gy), gname, fill=color, font=font_body)
        draw.text((40 + w_half - 18, gy), gtime, fill=gray, font=font_caption, anchor="ra")
        gy += 35

    # Row 3 Right: Deadliest Locales & Danger
    draw_panel(width - 40 - w_half, y_r3, width - 40, y_r3 + h_r3, "☠️ DEADLIEST LOCALES", crimson)
    deaths_list = [
        ("an Arena (PvP Area Duels)", "229 deaths"),
        ("Chardok (AE Pulling Hazards)", "113 deaths"),
        ("Temple of Veeshan (Dragon Raid)", "23 deaths"),
        ("Plane of Fear (Instanced)", "22 deaths"),
        ("Siren's Grotto", "19 deaths")
    ]
    dy = y_r3 + 48
    for dzone, dcnt in deaths_list:
        draw.text((width - 40 - w_half + 18, dy), dzone, fill=white, font=font_body)
        draw.text((width - 58, dy), dcnt, fill=crimson, font=font_bold, anchor="ra")
        dy += 35

    # Row 4: Expansion Firsts & Epic Milestone
    y_r4 = 850
    h_r4 = 175
    draw_panel(40, y_r4, width - 40, y_r4 + h_r4, "🏆 MILESTONES & EXPANSION FIRSTS", gold)
    milestones = [
        ("Staff of the Serpent (Epic 1.0)", "Sun Jan 05, 2025", "The Burning Wood / Overthere"),
        ("Ding 60 (Max Level)", "Sat Sep 28, 2024", "Skyfire Mountains"),
        ("First Kunark Footstep", "Thu Aug 01, 2024", "Timorous Deep"),
        ("First Velious Footstep", "Tue Apr 01, 2025", "Kael Drakkel"),
        ("First Luclin Footstep", "Sat Jul 26, 2025", "Ssraeshza Temple")
    ]
    my = y_r4 + 48
    for mtitle, mdate, mzone in milestones:
        color = gold_soft if "Epic" in mtitle or "Ding 60" in mtitle else white
        draw.text((58, my), f"★ {mtitle}", fill=color, font=font_bold)
        draw.text((450, my), mdate, fill=gray, font=font_caption)
        draw.text((width - 58, my), mzone, fill=cyan_glow, font=font_caption, anchor="ra")
        my += 23

    # Row 5: Pinnacle Raid Boss Trophy Case (Attended)
    y_r5 = 1040
    h_r5 = 285
    draw_panel(40, y_r5, width - 40, y_r5 + h_r5, "⚔️ PINNACLE RAID CONQUESTS (ATTENDED)", gold)
    draw.text((58, y_r5 + 46), "71 Unique Bosses Defeated • 558 Total Lockouts Incurred • 263 In-Zone Confirmed Kills", fill=gray, font=font_caption)

    raid_sample = [
        ("The Avatar of War", "Kael Drakkel", "Statue/Idol/AoW Ring", "Multiple Lockouts"),
        ("Lord Vyemm & Dragons", "Temple of Veeshan", "North ToV Clear", "Multiple Lockouts"),
        ("King Tormax & Dain", "Kael / Thurgadin", "Faction War Lords", "Multiple Lockouts"),
        ("Trakanon & Dragons", "Sebilis / Skyfire / Dreadlands", "Nagafen, Vox, Talendor, Faydedar", "Multiple Lockouts"),
        ("Veeshan's Peak Flight", "Veeshan's Peak", "Phara Dar, Silverwing, Hoshkar, Xygoz", "Multiple Lockouts"),
        ("Luclin Horrors", "Ssra Temple / Akheva / Umbral", "Shei Vinitras, Vyzh`dra, Grieg", "Multiple Lockouts")
    ]
    ry = y_r5 + 72
    for rboss, rzone, rnote, rlock in raid_sample:
        draw.text((58, ry), f"⚔ {rboss}", fill=white, font=font_bold)
        draw.text((320, ry), rzone, fill=gray, font=font_body)
        draw.text((620, ry), rnote, fill=gold_soft, font=font_caption)
        draw.text((width - 58, ry), rlock, fill=cyan_glow, font=font_caption, anchor="ra")
        ry += 32

    # Footer
    draw.text((width // 2, height - 32), "Project Quarm Chronicle • Client Logs from C:\\TAKPv22\\ • Powered by Quarm Chronicle Parser", fill=gray, font=font_caption, anchor="mm")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    img.save(output_image_path, "PNG")
    print(f"Updated high-res card saved to {output_image_path}!")

if __name__ == "__main__":
    create_tweedlede_card(
        r"C:\code\quarm-chronicle\data\sample_output\tweedlede_summary.json",
        r"C:\code\quarm-chronicle\data\sample_output\tweedlede_chronicle_card.png"
    )
