from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import os
import math

# === CONFIG ===
font_base = "PillowVersion"
spreadsheet_path = "Probe.csv"
font_dir = "fonts"
output_base = "Probe_images"
canvas_size = (500, 200)
font_size = 120

# === Define crowding levels (label, font suffix) ===
crowding_levels = [
    ("crwd1", 0),
    ("crwd2", 75),
    ("crwd3", 120),
    ("crwd4", "flipped"),  # Special case: flip the image using 0-crowding font
]

# === Load spreadsheet ===
df = pd.read_csv(spreadsheet_path)
df = df.fillna("")  # Replace NaNs with blank strings
df.columns = [f"con{i+1}" for i in range(len(df.columns))]

# === Track all words for clean duplicates
ghost_tracking = []  # List of (count, word, con_col, crowding_label, flip_flag)

# === Loop through connector columns
for con_col in df.columns:
    words = [w.strip() for w in df[con_col].sample(frac=1, random_state=42) if w.strip()]
    chunk_size = math.ceil(len(words) / len(crowding_levels))

    for i, (crowding_label, font_suffix) in enumerate(crowding_levels):
        chunk = words[i * chunk_size : (i + 1) * chunk_size]
        if not chunk:
            continue

        if font_suffix == "flipped":
            font_filename = f"{font_base}0.otf"  # Use clean font
            flip_image = True
        else:
            font_filename = f"{font_base}{font_suffix}.otf"
            flip_image = False

        font_path = os.path.join(font_dir, font_filename)
        output_dir = os.path.join(output_base, crowding_label)
        os.makedirs(output_dir, exist_ok=True)

        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            print(f"❌ Could not load font: {font_path}")
            continue

        for count, word in enumerate(chunk, 1):
            reshaped = arabic_reshaper.reshape(word)
            bidi_word = get_display(reshaped)

            dummy_img = Image.new("RGB", (1000, 1000), "white")
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.textbbox((0, 0), bidi_word, font=font)

            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            img = Image.new("RGB", canvas_size, "white")
            draw = ImageDraw.Draw(img)

            x = (canvas_size[0] - text_w) // 2 - bbox[0]
            y = (canvas_size[1] - text_h) // 2 - bbox[1]

            draw.text((x, y), bidi_word, font=font, fill="black")

            if flip_image:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)

            filename = f"Img_{count:03}_{con_col}_{crowding_label}.jpg"
            img.save(os.path.join(output_dir, filename))

            ghost_tracking.append((count, word, con_col, crowding_label, flip_image))

# === Generate clean (ghost duplicate) versions in matching folders
ghost_font_path = os.path.join(font_dir, f"{font_base}0.otf")

try:
    clean_font = ImageFont.truetype(ghost_font_path, font_size)
except OSError:
    print(f"❌ Could not load clean font: {ghost_font_path}")
else:
    for count, word, con_col, crowding_label, flip_image in ghost_tracking:
        reshaped = arabic_reshaper.reshape(word)
        bidi_word = get_display(reshaped)

        dummy_img = Image.new("RGB", (1000, 1000), "white")
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.textbbox((0, 0), bidi_word, font=clean_font)

        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        img = Image.new("RGB", canvas_size, "white")
        draw = ImageDraw.Draw(img)

        x = (canvas_size[0] - text_w) // 2 - bbox[0]
        y = (canvas_size[1] - text_h) // 2 - bbox[1]

        draw.text((x, y), bidi_word, font=clean_font, fill="black")

        # Keep clean versions unflipped regardless of condition
        clean_folder = f"clean_{crowding_label}"
        clean_output_dir = os.path.join(output_base, clean_folder)
        os.makedirs(clean_output_dir, exist_ok=True)

        filename = f"Img_{count:03}_{con_col}_crwd0.jpg"
        img.save(os.path.join(clean_output_dir, filename))

print("✅ All images generated! Ghost duplicates saved in separate folders.")
