import math
import hashlib
from PIL import Image, ImageDraw, ImageFont


def compute_txid(tx_hex: str) -> str:
    tx_bytes = bytes.fromhex(tx_hex)
    hashed = hashlib.sha256(hashlib.sha256(tx_bytes).digest()).digest()
    return hashed[::-1].hex()


def get_fitting_font(text, target_width, initial_size=36, min_size=10):
    """Shrink font size until text fits in target width."""
    for size in range(initial_size, min_size - 1, -1):
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", size)
        except:
            font = ImageFont.load_default()
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        if width <= target_width:
            return font
    return ImageFont.load_default()


def hex_to_postable_image(tx_hex: str, txid: str = None, output_path="tx_postable.png",
                          target_width=1600, target_height=900, margin=50, font_size=36):
    tx_hex = tx_hex.strip().lower()
    if txid is None:
        txid = compute_txid(tx_hex)

    chunk_size = 12
    chunks = [tx_hex[i:i + chunk_size] for i in range(0, len(tx_hex), chunk_size)]
    if len(chunks[-1]) < chunk_size:
        chunks[-1] = chunks[-1].ljust(chunk_size, '0')

    total_chunks = len(chunks)
    grid_dim = math.ceil(math.sqrt(total_chunks))
    padded_total = grid_dim ** 2
    while len(chunks) < padded_total:
        chunks.append("000000000000")

    usable_width = target_width - 2 * margin
    usable_height = target_height - 2 * margin - font_size * 2

    square_size = min(usable_width // grid_dim, usable_height // grid_dim)
    grid_px = grid_dim * square_size
    img_width = grid_px + 2 * margin
    img_height = grid_px + 2 * margin + font_size * 2

    img = Image.new("RGB", (img_width, img_height), color="white")
    draw = ImageDraw.Draw(img)

    for i, chunk in enumerate(chunks):
        r = int(chunk[0:2], 16)
        g = int(chunk[2:4], 16)
        b = int(chunk[4:6], 16)
        x = (i % grid_dim) * square_size + margin
        y = (i // grid_dim) * square_size + margin
        draw.rectangle([x, y, x + square_size, y + square_size], fill=(r, g, b))

    # Fit the TXID label dynamically
    label_text = f"TXID: {txid}"
    fitting_font = get_fitting_font(label_text, img_width - 2 * margin, initial_size=font_size)
    label_y = grid_px + margin + (font_size // 2)
    draw.text((margin, label_y), label_text, fill="black", font=fitting_font)

    img.save(output_path)
    print(f"✅ Image saved: {output_path}")
    print(f"🔐 TXID: {txid}")
    print(f"🧮 Grid: {grid_dim} x {grid_dim}, Squares: {total_chunks}, Square Size: {square_size}px")


# === Litecoin GenBlock ===
if __name__ == "__main__":
    tx_hex = (
        "01000000010000000000000000000000000000000000000000000000000000000000000000"
        "ffffffff4804ffff001d0104404e592054696d65732030352f4f63742f3230313120537465"
        "76204a6f62732c204170706c65e280997320566973696f6e6172792c204469657320617420"
        "3536ffffffff0100f2052a010000004341040184710fa689ad5023690c80f3a49c8f13f8d4"
        "5b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b1"
        "79c45070ac7b03a9ac00000000"
    )

    hex_to_postable_image(tx_hex, txid=None, output_path="tx_genesis_fit_for_x.png")
