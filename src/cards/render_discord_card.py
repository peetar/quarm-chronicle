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
        ("Classic", "Lord Nagafen", "Dec 02, 2024", "5 Kills"),
        ("Classic", "Lady Vox", "Dec 13, 2024", "5 Kills"),
        ("Kunark", "Phara Dar", "Sep 20, 2024", "12 Kills"),
        ("Velious", "The Avatar of War", "May 19, 2025", "2 Kills"),
        ("Velious", "Vulak`Aerr", "Aug 30, 2025", "2 Kills"),
        ("Luclin", "Aten Ha Ra", "Sep 15, 2026", "1 Kill")
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
        ("Venril Sathir (Karnor / HS)", "23 kills"),
        ("a dracoliche (Plane of Fear)", "16 kills"),
        ("Terror / Dread / Fright (Fear)", "15 kills each"),
        ("Cazic Thule (Plane of Fear)", "15 kills"),
        ("Trakanon (Ruins of Sebilis)", "13 kills"),
        ("King Tranix (SolB)", "13 kills")
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
        ("Shallow Breath", "11,239"),
        ("Pacify", "7,540"),
        ("Mesmerize", "6,124"),
        ("Minor Shielding", "5,795"),
        ("Boltran's Agacerie", "5,537")
    ]
    sy = y_r2 + 44
    for sname, scnt in spells:
        draw.text((58, sy), sname, fill=white, font=font_body)
        draw.text((40 + w_half - 18, sy), scnt, fill=gold_soft, font=font_bold, anchor="ra")
        sy += 35

    draw_panel(width - 40 - w_half, y_r2, width - 40, y_r2 + h_r2, "🌟 AA POINTS BY ZONE", gold)
    aa_zones = [
        ("The Fungus Grove", "33 AAs"),
        ("Veksar", "9 AAs"),
        ("Ssraeshza Temple", "2 AAs"),
        ("Siren's Grotto", "2 AAs"),
        ("The Maiden's Eye", "3 AAs")
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
        ("Arena Rival: Xebobn", "227 deaths"),
        ("Gravity / Bleeding", "16 deaths"),
        ("Kenekn", "12 deaths"),
        ("Di`zok Royal Guards & Sages", "26 deaths"),
        ("Accepted Resurrections", "225 rezzes")
    ]
    ny = y_r3 + 44
    for nname, ncount in nemesis_lines:
        color = emerald if "Resurrections" in nname else (crimson if "227" in ncount else white)
        draw.text((58, ny), nname, fill=color, font=font_body)
        draw.text((40 + w_half - 18, ny), ncount, fill=color, font=font_bold, anchor="ra")
        ny += 35

    draw_panel(width - 40 - w_half, y_r3, width - 40, y_r3 + h_r3, "🗡️ TOP NPCS PERSONALLY SLAIN", emerald)
    slain_mobs = [
        ("escaped slave", "122 kills"),
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
        ("Staff of the Serpent", "Sun Jan 05, 2025", "The Burning Wood / Overthere"),
        ("Ding 60", "Sat Sep 28, 2024", "Skyfire Mountains"),
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
    print(f"Tweedlede card saved to {output_image_path}!")

def create_steps_card(summary_json_path: str, output_image_path: str):
    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Card dimensions: 1000 x 1500 (Comprehensive Discord Chronicle Card)
    width = 1000
    height = 1500
    
    img = Image.new("RGBA", (width, height), (15, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(height):
        r = int(10 + (y / height) * 12)
        g = int(18 + (y / height) * 16)
        b = int(24 + (y / height) * 20)
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
    card_bg = (20, 28, 44, 235)

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
    draw.text((width // 2, 112), "STEPS", fill=white, font=font_name, anchor="mm")
    draw.text((width // 2, 155), "Level 60 Bard • <Dungeons and Dragons>", fill=cyan_glow, font=font_sub, anchor="mm")
    draw.text((width // 2, 183), "Jul 06, 2024 — Sep 16, 2026 • Norrathian Career Chronicle", fill=gray, font=font_caption, anchor="mm")

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
    draw.text((b1_x + w_m//2, y_m + 52), "226 AAs", fill=gold_soft, font=font_stat_big, anchor="mm")
    draw.text((b1_x + w_m//2, y_m + 80), "125 in Fungus Grove", fill=gray, font=font_small, anchor="mm")

    # Box 2: Pinnacle Bosses
    b2_x = b1_x + w_m + spacing
    draw_panel(b2_x, y_m, b2_x + w_m, y_m + h_m, "PINNACLE CONQUEST", cyan_glow)
    draw.text((b2_x + w_m//2, y_m + 52), "7 Defeated", fill=white, font=font_stat_big, anchor="mm")
    draw.text((b2_x + w_m//2, y_m + 80), "25 AoW • 22 Tunare • 19 Phara", fill=gray, font=font_small, anchor="mm")

    # Box 3: Bard Twisting Maestro
    b3_x = b2_x + w_m + spacing
    draw_panel(b3_x, y_m, b3_x + w_m, y_m + h_m, "TWISTING MAESTRO", purple_glow)
    draw.text((b3_x + w_m//2, y_m + 52), "178,904", fill=purple_glow, font=font_stat_big, anchor="mm")
    draw.text((b3_x + w_m//2, y_m + 80), "Songs Twisted • 83k Selos", fill=gray, font=font_small, anchor="mm")

    # Box 4: Deaths & Rezzes
    b4_x = b3_x + w_m + spacing
    draw_panel(b4_x, y_m, b4_x + w_m, y_m + h_m, "DEATH & REZ", crimson)
    draw.text((b4_x + w_m//2, y_m + 52), "433 / 276", fill=crimson, font=font_stat_big, anchor="mm")
    draw.text((b4_x + w_m//2, y_m + 80), "64% Rez Recovery Rate", fill=gray, font=font_small, anchor="mm")

    # Section 1: Pinnacle Bosses by Era (Left) & Top Raid Kills (Right)
    y_r1 = 320
    h_r1 = 265
    w_half = 445

    # Left: Pinnacle Bosses (Era First Kills)
    draw_panel(40, y_r1, 40 + w_half, y_r1 + h_r1, "👑 PINNACLE RAID BOSSES (FIRST KILLS)", gold)
    pinnacle_rows = [
        ("Classic", "Lord Nagafen", "Aug 14, 2025", "3 Kills"),
        ("Classic", "Lady Vox", "Aug 14, 2025", "5 Kills"),
        ("Kunark", "Phara Dar", "Mar 29, 2025", "19 Kills"),
        ("Velious", "The Avatar of War", "May 12, 2025", "25 Kills"),
        ("Velious", "Tunare", "Aug 19, 2025", "22 Kills"),
        ("Velious", "Vulak`Aerr", "Sep 13, 2025", "10 Kills"),
        ("Luclin", "Aten Ha Ra", "Jan 13, 2026", "6 Kills")
    ]
    py = y_r1 + 44
    for era, bname, fdate, tkills in pinnacle_rows:
        draw.text((58, py), f"★ {bname}", fill=gold_soft, font=font_bold)
        draw.text((260, py), era, fill=gray, font=font_caption)
        draw.text((320, py), fdate, fill=white, font=font_caption)
        draw.text((40 + w_half - 18, py), tkills, fill=cyan_glow, font=font_bold, anchor="ra")
        py += 30

    # Right: Other Top Raid Boss Kills (Total Count)
    # Right: Other Top Raid Boss Kills (Total Count)
    draw_panel(width - 40 - w_half, y_r1, width - 40, y_r1 + h_r1, "⚔️ TOP RAID BOSS TOTAL KILLS", cyan_glow)
    other_raids = [
        ("Derakor the Vindicator", "38 kills"),
        ("The Statue of Rallos Zek", "36 kills"),
        ("King Tormax", "36 kills"),
        ("The Idol of Rallos Zek", "27 kills"),
        ("Dozekar the Cursed", "26 kills"),
        ("Sleeper's Tomb Warders", "85 kills")
    ]
    ry = y_r1 + 44
    for rname, rcount in other_raids:
        draw.text((width - 40 - w_half + 18, ry), rname, fill=white, font=font_body)
        draw.text((width - 58, ry), rcount, fill=cyan_glow, font=font_bold, anchor="ra")
        ry += 35

    # Section 2: Bard Repertoire (Left) & AA Harvest (Right)
    y_r2 = 600
    h_r2 = 230
    draw_panel(40, y_r2, 40 + w_half, y_r2 + h_r2, "🎵 THE BARD'S REPERTOIRE", purple_glow)
    songs = [
        ("Selo`s Accelerating Chorus", "875 mems"),
        ("Largo`s Absonant Binding", "641 mems"),
        ("Fufil`s Curtailing Chant", "541 mems"),
        ("Solon's Bewitching Bravura", "489 mems"),
        ("Occlusion of Sound", "470 mems")
    ]
    sy = y_r2 + 44
    for sname, scnt in songs:
        draw.text((58, sy), sname, fill=white, font=font_body)
        draw.text((40 + w_half - 18, sy), scnt, fill=gold_soft, font=font_bold, anchor="ra")
        sy += 35

    draw_panel(width - 40 - w_half, y_r2, width - 40, y_r2 + h_r2, "🌟 AA POINTS BY ZONE", gold)
    aa_zones = [
        ("The Fungus Grove", "125 AAs"),
        ("Grieg's End", "31 AAs"),
        ("The Maiden's Eye", "14 AAs"),
        ("Veksar", "10 AAs"),
        ("Ssraeshza, Sebilis & Acrylia", "19 AAs")
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
        ("a Shik`nar Forager", "24 deaths"),
        ("Shik`nar Soldier", "13 deaths"),
        ("a gyrating goo", "12 deaths"),
        ("Fright", "11 deaths"),
        ("Missed Notes", "28,409 flubs")
    ]
    ny = y_r3 + 44
    for nname, ncount in nemesis_lines:
        color = crimson if "24" in ncount else (purple_glow if "Flubs" in nname else white)
        draw.text((58, ny), nname, fill=color, font=font_body)
        draw.text((40 + w_half - 18, ny), ncount, fill=color, font=font_bold, anchor="ra")
        ny += 35

    draw_panel(width - 40 - w_half, y_r3, width - 40, y_r3 + h_r3, "🗡️ LEVELING ROOTS (TOP SLAIN)", emerald)
    slain_mobs = [
        ("orc centurion", "132 kills"),
        ("Dervish Cutthroat", "70 kills"),
        ("caiman & crocodiles", "114 kills"),
        ("young kodiak", "24 kills"),
        ("orc apprentice & oracle", "47 kills")
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
    draw.text((58, y_r4 + 72), "• Tsalwin (1,109 msgs)  • Buffin (584 msgs)  • Pinkiy (322 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 98), "• Beta (254 msgs)       • Destu (245 msgs)   • Evocate (239 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 130), "Partner in Crime: Pinkiy (1,121 direct tells exchanged)", fill=cyan_glow, font=font_bold)

    # Right column: Raid Companions & Guild
    draw.text((540, y_r4 + 44), "Top Raid Chat Companions:", fill=gold_soft, font=font_bold)
    draw.text((540, y_r4 + 72), "• Tsalwin (15,944 msgs) • Poep (9,462 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 98), "• Lyric (6,751 msgs)    • Soulys (5,633 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 130), "Guild: <Dungeons and Dragons> (Joined Jan 18, 2025)", fill=gold_soft, font=font_bold)

    # Section 5: Expansion Firsts & Epic Quest (Full Width)
    y_r5 = 1285
    h_r5 = 150
    draw_panel(40, y_r5, width - 40, y_r5 + h_r5, "🏆 MILESTONES & EXPANSION FIRSTS", gold)
    milestones = [
        ("Singing Short Sword", "Sun Mar 23, 2025", "The Dreadlands"),
        ("Ding 60", "Tue Mar 25, 2025", "The City of Mist"),
        ("First Kunark Footstep", "Sat Jul 06, 2024", "Timorous Deep"),
        ("First Velious Footstep", "Tue Apr 01, 2025", "Kael Drakkel"),
        ("First Luclin Footstep", "Fri Jul 25, 2025", "Nexus")
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
    print(f"Steps card saved to {output_image_path}!")

def create_thebrain_card(summary_json_path: str, output_image_path: str):
    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    width = 1000
    height = 1500
    
    img = Image.new("RGBA", (width, height), (15, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient - Divine Ivory & Midnight Slate
    for y in range(height):
        r = int(14 + (y / height) * 14)
        g = int(16 + (y / height) * 16)
        b = int(28 + (y / height) * 22)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    gold = (212, 175, 55, 255)
    gold_dark = (130, 100, 30, 255)
    gold_soft = (240, 215, 120, 255)
    cyan_glow = (56, 189, 248, 255)
    purple_glow = (192, 132, 252, 255)
    crimson = (248, 113, 113, 255)
    emerald = (74, 222, 128, 255)
    white = (248, 250, 252, 255)
    gray = (148, 163, 184, 255)
    card_bg = (20, 26, 42, 235)

    draw.rectangle([14, 14, width - 14, height - 14], outline=gold_dark, width=2)
    draw.rectangle([20, 20, width - 20, height - 20], outline=gold, width=3)
    draw.rectangle([26, 26, width - 26, height - 26], outline=gold_dark, width=1)

    def draw_corner(cx, cy):
        draw.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=gold, outline=gold_dark, width=1)
        draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(15, 18, 25, 255))

    draw_corner(20, 20)
    draw_corner(width - 20, 20)
    draw_corner(20, height - 20)
    draw_corner(width - 20, height - 20)

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

    draw.text((width // 2, 54), "PROJECT QUARM CHRONICLE", fill=gold_soft, font=font_tag, anchor="mm")
    draw.line([(220, 70), (width - 220, 70)], fill=gold_dark, width=2)

    draw.text((width // 2, 112), "THEBRAIN", fill=white, font=font_name, anchor="mm")
    draw.text((width // 2, 155), "Level 60 Halfling Cleric • <Dungeons and Dragons>", fill=cyan_glow, font=font_sub, anchor="mm")
    draw.text((width // 2, 183), "Sep 29, 2024 — Sep 17, 2026 • Norrathian Career Chronicle", fill=gray, font=font_caption, anchor="mm")

    def draw_panel(x1, y1, x2, y2, title, accent=gold):
        draw.rectangle([x1, y1, x2, y2], fill=card_bg, outline=gold_dark, width=1)
        draw.line([x1, y1, x2, y1], fill=accent, width=3)
        draw.text((x1 + 18, y1 + 12), title, fill=accent, font=font_sec)

    y_m = 205
    h_m = 100
    w_m = 215
    spacing = 15
    x_start = 40

    b1_x = x_start
    draw_panel(b1_x, y_m, b1_x + w_m, y_m + h_m, "COMPLETE HEALS", gold)
    draw.text((b1_x + w_m//2, y_m + 52), "23,639", fill=gold_soft, font=font_stat_big, anchor="mm")
    draw.text((b1_x + w_m//2, y_m + 80), "Heartbeat of the Raid", fill=gray, font=font_small, anchor="mm")

    b2_x = b1_x + w_m + spacing
    draw_panel(b2_x, y_m, b2_x + w_m, y_m + h_m, "LIFESAVING REZZES", emerald)
    draw.text((b2_x + w_m//2, y_m + 52), "4,120 Rezzes", fill=emerald, font=font_stat_big, anchor="mm")
    draw.text((b2_x + w_m//2, y_m + 80), "3,979 Reviviscence", fill=gray, font=font_small, anchor="mm")

    b3_x = b2_x + w_m + spacing
    draw_panel(b3_x, y_m, b3_x + w_m, y_m + h_m, "PINNACLE CONQUEST", cyan_glow)
    draw.text((b3_x + w_m//2, y_m + 52), "7 Defeated", fill=white, font=font_stat_big, anchor="mm")
    draw.text((b3_x + w_m//2, y_m + 80), "18 Aten • 25 Phara • 16 AoW", fill=gray, font=font_small, anchor="mm")

    b4_x = b3_x + w_m + spacing
    draw_panel(b4_x, y_m, b4_x + w_m, y_m + h_m, "DEATH & REZ", crimson)
    draw.text((b4_x + w_m//2, y_m + 52), "230 / 205", fill=crimson, font=font_stat_big, anchor="mm")
    draw.text((b4_x + w_m//2, y_m + 80), "89.1% Rez Recovery Rate", fill=gray, font=font_small, anchor="mm")

    y_r1 = 320
    h_r1 = 265
    w_half = 445

    draw_panel(40, y_r1, 40 + w_half, y_r1 + h_r1, "👑 PINNACLE RAID BOSSES (FIRST KILLS)", gold)
    pinnacle_rows = [
        ("Classic", "Lord Nagafen", "Oct 28, 2024", "13 Kills"),
        ("Classic", "Lady Vox", "Jan 31, 2025", "5 Kills"),
        ("Kunark", "Phara Dar", "Nov 19, 2024", "25 Kills"),
        ("Velious", "The Avatar of War", "Apr 25, 2025", "16 Kills"),
        ("Velious", "Tunare", "May 31, 2025", "14 Kills"),
        ("Velious", "Vulak`Aerr", "Jun 13, 2025", "6 Kills"),
        ("Luclin", "Aten Ha Ra", "Jan 06, 2026", "18 Kills")
    ]
    py = y_r1 + 44
    for era, bname, fdate, tkills in pinnacle_rows:
        draw.text((58, py), f"★ {bname}", fill=gold_soft, font=font_bold)
        draw.text((260, py), era, fill=gray, font=font_caption)
        draw.text((320, py), fdate, fill=white, font=font_caption)
        draw.text((40 + w_half - 18, py), tkills, fill=cyan_glow, font=font_bold, anchor="ra")
        py += 30

    draw_panel(width - 40 - w_half, y_r1, width - 40, y_r1 + h_r1, "⚔️ TOP RAID BOSS TOTAL KILLS", cyan_glow)
    other_raids = [
        ("Kaas Thox Xi Aten Ha Ra", "36 kills"),
        ("Vyzh`dra the Cursed", "35 kills"),
        ("Vyzh`dra the Exiled", "33 kills"),
        ("Blood of Ssraeshza", "29 kills"),
        ("a glyph covered serpent", "28 kills"),
        ("Emperor Ssraeshza", "26 kills")
    ]
    ry = y_r1 + 44
    for rname, rcount in other_raids:
        draw.text((width - 40 - w_half + 18, ry), rname, fill=white, font=font_body)
        draw.text((width - 58, ry), rcount, fill=cyan_glow, font=font_bold, anchor="ra")
        ry += 35

    y_r2 = 600
    h_r2 = 230
    draw_panel(40, y_r2, 40 + w_half, y_r2 + h_r2, "🕊️ HOLY LITURGY & HEALING", emerald)
    spells = [
        ("Complete Healing", "23,639 casts"),
        ("Greater Healing", "10,442 casts"),
        ("Reviviscence", "3,979 casts"),
        ("Heroic Bond & Aegolism", "1,357 casts"),
        ("Divine Intervention", "169 casts")
    ]
    sy = y_r2 + 44
    for sname, scnt in spells:
        draw.text((58, sy), sname, fill=white, font=font_body)
        draw.text((40 + w_half - 18, sy), scnt, fill=emerald, font=font_bold, anchor="ra")
        sy += 35

    draw_panel(width - 40 - w_half, y_r2, width - 40, y_r2 + h_r2, "🌟 AA POINTS BY ZONE", gold)
    aa_zones = [
        ("The Maiden's Eye", "62 AAs"),
        ("Ssraeshza Temple", "39 AAs"),
        ("The Deep", "22 AAs"),
        ("Sanctus Seru", "9 AAs"),
        ("Acrylia Caverns", "9 AAs")
    ]
    ay = y_r2 + 44
    for zname, acnt in aa_zones:
        draw.text((width - 40 - w_half + 18, ay), zname, fill=white, font=font_body)
        draw.text((width - 58, ay), acnt, fill=gold_soft, font=font_bold, anchor="ra")
        ay += 35

    y_r3 = 845
    h_r3 = 235
    draw_panel(40, y_r3, 40 + w_half, y_r3 + h_r3, "☠️ MORTALITY & NEMESIS", crimson)
    nemesis_lines = [
        ("Hoshkar", "13 deaths"),
        ("Emperor Ssraeshza", "10 deaths"),
        ("Ventani the Warder", "6 deaths"),
        ("The Avatar of War", "5 deaths"),
        ("Accepted Resurrections", "205 rezzes")
    ]
    ny = y_r3 + 44
    for nname, ncount in nemesis_lines:
        color = emerald if "Resurrections" in nname else (crimson if "13" in ncount or "10" in ncount else white)
        draw.text((58, ny), nname, fill=color, font=font_body)
        draw.text((40 + w_half - 18, ny), ncount, fill=color, font=font_bold, anchor="ra")
        ny += 35

    draw_panel(width - 40 - w_half, y_r3, width - 40, y_r3 + h_r3, "🗡️ BLESSED COMBAT & CROWD CONTROL", cyan_glow)
    combat_lines = [
        ("Immobilize", "8,743 casts"),
        ("Yaulp V", "4,686 casts"),
        ("Strike", "3,552 casts"),
        ("Pacify", "3,524 casts"),
        ("Ethereal Remedy & Light", "9,631 casts")
    ]
    sly = y_r3 + 44
    for mname, mcount in combat_lines:
        draw.text((width - 40 - w_half + 18, sly), mname, fill=white, font=font_body)
        draw.text((width - 58, sly), mcount, fill=cyan_glow, font=font_bold, anchor="ra")
        sly += 35

    y_r4 = 1095
    h_r4 = 175
    draw_panel(40, y_r4, width - 40, y_r4 + h_r4, "💬 COMPANIONS IN ARMS & SOCIAL CIRCLE", cyan_glow)
    
    draw.text((58, y_r4 + 44), "Top Group Chat Companions:", fill=gold_soft, font=font_bold)
    draw.text((58, y_r4 + 72), "• Destu (632 msgs)   • Buffin (591 msgs)   • Tsalwin (421 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 98), "• Asirk (258 msgs)   • Olboy (240 msgs)    • Tweedlede (192 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 130), "Guild Journey: Project Faceless -> Haven -> Dungeons and Dragons", fill=gold_soft, font=font_caption)

    draw.text((540, y_r4 + 44), "Top Raid Chat Companions:", fill=gold_soft, font=font_bold)
    draw.text((540, y_r4 + 72), "• Tsalwin (18,421 msgs) • Poep (11,290 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 98), "• Lyric (7,910 msgs)    • Soulys (6,412 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 130), "Guild: <Dungeons and Dragons> (Joined Dec 14, 2024)", fill=cyan_glow, font=font_bold)

    y_r5 = 1285
    h_r5 = 150
    draw_panel(40, y_r5, width - 40, y_r5 + h_r5, "🏆 MILESTONES & EXPANSION FIRSTS", gold)
    milestones = [
        ("Water Sprinkler of Nem Ankh", "Inventory Confirmed", "Project Quarm"),
        ("Ding 60", "Sep 29, 2024", "Recorded in Logs"),
        ("First Kunark Footstep", "Sun Oct 20, 2024", "Skyfire Mountains"),
        ("First Velious Footstep", "Tue Apr 01, 2025", "Iceclad Ocean"),
        ("First Luclin Footstep", "Mon Jul 28, 2025", "The Fungus Grove")
    ]

    my = y_r5 + 42
    for mtitle, mdate, mzone in milestones:
        color = gold_soft if "Epic" in mtitle or "Ding 60" in mtitle else white
        draw.text((58, my), f"★ {mtitle}", fill=color, font=font_bold)
        draw.text((430, my), mdate, fill=gray, font=font_caption)
        draw.text((width - 58, my), mzone, fill=cyan_glow, font=font_caption, anchor="ra")
        my += 20

    draw.text((width // 2, height - 28), "Project Quarm Chronicle • Client Logs from C:\\TAKPv22\\ • Powered by Quarm Chronicle Engine", fill=gray, font=font_caption, anchor="mm")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    img.save(output_image_path, "PNG")
    print(f"Thebrain card saved to {output_image_path}!")


def create_zondro_card(summary_json_path: str, output_image_path: str):
    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    width = 1000
    height = 1500
    
    img = Image.new("RGBA", (width, height), (15, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient - Shadow Green & Abyssal Dark
    for y in range(height):
        r = int(8 + (y / height) * 10)
        g = int(18 + (y / height) * 16)
        b = int(14 + (y / height) * 16)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    gold = (212, 175, 55, 255)
    gold_dark = (130, 100, 30, 255)
    gold_soft = (240, 215, 120, 255)
    cyan_glow = (56, 189, 248, 255)
    purple_glow = (192, 132, 252, 255)
    crimson = (248, 113, 113, 255)
    emerald = (74, 222, 128, 255)
    white = (248, 250, 252, 255)
    gray = (148, 163, 184, 255)
    card_bg = (18, 28, 24, 235)

    draw.rectangle([14, 14, width - 14, height - 14], outline=gold_dark, width=2)
    draw.rectangle([20, 20, width - 20, height - 20], outline=gold, width=3)
    draw.rectangle([26, 26, width - 26, height - 26], outline=gold_dark, width=1)

    def draw_corner(cx, cy):
        draw.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=gold, outline=gold_dark, width=1)
        draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(15, 18, 25, 255))

    draw_corner(20, 20)
    draw_corner(width - 20, 20)
    draw_corner(20, height - 20)
    draw_corner(width - 20, height - 20)

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

    draw.text((width // 2, 54), "PROJECT QUARM CHRONICLE", fill=gold_soft, font=font_tag, anchor="mm")
    draw.line([(220, 70), (width - 220, 70)], fill=gold_dark, width=2)

    draw.text((width // 2, 112), "ZONDRO", fill=white, font=font_name, anchor="mm")
    draw.text((width // 2, 155), "Level 60 Iksar Necromancer • <Dungeons and Dragons>", fill=emerald, font=font_sub, anchor="mm")
    draw.text((width // 2, 183), "Jun 02, 2024 — Sep 16, 2026 • Norrathian Career Chronicle", fill=gray, font=font_caption, anchor="mm")

    def draw_panel(x1, y1, x2, y2, title, accent=gold):
        draw.rectangle([x1, y1, x2, y2], fill=card_bg, outline=gold_dark, width=1)
        draw.line([x1, y1, x2, y1], fill=accent, width=3)
        draw.text((x1 + 18, y1 + 12), title, fill=accent, font=font_sec)

    y_m = 205
    h_m = 100
    w_m = 215
    spacing = 15
    x_start = 40

    b1_x = x_start
    draw_panel(b1_x, y_m, b1_x + w_m, y_m + h_m, "DEATH & DECAY", emerald)
    draw.text((b1_x + w_m//2, y_m + 52), "17,385 DoTs", fill=emerald, font=font_stat_big, anchor="mm")
    draw.text((b1_x + w_m//2, y_m + 80), "Splurt, Cor, Lifebane", fill=gray, font=font_small, anchor="mm")

    b2_x = b1_x + w_m + spacing
    draw_panel(b2_x, y_m, b2_x + w_m, y_m + h_m, "DEATH TRICKERY", purple_glow)
    draw.text((b2_x + w_m//2, y_m + 52), "1,356 FDs", fill=purple_glow, font=font_stat_big, anchor="mm")
    draw.text((b2_x + w_m//2, y_m + 80), "Feign Death Master", fill=gray, font=font_small, anchor="mm")

    b3_x = b2_x + w_m + spacing
    draw_panel(b3_x, y_m, b3_x + w_m, y_m + h_m, "PINNACLE CONQUEST", cyan_glow)
    draw.text((b3_x + w_m//2, y_m + 52), "6 Defeated", fill=white, font=font_stat_big, anchor="mm")
    draw.text((b3_x + w_m//2, y_m + 80), "9 Aten • 6 Vulak • 3 Phara", fill=gray, font=font_small, anchor="mm")

    b4_x = b3_x + w_m + spacing
    draw_panel(b4_x, y_m, b4_x + w_m, y_m + h_m, "SHADOW MINIONS", gold)
    draw.text((b4_x + w_m//2, y_m + 52), "610 Pets", fill=gold_soft, font=font_stat_big, anchor="mm")
    draw.text((b4_x + w_m//2, y_m + 80), "Emissary of Thule Summons", fill=gray, font=font_small, anchor="mm")

    y_r1 = 320
    h_r1 = 265
    w_half = 445

    draw_panel(40, y_r1, 40 + w_half, y_r1 + h_r1, "👑 PINNACLE RAID BOSSES (FIRST KILLS)", gold)
    pinnacle_rows = [
        ("Luclin", "Aten Ha Ra", "Feb 17, 2026", "9 Kills"),
        ("Velious", "Vulak`Aerr", "May 09, 2025", "6 Kills"),
        ("Kunark", "Phara Dar", "Dec 13, 2024", "3 Kills"),
        ("Classic", "Lord Nagafen", "Apr 08, 2025", "1 Kill"),
        ("Velious", "Tunare", "Jun 29, 2026", "1 Kill"),
        ("Classic", "Lady Vox", "Apr 22, 2026", "1 Kill")
    ]
    py = y_r1 + 44
    for era, bname, fdate, tkills in pinnacle_rows:
        draw.text((58, py), f"★ {bname}", fill=gold_soft, font=font_bold)
        draw.text((260, py), era, fill=gray, font=font_caption)
        draw.text((320, py), fdate, fill=white, font=font_caption)
        draw.text((40 + w_half - 18, py), tkills, fill=cyan_glow, font=font_bold, anchor="ra")
        py += 35

    draw_panel(width - 40 - w_half, y_r1, width - 40, y_r1 + h_r1, "⚔️ TOP RAID BOSS TOTAL KILLS", cyan_glow)
    other_raids = [
        ("King Tranix", "18 kills"),
        ("Kaas Thox Xi Aten Ha Ra", "17 kills"),
        ("Thall Va Xakra", "14 kills"),
        ("a glyph covered serpent", "13 kills"),
        ("Vyzh`dra the Exiled", "13 kills"),
        ("Vyzh`dra the Cursed", "13 kills")
    ]
    ry = y_r1 + 44
    for rname, rcount in other_raids:
        draw.text((width - 40 - w_half + 18, ry), rname, fill=white, font=font_body)
        draw.text((width - 58, ry), rcount, fill=cyan_glow, font=font_bold, anchor="ra")
        ry += 35

    y_r2 = 600
    h_r2 = 230
    draw_panel(40, y_r2, 40 + w_half, y_r2 + h_r2, "☠️ NECROTIC INCANTATIONS", purple_glow)
    spells = [
        ("Dooming Darkness", "11,246"),
        ("Splurt", "4,906"),
        ("Cessation of Cor", "4,834"),
        ("Vexing Mordinia", "4,402"),
        ("Ancient: Lifebane", "3,972")
    ]
    sy = y_r2 + 44
    for sname, scnt in spells:
        draw.text((58, sy), sname, fill=white, font=font_body)
        draw.text((40 + w_half - 18, sy), scnt, fill=purple_glow, font=font_bold, anchor="ra")
        sy += 35

    draw_panel(width - 40 - w_half, y_r2, width - 40, y_r2 + h_r2, "🌟 AA POINTS BY ZONE", gold)
    aa_zones = [
        ("The Maiden's Eye", "67 AAs"),
        ("Shar Vahl", "15 AAs"),
        ("Katta Castellum", "9 AAs"),
        ("The Grey", "5 AAs"),
        ("The Paludal Caverns", "4 AAs")
    ]
    ay = y_r2 + 44
    for zname, acnt in aa_zones:
        draw.text((width - 40 - w_half + 18, ay), zname, fill=white, font=font_body)
        draw.text((width - 58, ay), acnt, fill=gold_soft, font=font_bold, anchor="ra")
        ay += 35

    y_r3 = 845
    h_r3 = 235
    draw_panel(40, y_r3, 40 + w_half, y_r3 + h_r3, "☠️ MORTALITY & NEMESIS", crimson)
    nemesis_lines = [
        ("Kaas Thox Xi Aten Ha Ra", "6 deaths"),
        ("Aten Ha Ra", "4 deaths"),
        ("carrion beetle hatchling", "4 deaths"),
        ("Bleeding Out / Negative HP", "25 deaths"),
        ("Accepted Resurrections", "137 rezzes")
    ]
    ny = y_r3 + 44
    for nname, ncount in nemesis_lines:
        color = emerald if "Resurrections" in nname else (crimson if "6 deaths" in ncount else white)
        draw.text((58, ny), nname, fill=color, font=font_body)
        draw.text((40 + w_half - 18, ny), ncount, fill=color, font=font_bold, anchor="ra")
        ny += 35

    draw_panel(width - 40 - w_half, y_r3, width - 40, y_r3 + h_r3, "🗡️ SHADOW CRAFT & TWITCH", emerald)
    necro_craft = [
        ("Mana Conversion", "3,722 casts"),
        ("Feign Death", "1,356 casts"),
        ("Pet Summons", "610 casts"),
        ("Mana Twitch", "424 casts"),
        ("Lifetaps", "365 casts")
    ]
    sly = y_r3 + 44
    for mname, mcount in necro_craft:
        draw.text((width - 40 - w_half + 18, sly), mname, fill=white, font=font_body)
        draw.text((width - 58, sly), mcount, fill=emerald, font=font_bold, anchor="ra")
        sly += 35

    y_r4 = 1095
    h_r4 = 175
    draw_panel(40, y_r4, width - 40, y_r4 + h_r4, "💬 COMPANIONS IN ARMS & SOCIAL CIRCLE", cyan_glow)
    
    draw.text((58, y_r4 + 44), "Top Group Chat Companions:", fill=gold_soft, font=font_bold)
    draw.text((58, y_r4 + 72), "• Tsalwin (531 msgs)   • Buffin (425 msgs)   • Destu (263 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 98), "• Qados (215 msgs)     • Tailsweat (171 msgs)• Asirk (150 msgs)", fill=white, font=font_body)
    draw.text((58, y_r4 + 130), "Guild Journey: Project Faceless -> Haven -> Dungeons and Dragons", fill=gold_soft, font=font_caption)

    draw.text((540, y_r4 + 44), "Top Raid Chat Companions:", fill=gold_soft, font=font_bold)
    draw.text((540, y_r4 + 72), "• Tsalwin (4,912 msgs) • Poep (3,120 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 98), "• Lyric (2,450 msgs)   • Soulys (2,180 msgs)", fill=white, font=font_body)
    draw.text((540, y_r4 + 130), "Guild: <Dungeons and Dragons> (Joined Dec 14, 2024)", fill=emerald, font=font_bold)

    y_r5 = 1285
    h_r5 = 150
    draw_panel(40, y_r5, width - 40, y_r5 + h_r5, "🏆 MILESTONES & EXPANSION FIRSTS", gold)
    milestones = [
        ("Scythe of the Shadowed Soul", "Thu Feb 13, 2025", "Lake Rathetear"),
        ("Ding 60", "Jun 02, 2024", "Recorded in Logs"),
        ("First Kunark Footstep", "Sun Jun 02, 2024", "Field of Bone"),
        ("First Velious Footstep", "Sun Apr 06, 2025", "Iceclad Ocean"),
        ("First Luclin Footstep", "Wed Aug 06, 2025", "Nexus")
    ]

    my = y_r5 + 42
    for mtitle, mdate, mzone in milestones:
        color = gold_soft if "Epic" in mtitle or "Ding 60" in mtitle else white
        draw.text((58, my), f"★ {mtitle}", fill=color, font=font_bold)
        draw.text((430, my), mdate, fill=gray, font=font_caption)
        draw.text((width - 58, my), mzone, fill=cyan_glow, font=font_caption, anchor="ra")
        my += 20

    draw.text((width // 2, height - 28), "Project Quarm Chronicle • Client Logs from C:\\TAKPv22\\ • Powered by Quarm Chronicle Engine", fill=gray, font=font_caption, anchor="mm")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    img.save(output_image_path, "PNG")
    print(f"Zondro card saved to {output_image_path}!")


if __name__ == "__main__":
    import sys
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    
    if target in ("tweedlede", "all"):
        create_tweedlede_card(
            r"C:\code\quarm-chronicle\data\sample_output\tweedlede_summary.json",
            r"C:\code\quarm-chronicle\data\sample_output\tweedlede_chronicle_card.png"
        )
    if target in ("steps", "all"):
        create_steps_card(
            r"C:\code\quarm-chronicle\data\sample_output\steps_summary.json",
            r"C:\code\quarm-chronicle\data\sample_output\steps_chronicle_card.png"
        )
    if target in ("thebrain", "all"):
        create_thebrain_card(
            r"C:\code\quarm-chronicle\data\sample_output\thebrain_summary.json",
            r"C:\code\quarm-chronicle\data\sample_output\thebrain_chronicle_card.png"
        )
    if target in ("zondro", "all"):
        create_zondro_card(
            r"C:\code\quarm-chronicle\data\sample_output\zondro_summary.json",
            r"C:\code\quarm-chronicle\data\sample_output\zondro_chronicle_card.png"
        )
