from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "opening" / "figures" / "sqlplus_multi_agent_loop_v2.svg"

BLUE = "#1F4E79"
ORANGE = "#C65911"
GREEN = "#548235"
DARK = "#2B2B2B"
MUTED = "#666666"
LIGHT = "#EEF2F7"
PALE_BLUE = "#DDEBF7"
PALE_ORANGE = "#FBE5D6"
PALE_GREEN = "#E2EFDA"
WHITE = "#FFFFFF"


def text(parts: list[str], x: int, y: int, value: str, cls: str = "box-text", anchor: str = "start") -> None:
    parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{escape(value)}</text>')


def multiline_text(parts: list[str], x: int, y: int, lines: list[str], cls: str = "box-text", anchor: str = "middle") -> None:
    parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">')
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else 24
        parts.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
    parts.append("</text>")


def box(parts: list[str], x: int, y: int, w: int, h: int, fill: str, stroke: str, lines: list[str]) -> None:
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    start_y = y + h // 2 - (len(lines) - 1) * 13
    multiline_text(parts, x + w // 2, start_y, lines)


def arrow(parts: list[str], x1: int, y1: int, x2: int, y2: int, color: str = BLUE) -> None:
    marker = "arrow-orange" if color == ORANGE else "arrow-blue"
    parts.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="3" marker-end="url(#{marker})"/>'
    )


def build_svg() -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="760" viewBox="0 0 1280 760">',
        "<defs>",
        '<marker id="arrow-blue" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        f'<path d="M2,2 L10,6 L2,10 Z" fill="{BLUE}" />',
        "</marker>",
        '<marker id="arrow-orange" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        f'<path d="M2,2 L10,6 L2,10 Z" fill="{ORANGE}" />',
        "</marker>",
        "<style><![CDATA[",
        "text { font-family: 'Microsoft YaHei', 'Noto Sans CJK SC', Arial, sans-serif; }",
        ".title { font-size: 34px; font-weight: 700; fill: #1F4E79; }",
        ".lane { font-size: 17px; font-weight: 700; fill: #666666; }",
        ".box-text { font-size: 17px; fill: #2B2B2B; font-weight: 600; }",
        ".small { font-size: 15px; fill: #2B2B2B; }",
        ".note { font-size: 17px; fill: #C65911; }",
        "]]></style>",
        "</defs>",
        f'<rect x="0" y="0" width="1280" height="760" fill="{WHITE}"/>',
    ]

    text(parts, 60, 58, "SQL+ 多智能体生成与反馈修正闭环", "title")
    text(parts, 80, 115, "生成链路", "lane")
    text(parts, 80, 305, "执行与诊断", "lane")
    text(parts, 80, 500, "局部修复回路", "lane")

    # Forward generation chain.
    box(parts, 90, 140, 185, 82, PALE_BLUE, BLUE, ["用户问题", "Natural language"])
    box(parts, 320, 140, 185, 82, PALE_BLUE, BLUE, ["Intent Agent", "查询意图"])
    box(parts, 550, 140, 185, 82, PALE_BLUE, BLUE, ["Schema Agent", "表字段关系"])
    box(parts, 780, 140, 185, 82, PALE_BLUE, BLUE, ["Planner Agent", "SQL+ 步骤"])
    box(parts, 1010, 140, 185, 82, PALE_BLUE, BLUE, ["SQL+ Generator", "SQL+ 表达"])
    arrow(parts, 280, 181, 315, 181)
    arrow(parts, 510, 181, 545, 181)
    arrow(parts, 740, 181, 775, 181)
    arrow(parts, 970, 181, 1005, 181)

    # Execution and diagnosis chain.
    box(parts, 1010, 335, 185, 82, PALE_GREEN, GREEN, ["Translator", "SQL+ → SQL"])
    box(parts, 780, 335, 185, 82, PALE_GREEN, GREEN, ["Executor", "执行 SQL"])
    box(parts, 550, 335, 185, 82, PALE_ORANGE, ORANGE, ["Critic Agent", "定位错误步骤"])
    box(parts, 320, 335, 185, 82, PALE_ORANGE, ORANGE, ["Skill Router", "选择修复技能"])
    arrow(parts, 1102, 226, 1102, 328, ORANGE)
    arrow(parts, 1005, 376, 970, 376)
    arrow(parts, 775, 376, 740, 376, ORANGE)
    arrow(parts, 545, 376, 510, 376, ORANGE)

    # Repair loop.
    box(parts, 320, 530, 210, 82, PALE_ORANGE, ORANGE, ["Repair Skill", "局部修改 SQL+ 步骤"])
    box(parts, 610, 530, 210, 82, PALE_ORANGE, ORANGE, ["SQL+ Patch", "更新中间表示"])
    arrow(parts, 412, 422, 412, 523, ORANGE)
    arrow(parts, 535, 571, 605, 571, ORANGE)

    # Correct loop-back position: patched SQL+ returns to Translator, then Executor.
    parts.append(
        f'<path d="M 825 571 C 1100 570, 1230 505, 1110 420" '
        f'fill="none" stroke="{ORANGE}" stroke-width="3" marker-end="url(#arrow-orange)"/>'
    )
    text(parts, 1065, 520, "回到 Translator", "small", "middle")
    text(parts, 1065, 543, "重新转换与执行", "small", "middle")

    # Success output.
    box(parts, 780, 645, 230, 62, PALE_GREEN, GREEN, ["最终 SQL / 查询结果"])
    arrow(parts, 873, 421, 873, 638, GREEN)
    text(parts, 1030, 690, "执行通过", "small")

    text(
        parts,
        60,
        735,
        "关键点：失败反馈进入 Critic 和 Router，Repair Skill 只修改 SQL+ 局部步骤，patch 后回到 Translator 和 Executor 重新验证。",
        "note",
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_svg(), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
