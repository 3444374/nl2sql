from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("docs/opening/assets/png")
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1800, 980
INK = "#17324D"
MUTED = "#5B6875"
BLUE = "#2E5E8C"
BLUE_FILL = "#F3F8FC"
GREEN = "#5C8A4B"
GREEN_FILL = "#F5FAF2"
RED = "#B23A3A"
RED_FILL = "#FFF7F7"
LINE = "#748394"
BG = "white"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for candidate in [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf" if bold else "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


F_TITLE = font(50, True)
F_LABEL = font(38, True)
F_SMALL = font(29)
F_SUB = font(24)
F_NOTE = font(33, True)


def center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill: str = INK) -> None:
    x, y = xy
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2), text, font=fnt, fill=fill)


def card(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], title: str, sub: str, *, fill: str, outline: str) -> None:
    draw.rounded_rectangle(xy, radius=28, fill=fill, outline=outline, width=4)
    x1, y1, x2, _ = xy
    center(draw, ((x1 + x2) // 2, y1 + 46), title, F_LABEL, INK)
    lines = sub.split("\\n")
    if len(lines) == 1:
        center(draw, ((x1 + x2) // 2, y1 + 99), lines[0], F_SUB, MUTED)
    else:
        center(draw, ((x1 + x2) // 2, y1 + 88), lines[0], F_SUB, MUTED)
        center(draw, ((x1 + x2) // 2, y1 + 126), lines[1], F_SUB, MUTED)

def bezier(p0: tuple[int, int], p1: tuple[int, int], p2: tuple[int, int], p3: tuple[int, int], steps: int = 50) -> list[tuple[int, int]]:
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        pts.append((int(x), int(y)))
    return pts


def arrow_head(draw: ImageDraw.ImageDraw, prev: tuple[int, int], end: tuple[int, int], color: str) -> None:
    dx, dy = end[0] - prev[0], end[1] - prev[1]
    angle = math.atan2(dy, dx)
    size = 24
    left = (end[0] - size * math.cos(angle - 0.45), end[1] - size * math.sin(angle - 0.45))
    right = (end[0] - size * math.cos(angle + 0.45), end[1] - size * math.sin(angle + 0.45))
    draw.polygon([end, left, right], fill=color)


def curve_arrow(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], *, color: str = LINE, width: int = 7) -> None:
    draw.line(pts, fill=color, width=width, joint="curve")
    arrow_head(draw, pts[-2], pts[-1], color)


def straight_arrow(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], *, color: str = LINE, width: int = 7) -> None:
    curve_arrow(draw, [a, b], color=color, width=width)


def canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    center(draw, (W // 2, 80), title, F_TITLE)
    return img, draw


def save(img: Image.Image, name: str) -> None:
    img.save(OUT_DIR / name, quality=95, optimize=True)


def system_architecture() -> None:
    img, d = canvas("SQL+ 多智能体生成与反馈修正框架")
    y = 190
    xs = [105, 475, 845, 1215]
    labels = [("用户问题", "自然语言输入"), ("SQL+ 生成", "意图 + schema"), ("转换执行", "SQL+ → SQL"), ("结果/错误", "数据库反馈")]
    for i, (x, (t, s)) in enumerate(zip(xs, labels)):
        fill, outline = (GREEN_FILL, GREEN) if i >= 2 else (BLUE_FILL, BLUE)
        card(d, (x, y, x + 265, y + 135), t, s, fill=fill, outline=outline)
        if i < 3:
            straight_arrow(d, (x + 265, y + 67), (xs[i + 1] - 15, y + 67))
    ry = 550
    repair = [(260, "Critic Agent", "定位错误步骤"), (680, "Skill Router", "选择修复技能"), (1100, "Repair Skill", "局部修改 SQL+")]
    for x, t, s in repair:
        card(d, (x, ry, x + 300, ry + 135), t, s, fill=RED_FILL, outline=RED)
    straight_arrow(d, (560, ry + 67), (680, ry + 67), color=RED)
    straight_arrow(d, (980, ry + 67), (1100, ry + 67), color=RED)
    curve_arrow(d, bezier((1350, 325), (1370, 445), (520, 405), (410, 550)), color=RED)
    curve_arrow(d, bezier((1250, 550), (1220, 455), (1000, 430), (980, 325)), color=RED)
    d.rounded_rectangle((360, 805, 1440, 875), radius=20, fill=RED_FILL, outline=RED, width=3)
    center(d, (900, 840), "核心：错误反馈进入 SQL+ 局部步骤，避免整条 SQL 反复重写", F_NOTE, RED)
    save(img, "docx_system_architecture.png")


def technical_route() -> None:
    img, d = canvas("\u8bfe\u9898\u6280\u672f\u8def\u7ebf")
    y = 195
    items = [("SQL+ \u5b9a\u4e49", "\u8bed\u6cd5\u4e0e\u8f6c\u6362"), ("\u751f\u6210\u65b9\u6cd5", "NL \u2192 SQL+"), ("\u53cd\u9988\u8bca\u65ad", "\u9519\u8bef\u7c7b\u578b\u5b9a\u4f4d"), ("\u5b9e\u9a8c\u8bc4\u4f30", "\u591a\u6307\u6807\u9a8c\u8bc1")]
    xs = [100, 500, 900, 1300]
    for i, (x, (t, sub)) in enumerate(zip(xs, items)):
        card(d, (x, y, x + 285, y + 135), t, sub, fill=BLUE_FILL, outline=BLUE)
        if i < 3:
            straight_arrow(d, (x + 285, y + 67), (xs[i + 1] - 15, y + 67))
    d.rounded_rectangle((145, 470, 1655, 645), radius=28, fill="#F8FAFC", outline="#D6DEE8", width=3)
    d.text((210, 520), "\u7814\u7a76\u95ed\u73af\uff1a", font=F_LABEL, fill=INK)
    d.text((430, 526), "\u8868\u793a\u590d\u6742\u5ea6\u5bf9\u6bd4 \u2192 \u521d\u6b21\u751f\u6210 \u2192 \u6267\u884c\u9a8c\u8bc1 \u2192 \u5c40\u90e8\u4fee\u590d \u2192 Spider \u5c0f\u89c4\u6a21\u8fc1\u79fb", font=F_SMALL, fill=MUTED)
    d.text((210, 585), "\u8bc4\u4f30\u91cd\u70b9\uff1a", font=F_LABEL, fill=INK)
    d.text((430, 591), "valid rate, execution match, repair rounds, token, latency, patch minimality", font=F_SMALL, fill=MUTED)
    d.rounded_rectangle((305, 790, 1495, 860), radius=20, fill=RED_FILL, outline=RED, width=3)
    center(d, (900, 825), "\u76ee\u6807\u4e0d\u662f\u53ea\u8dd1\u901a Demo\uff0c\u800c\u662f\u9a8c\u8bc1 SQL+ \u662f\u5426\u63d0\u9ad8\u53ef\u5b9a\u4f4d\u3001\u53ef\u4fee\u590d\u6027", F_NOTE, RED)
    save(img, "docx_technical_route.png")

def motivation_test() -> None:
    img, d = canvas("\u52a8\u673a\u6d4b\u8bd5\u4e0e\u521d\u6b65\u5b9e\u9a8c\u6d41\u7a0b")
    y = 195
    items = [("\u6837\u4f8b\u96c6", "\u81ea\u5efa30\u6761\\nSpider20\u6761"), ("\u8868\u793a\u5bf9\u6bd4", "SQL / SQL+\\nNatSQL / SemQL"), ("\u751f\u6210\u6210\u672c", "token / latency"), ("\u4fee\u590d\u6536\u76ca", "\u5b9a\u4f4d / patch\\n\u6267\u884c\u9a8c\u8bc1")]
    xs = [80, 500, 920, 1340]
    for i, (x, (t, sub)) in enumerate(zip(xs, items)):
        card(d, (x, y, x + 330, y + 160), t, sub, fill=BLUE_FILL, outline=BLUE)
        if i < 3:
            straight_arrow(d, (x + 330, y + 80), (xs[i + 1] - 15, y + 80))
    d.rounded_rectangle((140, 485, 1660, 660), radius=28, fill="#F8FAFC", outline="#D6DEE8", width=3)
    d.text((210, 535), "\u56de\u7b54\u95ee\u9898\uff1a", font=F_LABEL, fill=INK)
    d.text((430, 541), "\u4e3a\u4ec0\u4e48\u9700\u8981 SQL+\uff1f\u5b83\u4e0d\u662f\u4e3a\u4e86\u66f4\u77ed\uff0c\u800c\u662f\u4e3a\u4e86\u7ed3\u6784\u8fb9\u754c\u66f4\u6e05\u6670\u3002", font=F_SMALL, fill=MUTED)
    d.text((210, 600), "\u89c2\u5bdf\u6307\u6807\uff1a", font=F_LABEL, fill=INK)
    d.text((430, 606), "valid rate, execution match, \u522b\u540d\u4f9d\u8d56, \u8de8\u5b50\u53e5\u5f15\u7528, \u4fee\u590d\u8f6e\u6570", font=F_SMALL, fill=MUTED)
    d.rounded_rectangle((275, 795, 1525, 865), radius=20, fill=RED_FILL, outline=RED, width=3)
    center(d, (900, 830), "\u5b9e\u9a8c\u670d\u52a1\u4e8e\u7814\u7a76\u52a8\u673a\uff1aSQL+ \u7684\u4ef7\u503c\u4e3b\u8981\u4f53\u73b0\u5728\u540e\u7eed\u8bca\u65ad\u4e0e\u4fee\u590d", F_NOTE, RED)
    save(img, "docx_motivation_test_flow.png")

def repair_loop() -> None:
    img, d = canvas("SQL+ 层局部诊断与反馈修正闭环")
    y = 190
    top = [(110, "SQL+", "步骤化表示"), (475, "Translator", "转 SQL"), (840, "Executor", "执行反馈"), (1205, "Critic", "错误定位")]
    for i, (x, t, s) in enumerate(top):
        fill, outline = (GREEN_FILL, GREEN) if t in {"Translator", "Executor"} else (BLUE_FILL, BLUE)
        if t == "Critic":
            fill, outline = RED_FILL, RED
        card(d, (x, y, x + 285, y + 135), t, s, fill=fill, outline=outline)
        if i < 3:
            straight_arrow(d, (x + 285, y + 67), (top[i + 1][0] - 15, y + 67), color=RED if t == "Executor" else LINE)
    by = 560
    bottom = [(255, "Skill Router", "选择技能"), (705, "Repair Skill", "生成 patch"), (1155, "Re-validate", "重新执行")]
    for x, t, s in bottom:
        fill, outline = (GREEN_FILL, GREEN) if t == "Re-validate" else (RED_FILL, RED)
        card(d, (x, by, x + 320, by + 135), t, s, fill=fill, outline=outline)
    curve_arrow(d, bezier((1345, y + 135), (1365, 430), (420, 410), (415, by)), color=RED)
    straight_arrow(d, (575, by + 67), (705, by + 67), color=RED)
    straight_arrow(d, (1025, by + 67), (1155, by + 67), color=RED)
    curve_arrow(d, bezier((1315, by), (1320, 455), (620, 450), (618, y + 135)), color=RED)
    d.rounded_rectangle((285, 805, 1515, 875), radius=20, fill=RED_FILL, outline=RED, width=3)
    center(d, (900, 840), "失败反馈进入 Critic → Router → Skill，patch 后再转换和执行", F_NOTE, RED)
    save(img, "docx_sqlplus_multi_agent_loop.png")


def main() -> None:
    system_architecture()
    technical_route()
    motivation_test()
    repair_loop()
    print(OUT_DIR)


if __name__ == "__main__":
    main()
