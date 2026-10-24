"""Techu Machi carousel toolkit.

Helpers: background(), frame(img, idx, total) (adds logo watermark, page count, footer),
draw_line(), para() (wrapped text), card(), pill(), bolt(), save().
Canvas is 1080x1350 (Instagram 4:5). Colours: WHITE, CYAN, YEL, GREY, RED, GREEN.
The build_* functions are worked examples of past posts - copy their layout for new posts.
Usage: import techumachi as tm; then write a build function and call it.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))
GF = os.path.join(HERE, "fonts") + "/"
TF = os.path.join(HERE, "fonts") + "/"
LOGO = os.path.join(HERE, "..", "logo.png")
RAQM = ImageFont.Layout.RAQM
WHITE, CYAN, YEL, GREY = (255, 255, 255), (0, 229, 255), (255, 196, 0), (150, 160, 190)

_cache = {}
def font(kind, size, weight="bold"):
    key = (kind, size, weight)
    if key not in _cache:
        if kind == "ta":
            p = TF + ("noto-sans-tamil-tamil-700-normal.woff" if weight == "bold" else "noto-sans-tamil-tamil-500-normal.woff")
        else:
            p = GF + ("Poppins-Bold.ttf" if weight == "bold" else "Poppins-Medium.ttf")
        _cache[key] = ImageFont.truetype(p, size, layout_engine=RAQM)
    return _cache[key]

def is_ta(ch):
    return 0x0B80 <= ord(ch) <= 0x0BFF

def runs(text):
    out, cur, curk = [], "", None
    for ch in text:
        k = "ta" if is_ta(ch) else ("any" if ch == " " else "la")
        if k == "any":
            cur += ch; continue
        if curk is None or k == curk:
            cur += ch; curk = k
        else:
            out.append((curk, cur)); cur, curk = ch, k
    if cur:
        out.append((curk or "la", cur))
    return out

def width(d, text, size, weight="bold"):
    # Tamil glyphs look larger; scale Tamil down slightly to balance with Poppins
    return sum(d.textlength(t, font=font(k, int(size * (0.86 if k == "ta" else 1)), weight)) for k, t in runs(text))

def draw_line(d, text, x, y, size, fill, weight="bold", align="left"):
    """y is the baseline."""
    w = width(d, text, size, weight)
    if align == "center":
        x = (W - w) / 2
    for k, t in runs(text):
        f = font(k, int(size * (0.86 if k == "ta" else 1)), weight)
        d.text((x, y), t, font=f, fill=fill, anchor="ls")
        x += d.textlength(t, font=f)
    return w

def background():
    img = Image.new("RGB", (W, H))
    px = img.load()
    c1, c2 = (10, 10, 22), (26, 32, 66)
    for y in range(H):
        for x in range(0, W):
            t = (x * 0.4 + y) / (W * 0.4 + H)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return img.convert("RGBA")

def bolt(img, cx, cy, s, glow=True):
    pts = [(0, -1), (-0.55, 0.25), (-0.1, 0.25), (-0.35, 1), (0.45, -0.15), (0.0, -0.15), (0.25, -1)]
    pts = [(cx + px * s, cy + py * s) for px, py in pts]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(pts, fill=YEL + (255,))
    if glow:
        g = layer.filter(ImageFilter.GaussianBlur(s * 0.25))
        img.alpha_composite(g)
    img.alpha_composite(layer)

def frame(img, idx, total):
    d = ImageDraw.Draw(img)
    # logo watermark (top-left, round, with a thin cyan ring)
    sz = 130
    logo = Image.open(LOGO).convert("RGB").resize((sz, sz), Image.LANCZOS)
    mask = Image.new("L", (sz, sz), 0); ImageDraw.Draw(mask).ellipse([0, 0, sz - 1, sz - 1], fill=255)
    img.paste(logo, (70, 45), mask)
    d = ImageDraw.Draw(img)
    d.ellipse([68, 43, 72 + sz, 47 + sz], outline=CYAN, width=3)
    draw_line(d, f"{idx}/{total}", W - 80 - width(d, f"{idx}/{total}", 34, "med"), 122, 34, GREY, "med")
    # footer
    d.line([(80, H - 140), (W - 80, H - 140)], fill=(60, 70, 110), width=2)
    draw_line(d, "@techumachi", 80, H - 72, 36, CYAN, "med")
    if idx < total:
        t = "Swipe  >>"
        draw_line(d, t, W - 80 - width(d, t, 36, "med"), H - 72, 36, YEL, "med")
    return d

def save(img, path):
    img.convert("RGB").save(path, quality=95)

def build_intro(outdir):
    total = 3
    # Slide 1
    img = background(); d = frame(img, 1, total)
    bolt(img, W // 2, 330, 110); d = ImageDraw.Draw(img)
    draw_line(d, "Vanakkam Machi!", 0, 590, 64, YEL, align="center")
    draw_line(d, "இனி Tech news", 0, 740, 104, WHITE, align="center")
    draw_line(d, "தமிழில்!", 0, 880, 124, CYAN, align="center")
    draw_line(d, "உங்க daily tech நண்பன்", 0, 1020, 52, GREY, "med", align="center")
    save(img, os.path.join(outdir, "intro_1.jpg"))

    # Slide 2
    img = background(); d = frame(img, 2, total)
    draw_line(d, "இங்க என்ன", 80, 330, 96, WHITE)
    draw_line(d, "கிடைக்கும்?", 80, 460, 96, CYAN)
    items = [("New phones & prices", "launch, offers, comparison"),
             ("Free AI tools & tricks", "work-ஐ easy-ஆ முடிக்க"),
             ("Useful apps", "daily life-க்கு helpful"),
             ("Phone tips & settings", "speed, battery, safety")]
    y = 610
    for title, sub in items:
        d.rounded_rectangle([80, y - 62, W - 80, y + 66], radius=28, fill=(30, 38, 78), outline=(55, 70, 130), width=2)
        d.ellipse([112, y - 22, 140, y + 6], fill=YEL)
        draw_line(d, title, 170, y + 2, 46, WHITE)
        draw_line(d, sub, 170, y + 48, 32, GREY, "med")
        y += 150
    save(img, os.path.join(outdir, "intro_2.jpg"))

    # Slide 3
    img = background(); d = frame(img, 3, total)
    draw_line(d, "தினமும்", 0, 400, 90, WHITE, align="center")
    draw_line(d, "7 PM", 0, 580, 190, YEL, align="center")
    draw_line(d, "Tech update", 0, 700, 84, CYAN, align="center")
    d.rounded_rectangle([140, 820, W - 140, 960], radius=70, fill=CYAN)
    draw_line(d, "Follow பண்ணுங்க!", 0, 912, 60, (10, 12, 30), align="center")
    draw_line(d, "Miss பண்ணாதீங்க machi", 0, 1060, 50, GREY, "med", align="center")
    save(img, os.path.join(outdir, "intro_3.jpg"))



def card(d, x0, y0, x1, y1):
    d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=(30, 38, 78), outline=(55, 70, 130), width=2)

def build_iphone_duo(outdir):
    total = 3
    # Slide 1 - hook
    img = background(); d = frame(img, 1, total)
    d.rounded_rectangle([80, 260, 400, 340], radius=40, fill=(230, 40, 70))
    draw_line(d, "BREAKING", 112, 318, 44, WHITE)
    draw_line(d, "iPhone Duo", 80, 520, 140, WHITE)
    draw_line(d, "இன்று முதல்", 80, 680, 100, CYAN)
    draw_line(d, "India-ல sale!", 80, 820, 100, CYAN)
    draw_line(d, "Apple-ன் first foldable phone", 80, 960, 50, YEL, "med")
    draw_line(d, "Price தெரிஞ்சா shock ஆவீங்க", 80, 1050, 46, GREY, "med")
    save(img, os.path.join(outdir, "iphoneduo_1.jpg"))

    # Slide 2 - prices
    img = background(); d = frame(img, 2, total)
    draw_line(d, "India Price", 80, 340, 104, WHITE)
    draw_line(d, "எவ்வளவு?", 80, 470, 104, CYAN)
    rows = [("256GB", "₹2,99,900"), ("512GB", "₹3,24,900"), ("1TB", "₹3,74,900")]
    y = 570
    for v, p in rows:
        card(d, 80, y, W - 80, y + 140)
        draw_line(d, v, 130, y + 92, 54, GREY, "med")
        draw_line(d, p, W - 130 - width(d, p, 70), y + 98, 70, YEL)
        y += 170
    draw_line(d, "Pre-order: Oct 16  •  Sale: Oct 23", 0, 1130, 40, GREY, "med", align="center")
    save(img, os.path.join(outdir, "iphoneduo_2.jpg"))

    # Slide 3 - key facts
    img = background(); d = frame(img, 3, total)
    draw_line(d, "தெரிஞ்சுக்கோங்க", 80, 330, 92, CYAN)
    facts = [("6 Apple stores-ல மட்டும்", "Delhi, Noida, Bengaluru, Mumbai, Pune"),
             ("Online: max 2 units", "ஒரு customer-க்கு 2 தான்"),
             ("First week ~6,000 units", "report படி (Apple confirm பண்ணல)"),
             ("Grey market-ல +₹50K!", "அதிக விலைக்கு வாங்காதீங்க")]
    y = 430
    for t, s in facts:
        card(d, 80, y, W - 80, y + 140)
        d.ellipse([112, y + 44, 140, y + 72], fill=YEL)
        draw_line(d, t, 170, y + 70, 46, WHITE)
        draw_line(d, s, 170, y + 118, 32, GREY, "med")
        y += 160
    draw_line(d, "நீங்க வாங்குவீங்களா?", 0, 1110, 46, YEL, align="center")
    save(img, os.path.join(outdir, "iphoneduo_3.jpg"))



RED, GREEN = (235, 60, 80), (40, 200, 120)

def wrap(d, text, size, maxw, weight="bold"):
    words, lines, cur = text.split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if width(d, t, size, weight) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def para(d, text, x, y, size, fill, maxw, weight="bold", lh=1.3, align="left"):
    for ln in wrap(d, text, size, maxw, weight):
        draw_line(d, ln, x, y, size, fill, weight, align)
        y += int(size * lh)
    return y

def pill(d, x, y, label, color):
    w = width(d, label, 40) + 60
    d.rounded_rectangle([x, y, x + w, y + 70], radius=35, fill=color)
    draw_line(d, label, x + 30, y + 50, 40, WHITE)

def build_myths(outdir):
    myths = [
        ("Overnight charging battery-ஐ கெடுக்கும்", "புது phones-ல optimized charging இருக்கு. Battery full ஆனதும் தானா control பண்ணிக்கும்."),
        ("Background apps close பண்ணா battery save ஆகும்", "திரும்ப open பண்ணும்போது இன்னும் அதிக battery போகும். Android, iOS தானே manage பண்ணும்."),
        ("அதிக megapixel = நல்ல photo", "Sensor size, lens, software processing தான் photo quality-ஐ decide பண்ணும்."),
        ("Incognito mode-ல யாருக்கும் தெரியாது", "உங்க phone-ல history save ஆகாது. ஆனா websites, internet provider, office network பார்க்க முடியும்."),
    ]
    total = 1 + len(myths)
    img = background(); d = frame(img, 1, total)
    draw_line(d, "Phone", 0, 470, 150, WHITE, align="center")
    draw_line(d, "MYTHS vs FACTS", 0, 620, 104, YEL, align="center")
    draw_line(d, "இன்னும் இதை", 0, 790, 80, CYAN, align="center")
    draw_line(d, "நம்பறீங்களா?", 0, 900, 80, CYAN, align="center")
    draw_line(d, "4 common myths, உண்மை என்ன?", 0, 1040, 44, GREY, "med", align="center")
    save(img, os.path.join(outdir, "myths_1.jpg"))
    for n, (m, f) in enumerate(myths, start=2):
        img = background(); d = frame(img, n, total)
        draw_line(d, f"#{n-1}", 80, 330, 90, (60, 75, 130))
        pill(d, 80, 380, "MYTH", RED)
        y = para(d, m, 80, 545, 66, WHITE, W - 160)
        d.line([(80, y + 10), (W - 80, y + 10)], fill=(60, 70, 110), width=2)
        pill(d, 80, y + 60, "FACT", GREEN)
        para(d, f, 80, y + 210, 48, CYAN, W - 160, "med", lh=1.4)
        save(img, os.path.join(outdir, f"myths_{n}.jpg"))

def build_oppo(outdir):
    total = 3
    img = background(); d = frame(img, 1, total)
    d.rounded_rectangle([80, 260, 470, 340], radius=40, fill=(40, 200, 120))
    draw_line(d, "INDIA LAUNCH", 112, 318, 44, WHITE)
    draw_line(d, "OPPO", 80, 500, 110, WHITE)
    draw_line(d, "Find X10 Series", 80, 640, 104, CYAN)
    draw_line(d, "3 x 200MP camera!", 80, 800, 76, YEL)
    draw_line(d, "8,000mAh battery", 80, 900, 60, WHITE, "med")
    draw_line(d, "Price எவ்வளவு? Swipe பண்ணுங்க", 80, 1040, 46, GREY, "med")
    save(img, os.path.join(outdir, "oppo_1.jpg"))

    img = background(); d = frame(img, 2, total)
    draw_line(d, "India Price", 80, 340, 104, WHITE)
    rows = [("Find X10", "12+256GB", "₹1,39,999"), ("Find X10", "12+512GB", "₹1,69,999"), ("X10 Pro Max", "12+512GB", "₹1,99,999")]
    y = 430
    for name, v, pr in rows:
        card(d, 80, y, W - 80, y + 170)
        draw_line(d, name, 130, y + 75, 50, WHITE)
        draw_line(d, v, 130, y + 130, 36, GREY, "med")
        draw_line(d, pr, W - 130 - width(d, pr, 64), y + 110, 64, YEL)
        y += 200
    draw_line(d, "Sale: Oct 29 முதல்", 0, 1080, 56, CYAN, align="center")
    draw_line(d, "OPPO store • Flipkart • Amazon", 0, 1150, 40, GREY, "med", align="center")
    save(img, os.path.join(outdir, "oppo_2.jpg"))

    img = background(); d = frame(img, 3, total)
    draw_line(d, "Highlights", 80, 330, 100, CYAN)
    facts = [("Pro Max: 3 x 200MP cameras", "Main, ultrawide, 3x periscope"),
             ("8,000mAh battery", "80W wired, 50W wireless charging"),
             ("Dimensity 9600 chips", "Pro Max-ல 2nm 9600 Pro"),
             ("LTPO AMOLED, 120Hz", "X10: 6.59-inch • Pro Max: 6.78-inch")]
    y = 430
    for t, s_ in facts:
        card(d, 80, y, W - 80, y + 140)
        d.ellipse([112, y + 44, 140, y + 72], fill=YEL)
        draw_line(d, t, 170, y + 70, 46, WHITE)
        draw_line(d, s_, 170, y + 118, 32, GREY, "med")
        y += 160
    draw_line(d, "iPhone Duo vs OPPO: எது best?", 0, 1110, 46, YEL, align="center")
    save(img, os.path.join(outdir, "oppo_3.jpg"))


def build_battery(outdir):
    tips = [
        ("Turn on Dark Mode", "On OLED/AMOLED screens, black pixels are switched off, so dark mode uses less power."),
        ("Screen timeout: 30 seconds", "Your screen is the biggest battery drain. Let it switch off quickly when you're not using it."),
        ("Use Adaptive Brightness", "Your phone adjusts brightness to your surroundings instead of staying at full blast."),
        ("Location: 'While using' only", "Stop apps from tracking your location in the background. Check Settings > Location."),
        ("Switch on Battery Saver early", "Set it to turn on automatically at 20-30% so you never run out before night."),
    ]
    total = 1 + len(tips)
    img = background(); d = frame(img, 1, total)
    draw_line(d, "5 Settings", 0, 480, 140, WHITE, align="center")
    draw_line(d, "to save your", 0, 610, 84, CYAN, align="center")
    draw_line(d, "BATTERY", 0, 760, 150, YEL, align="center")
    draw_line(d, "Change them in 2 minutes", 0, 900, 52, GREY, "med", align="center")
    draw_line(d, "Save this post for later", 0, 1040, 44, CYAN, "med", align="center")
    save(img, os.path.join(outdir, "battery_1.jpg"))
    for n, (t, desc) in enumerate(tips, start=2):
        img = background(); d = frame(img, n, total)
        draw_line(d, f"0{n-1}", 80, 420, 200, (60, 75, 130))
        y = para(d, t, 80, 600, 80, YEL, W - 160)
        para(d, desc, 80, y + 60, 54, WHITE, W - 160, "med", lh=1.4)
        save(img, os.path.join(outdir, f"battery_{n}.jpg"))

def build_vs(outdir):
    total = 3
    img = background(); d = frame(img, 1, total)
    draw_line(d, "iPhone Duo", 0, 470, 116, WHITE, align="center")
    d.ellipse([W//2 - 80, 540, W//2 + 80, 700], fill=YEL)
    draw_line(d, "VS", 0, 650, 80, (10, 12, 30), align="center")
    draw_line(d, "OPPO Find X10", 0, 850, 104, CYAN, align="center")
    draw_line(d, "Pro Max", 0, 960, 104, CYAN, align="center")
    draw_line(d, "This week's 2 big launches", 0, 1080, 46, GREY, "med", align="center")
    save(img, os.path.join(outdir, "vs_1.jpg"))

    img = background(); d = frame(img, 2, total)
    draw_line(d, "Head to Head", 80, 330, 96, WHITE)
    cw = (W - 160 - 30) // 2
    xs = [80, 80 + cw + 30]
    heads = [("iPhone Duo", WHITE), ("Find X10 Pro Max", CYAN)]
    rows = [("Starts at", "₹2,99,900", "₹1,99,999"),
            ("Type", "Foldable", "Camera flagship"),
            ("Storage", "256GB-1TB", "512GB"),
            ("On sale", "Oct 23", "Oct 29")]
    for k, (h, col) in enumerate(heads):
        d.rounded_rectangle([xs[k], 400, xs[k] + cw, 480], radius=24, fill=(40, 50, 100))
        draw_line(d, h, xs[k] + (cw - width(d, h, 38)) / 2, 455, 38, col)
    y = 510
    for label, a, b in rows:
        draw_line(d, label, 80, y + 40, 32, GREY, "med")
        for k, v in enumerate((a, b)):
            card(d, xs[k], y + 60, xs[k] + cw, y + 150)
            draw_line(d, v, xs[k] + (cw - width(d, v, 44)) / 2, y + 122, 44, YEL if label == "Starts at" else WHITE)
        y += 165
    save(img, os.path.join(outdir, "vs_2.jpg"))

    img = background(); d = frame(img, 3, total)
    draw_line(d, "The Verdict", 80, 330, 100, CYAN)
    pts = [("Want a foldable?", "iPhone Duo is Apple's first ever foldable phone."),
           ("Want the best camera?", "Find X10 Pro Max has three 200MP cameras."),
           ("Want battery life?", "OPPO packs an 8,000mAh battery."),
           ("Budget matters?", "OPPO is about ₹1 lakh cheaper.")]
    y = 430
    for t, s_ in pts:
        card(d, 80, y, W - 80, y + 140)
        d.ellipse([112, y + 44, 140, y + 72], fill=YEL)
        draw_line(d, t, 170, y + 70, 44, WHITE)
        draw_line(d, s_, 170, y + 118, 32, GREY, "med")
        y += 160
    draw_line(d, "Which one would you buy?", 0, 1110, 50, YEL, align="center")
    save(img, os.path.join(outdir, "vs_3.jpg"))

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    build_battery(out)
    build_vs(out)
