"""PIL thumbnail adapter (no GPU). Text overlay on a base image or solid color."""

def probe():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def capabilities():
    return ["thumbnail.create", "thumbnail.text"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "Pillow not installed"}
    if action not in ("thumbnail.create", "thumbnail.text"):
        return {"status": "refused", "reason": f"unknown action {action}"}
    from PIL import Image, ImageDraw, ImageFont

    out = params.get("out", "thumb.png")
    w = params.get("w", 1280)
    h = params.get("h", 720)
    bg = params.get("bg", (20, 20, 40))
    text = params.get("text", "")
    base = params.get("base")
    if base:
        img = Image.open(base).resize((w, h))
    else:
        img = Image.new("RGB", (w, h), bg)
    if text:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", params.get("font_size", 48))
        except Exception:
            font = ImageFont.load_default()
        draw.text((40, h // 2), text, fill=(255, 255, 255), font=font)
    img.save(out)
    return {"status": "ok", "out": out, "size": [w, h]}