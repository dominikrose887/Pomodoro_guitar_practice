"""
Ikon generáló script a Pomodoro Guitar Practice alkalmazáshoz.

Egyedi gitár pick (pengető) + metronóm stílusú ikont generál .ico formátumban.
Szükséges: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def create_icon(output_path: str = "app_icon.ico") -> None:
    """Generál egy egyedi ikont több méretben."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = _draw_icon(size)
        images.append(img)

    # Az első képet mentjük, a többit append-eljük
    images[-1].save(
        output_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[:-1],
    )
    print(f"✅ Ikon létrehozva: {os.path.abspath(output_path)}")


def _draw_icon(size: int) -> Image.Image:
    """Egyetlen méretre rajzol egy gitár pick ikont zöld-arany témával."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2
    scale = size / 256  # alap méret: 256px

    # ── Háttér kör (zsálya-zöld) ───────────────────────────────────────
    pad = int(8 * scale)
    draw.ellipse(
        [pad, pad, size - pad, size - pad],
        fill=(162, 175, 155),  # #A2AF9B
    )

    # ── Gitár pick (pengető) forma ─────────────────────────────────────
    # Egy lekerekített háromszög-szerű forma
    pick_color = (250, 249, 238)  # #FAF9EE (világos krém)
    pick_outline = (200, 188, 168)  # finom szegély

    # Pick méret és pozíció
    pw = int(100 * scale)
    ph = int(130 * scale)
    px = cx - pw / 2
    py = cy - ph / 2 + int(5 * scale)

    # Pick pontok (lekerekített háromszög)
    _draw_pick(draw, cx, cy + int(5 * scale), pw, ph, pick_color, pick_outline, scale)

    # ── Hangjegy szimbólum a pick közepén ──────────────────────────────
    note_color = (106, 138, 96)  # #6a8a60 (sötét zöld)
    _draw_note(draw, cx, cy + int(5 * scale), scale, note_color)

    return img


def _draw_pick(draw: ImageDraw.Draw, cx: float, cy: float,
               w: float, h: float, fill: tuple, outline: tuple,
               scale: float) -> None:
    """Gitár pick alakzatot rajzol (lekerekített háromszög)."""
    # Felső lekerekített rész (széles) + alsó csúcs
    top_y = cy - h * 0.4
    mid_y = cy + h * 0.05
    bot_y = cy + h * 0.45
    left_x = cx - w * 0.5
    right_x = cx + w * 0.5

    # Közelítő pick forma polygon pontokkal
    points = []
    steps = 20

    # Felső ív (balról jobbra)
    for i in range(steps + 1):
        t = i / steps
        angle = math.pi + t * math.pi  # 180° → 360° (felső félkör)
        rx = w * 0.5
        ry = h * 0.25
        x = cx + rx * math.cos(angle)
        y = (top_y + ry) + ry * math.sin(angle)
        points.append((x, y))

    # Jobb oldal lefelé a csúcsig
    for i in range(1, steps + 1):
        t = i / steps
        x = right_x - (right_x - cx) * t
        y = mid_y + (bot_y - mid_y) * t
        points.append((x, y))

    # Bal oldal felfelé a csúcstól
    for i in range(1, steps):
        t = i / steps
        x = cx + (left_x - cx) * (1 - t)
        y = bot_y - (bot_y - mid_y) * t
        points.append((x, y))

    draw.polygon(points, fill=fill, outline=outline)

    # Belső border a szebb kinézet érdekében
    border_w = max(1, int(2 * scale))
    for offset in range(border_w):
        inner_points = []
        for px, py in points:
            dx = px - cx
            dy = py - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                factor = (dist - offset - 1) / dist
                inner_points.append((cx + dx * factor, cy + dy * factor))
            else:
                inner_points.append((px, py))


def _draw_note(draw: ImageDraw.Draw, cx: float, cy: float,
               scale: float, color: tuple) -> None:
    """Egyszerű hangjegy szimbólumot rajzol (♪)."""
    # Hangjegy fej (ovális)
    head_rx = int(14 * scale)
    head_ry = int(10 * scale)
    head_cx = cx - int(4 * scale)
    head_cy = cy + int(16 * scale)

    draw.ellipse(
        [head_cx - head_rx, head_cy - head_ry,
         head_cx + head_rx, head_cy + head_ry],
        fill=color,
    )

    # Hangjegy szár (függőleges vonal)
    stem_x = head_cx + head_rx - int(2 * scale)
    stem_top = cy - int(28 * scale)
    stem_bot = head_cy
    stem_w = max(2, int(4 * scale))

    draw.rectangle(
        [stem_x - stem_w // 2, stem_top, stem_x + stem_w // 2, stem_bot],
        fill=color,
    )

    # Hangjegy zászló (kis ív a szár tetején)
    flag_points = []
    for i in range(15):
        t = i / 14
        x = stem_x + int(18 * scale * t)
        y = stem_top + int(30 * scale * t * t)
        flag_points.append((x, y))

    if len(flag_points) >= 2:
        draw.line(flag_points, fill=color, width=max(2, int(3 * scale)))


if __name__ == "__main__":
    create_icon()
