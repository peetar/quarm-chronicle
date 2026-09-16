import os
import json
from PIL import Image, ImageDraw, ImageFont

def create_tweedlede_card(summary_json_path: str, output_image_path: str):
    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Card dimensions: 900 x 1200 (Discord card aspect ratio)
    width = 900
    height = 1200
    
    img = Image.new("RGBA", (width, height), (15, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient / vignette
    for y in range(height):
        # subtle vertical gradient
        r = int(14 + (y / height) * 12)
        g = int(18 + (y / height) * 10)
        b = int(28 + (y / height) * 12)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Outer and Inner Gold Borders
    gold = (212, 175, 55, 255)
    gold_dark = (130, 100, 30, 255)
    gold_soft = (230, 205, 115, 255)
    cyan_glow = (64, 224, 208, 255)
    purple_glow = (186, 104, 200, 255)
    crimson = (220, 70, 70, 255)
    white = (245, 245, 245, 255)
    gray = (160, 170, 185, 255)
    card_bg = (24, 29, 42, 230)

    # Borders
    draw.rectangle([15, 15, width - 15, height - 15], outline=gold_dark, width=2)
    draw.rectangle([22, 22, width - 22, height - 22], outline=gold, width=3)
    draw.rectangle([28, 28, width - 28, height - 28], outline=gold_dark, width=1)

    # Corner decorations
    def draw_corner(cx, cy):
        draw.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=gold, outline=gold_dark, width=1)
        draw.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(15, 18, 25, 255))

    draw_corner(22, 22)
    draw_corner(width - 22, 22)
    draw_corner(22, height - 22)
    draw_corner(width - 22, height - 22)

    # Try loading default fonts or TTF fonts
    try:
        font_header = ImageFont.truetype("arial.ttf", 20)
        font_name = ImageFont.truetype("georgia.ttf", 54)
        font_subtitle = ImageFont.truetype("georgia.ttf", 22)
        font_section = ImageFont.truetype("georgia.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 20)
        font_bold = ImageFont.truetype("arialbd.ttf", 22)
        font_stat_big = ImageFont.truetype("georgia.ttf", 40)
        font_caption = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font_header = font_name = font_subtitle = font_section = font_body = font_bold = font_stat_big = font_caption = ImageFont.load_default()

    # Header Ribbon
    draw.text((width // 2, 55), "PROJECT QUARM CHRONICLE", fill=gold_soft, font=font_header, anchor="mm")
    draw.line([(180, 75), (width - 180, 75)], fill=gold_dark, width=2)

    # Character Name & Title
    char_name = data.get("character", "Tweedlede").upper()
    draw.text((width // 2, 115), char_name, fill=white, font=font_name, anchor="mm")
    draw.text((width // 2, 160), "Grand Illusionist • Level 60 Enchanter", fill=cyan_glow, font=font_subtitle, anchor="mm")
    
    dates = f"{data['date_range']['first'][:15]} — {data['date_range']['last'][:15]}"
    draw.text((width // 2, 190), dates, fill=gray, font=font_caption, anchor="mm")

    # Helper function to draw a styled box
    def draw_card_box(x1, y1, x2, y2, title, accent_color=gold):
        draw.rectangle([x1, y1, x2, y2], fill=card_bg, outline=gold_dark, width=1)
        draw.line([x1, y1, x2, y1], fill=accent_color, width=3)
        draw.text((x1 + 18, y1 + 16), title, fill=accent_color, font=font_section)

    # Row 1: Key Summary Stats (3 Boxes)
    box_w = 260
    y_r1 = 220
    h_r1 = 125

    # 1. Total Zone-ins
    draw_card_box(45, y_r1, 45 + box_w, y_r1 + h_r1, "ZONE TRANSITIONS", cyan_glow)
    draw.text((45 + box_w//2, y_r1 + 65), "2,517", fill=white, font=font_stat_big, anchor="mm")
    draw.text((45 + box_w//2, y_r1 + 102), "in Chardok Alone", fill=gray, font=font_caption, anchor="mm")

    # 2. Spells Twisted / Cast
    draw_card_box(320, y_r1, 320 + box_w, y_r1 + h_r1, "SPELLS WEAVED", purple_glow)
    draw.text((320 + box_w//2, y_r1 + 65), "36,235+", fill=white, font=font_stat_big, anchor="mm")
    draw.text((320 + box_w//2, y_r1 + 102), "Total Incantations", fill=gray, font=font_caption, anchor="mm")

    # 3. Deaths
    draw_card_box(595, y_r1, 595 + box_w, y_r1 + h_r1, "TOTAL DEATHS", crimson)
    draw.text((595 + box_w//2, y_r1 + 65), "573", fill=crimson, font=font_stat_big, anchor="mm")
    draw.text((595 + box_w//2, y_r1 + 102), "229 in Arena PvP", fill=gray, font=font_caption, anchor="mm")

    # Row 2: Signature Spells & Chardok Pulling
    y_r2 = 365
    h_r2 = 235
    draw_card_box(45, y_r2, 45 + 395, y_r2 + h_r2, "🔮 SIGNATURE SPELLS", purple_glow)
    spells = [
        ("Shallow Breath (Fast Pulls)", "11,239"),
        ("Pacify (Calm Harmony)", "7,540"),
        ("Mesmerize (Crowd Control)", "6,124"),
        ("Boltran's Agacerie (Charm)", "5,537"),
        ("Minor Shielding (Buff/Cycle)", "5,795")
    ]
    sy = y_r2 + 55
    for sname, scnt in spells:
        draw.text((65, sy), sname, fill=white, font=font_body)
        draw.text((420, sy), scnt, fill=gold_soft, font=font_bold, anchor="ra")
        sy += 33

    # Row 2 Right: Zone Metrics & AA Harvest
    draw_card_box(460, y_r2, width - 45, y_r2 + h_r2, "🌟 AA HARVEST & GRIND", gold)
    aas = [
        ("The Fungus Grove", "5 AAs"),
        ("Veksar (Deep Ruins)", "3 AAs"),
        ("Ssraeshza Temple", "1 AA"),
        ("Siren's Grotto", "1 AA"),
        ("Total Alternate Advancements", "10 AAs")
    ]
    ay = y_r2 + 55
    for zname, acnt in aas:
        color = gold_soft if "Total" in zname else white
        draw.text((480, ay), zname, fill=color, font=font_bold if "Total" in zname else font_body)
        draw.text((width - 65, ay), acnt, fill=cyan_glow if "Total" in zname else gold_soft, font=font_bold, anchor="ra")
        ay += 33

    # Row 3: Danger & Deaths by Zone
    y_r3 = 620
    h_r3 = 240
    draw_card_box(45, y_r3, 45 + 395, y_r3 + h_r3, "☠️ DEADLIEST LOCALES", crimson)
    deaths_zones = [
        ("an Arena (PvP Duels)", "229 deaths"),
        ("Chardok (AE Pulling)", "113 deaths"),
        ("Temple of Veeshan", "23 deaths"),
        ("Plane of Fear (Instanced)", "22 deaths"),
        ("Siren's Grotto", "19 deaths")
    ]
    dy = y_r3 + 55
    for zname, dcnt in deaths_zones:
        draw.text((65, dy), zname, fill=white, font=font_body)
        draw.text((420, dy), dcnt, fill=crimson, font=font_bold, anchor="ra")
        dy += 33

    # Row 3 Right: Social Highlights & Partner in Crime
    draw_card_box(460, y_r3, width - 45, y_r3 + h_r3, "💬 SOCIAL & INNER CIRCLE", cyan_glow)
    social = [
        ("Tweedledum (Partner in Crime)", "480 tells"),
        ("Olboy", "87 tells"),
        ("Pinkiy", "83 tells"),
        ("Soulys", "78 tells"),
        ("Tigir", "61 tells")
    ]
    sy = y_r3 + 55
    for pname, tcnt in social:
        draw.text((480, sy), pname, fill=white, font=font_body)
        draw.text((width - 65, sy), tcnt, fill=cyan_glow, font=font_bold, anchor="ra")
        sy += 33

    # Row 4: Pinnacle Raid Bosses Witnessed / Defeated
    y_r4 = 880
    h_r4 = 220
    draw_card_box(45, y_r4, width - 45, y_r4 + h_r4, "⚔️ RAID BOSS TROPHY CASE", gold)
    raids = [
        ("Trakanon", "Ruins of Sebilis", "Sep 13, 2024", "Slayed by Morde"),
        ("Venril Sathir", "Karnor's Castle", "Oct 16, 2024", "Slayed by Ranza"),
        ("Faydedar", "Timorous Deep", "Oct 16, 2024", "Slayed by Lasartik"),
        ("Faydedar", "Timorous Deep", "Nov 06, 2024", "Slayed by Hillaryclinton"),
        ("Venril Sathir", "Karnor's Castle", "Nov 08, 2024", "Slayed by Dismas")
    ]
    ry = y_r4 + 55
    for boss, zone, dt, killer in raids:
        draw.text((65, ry), f"★ {boss}", fill=gold_soft, font=font_bold)
        draw.text((260, ry), zone, fill=gray, font=font_body)
        draw.text((540, ry), dt, fill=white, font=font_body)
        draw.text((width - 65, ry), killer, fill=cyan_glow, font=font_caption, anchor="ra")
        ry += 30

    # Footer
    draw.text((width // 2, 1145), "Generated by Quarm Chronicle • EverQuest: Project Quarm", fill=gray, font=font_caption, anchor="mm")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    img.save(output_image_path, "PNG")
    print(f"Card saved to {output_image_path}!")

if __name__ == "__main__":
    create_tweedlede_card(
        r"C:\code\quarm-chronicle\data\sample_output\tweedlede_summary.json",
        r"C:\code\quarm-chronicle\data\sample_output\tweedlede_chronicle_card.png"
    )
