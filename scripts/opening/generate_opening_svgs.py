from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "opening" / "figures"

BLUE = "#1F4E79"
ORANGE = "#C65911"
GREEN = "#548235"
RED = "#AA3C3C"
DARK = "#2B2B2B"
MUTED = "#666666"
LIGHT = "#EEF2F7"
PALE_BLUE = "#DDEBF7"
PALE_ORANGE = "#FBE5D6"
PALE_GREEN = "#E2EFDA"
WHITE = "#FFFFFF"


def svg_root(width: int = 1200, height: int = 720) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<marker id="arrow-blue" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        f'<path d="M2,2 L10,6 L2,10 Z" fill="{BLUE}" />',
        "</marker>",
        '<marker id="arrow-orange" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        f'<path d="M2,2 L10,6 L2,10 Z" fill="{ORANGE}" />',
        "</marker>",
        '<style><![CDATA[',
        "text { font-family: 'Microsoft YaHei', 'Noto Sans CJK SC', Arial, sans-serif; }",
        ".title { font-size: 34px; font-weight: 700; fill: #1F4E79; }",
        ".subtitle { font-size: 20px; fill: #666666; }",
        ".box-title { font-size: 20px; font-weight: 700; fill: #2B2B2B; }",
        ".box-text { font-size: 17px; fill: #2B2B2B; }",
        ".small { font-size: 15px; fill: #2B2B2B; }",
        ".note { font-size: 17px; fill: #C65911; }",
        "]]></style>",
        "</defs>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{WHITE}"/>',
    ]


def end_svg(parts: list[str]) -> str:
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def text(parts: list[str], x: int, y: int, value: str, cls: str = "box-text", anchor: str = "start") -> None:
    parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{escape(value)}</text>')


def multiline_text(parts: list[str], x: int, y: int, lines: list[str], cls: str = "box-text", anchor: str = "middle", gap: int = 24) -> None:
    parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">')
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else gap
        parts.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
    parts.append("</text>")


def box(parts: list[str], x: int, y: int, w: int, h: int, fill: str, stroke: str, lines: list[str], cls: str = "box-text") -> None:
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    start_y = y + h // 2 - (len(lines) - 1) * 13
    multiline_text(parts, x + w // 2, start_y, lines, cls=cls)


def arrow(parts: list[str], x1: int, y1: int, x2: int, y2: int, color: str = BLUE) -> None:
    marker = "arrow-orange" if color == ORANGE else "arrow-blue"
    parts.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="3" marker-end="url(#{marker})"/>'
    )


def save(name: str, content: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / name).write_text(content, encoding="utf-8")


def traditional_text_to_sql() -> str:
    p = svg_root()
    text(p, 60, 60, "传统 Text-to-SQL 流程及其问题", "title")
    labels = [
        ("自然语言问题", PALE_BLUE),
        ("LLM / 解析器", PALE_BLUE),
        ("标准 SQL", PALE_ORANGE),
        ("数据库执行", PALE_GREEN),
        ("查询结果", PALE_GREEN),
    ]
    xs = [70, 280, 490, 700, 910]
    for i, (label, fill) in enumerate(labels):
        box(p, xs[i], 140, 155, 85, fill, BLUE, [label], "box-title")
        if i < len(labels) - 1:
            arrow(p, xs[i] + 160, 182, xs[i + 1] - 10, 182)
    box(p, 330, 300, 540, 86, PALE_ORANGE, ORANGE, ["错误反馈通常只作用在整条 SQL 上"], "box-title")
    arrow(p, 760, 240, 760, 294, ORANGE)
    text(p, 105, 455, "主要问题", "box-title")
    bullets = [
        "SQL 子句之间耦合强，join、filter、aggregation、order 会互相影响。",
        "执行报错往往只说明最终 SQL 出错，不一定指出哪一步语义错误。",
        "整条 SQL 重写容易修复一个错误，同时破坏原本正确的部分。",
    ]
    for i, item in enumerate(bullets):
        text(p, 130, 500 + i * 42, f"• {item}", "box-text")
    return end_svg(p)


def sqlplus_multi_agent_loop() -> str:
    p = svg_root()
    text(p, 60, 60, "SQL+ 多智能体生成与反馈修正闭环", "title")
    top = [
        ("Intent Agent", "识别查询目标"),
        ("Schema Agent", "表字段与关系"),
        ("Planner Agent", "SQL+ 步骤计划"),
        ("SQL+ Generator", "生成中间表示"),
    ]
    for i, (a, b) in enumerate(top):
        x = 70 + i * 270
        box(p, x, 125, 210, 90, PALE_BLUE, BLUE, [a, b], "box-text")
        if i < 3:
            arrow(p, x + 218, 170, x + 260, 170)
    mid = [
        ("Translator", "SQL+ 转 SQL"),
        ("Executor", "执行并返回反馈"),
        ("Critic Agent", "定位错误步骤"),
        ("Skill Router", "选择修复技能"),
    ]
    for i, (a, b) in enumerate(mid):
        x = 70 + i * 270
        box(p, x, 305, 210, 90, PALE_GREEN, GREEN, [a, b], "box-text")
        if i < 3:
            arrow(p, x + 218, 350, x + 260, 350)
    arrow(p, 1015, 220, 1015, 295, ORANGE)
    box(p, 280, 500, 250, 90, PALE_ORANGE, ORANGE, ["Repair Skill", "局部 SQL+ patch"], "box-text")
    box(p, 680, 500, 250, 90, PALE_ORANGE, ORANGE, ["重新验证", "SQL+ → SQL → 执行"], "box-text")
    arrow(p, 530, 545, 670, 545, ORANGE)
    arrow(p, 805, 500, 805, 405, ORANGE)
    text(p, 60, 660, "设计意图：每个 Agent 输出可检查中间产物，避免把多智能体退化成多个 prompt 的简单串联。", "note")
    return end_svg(p)


def sqlplus_stepwise_ir() -> str:
    p = svg_root()
    text(p, 60, 60, "SQL+ 表达逻辑：线性步骤与修复锚点", "title")
    steps = ["FROM", "JOIN", "WHERE", "GROUP", "AGG", "HAVING", "SELECT", "ORDER", "LIMIT"]
    for i, step in enumerate(steps):
        fill = BLUE if i % 2 == 0 else ORANGE
        box(p, 55 + i * 125, 130, 95, 60, fill, fill, [step], "box-title")
        p[-2] = p[-2].replace('fill="#2B2B2B"', 'fill="#FFFFFF"')
        if i < len(steps) - 1:
            arrow(p, 155 + i * 125, 160, 175 + i * 125, 160)
    rows = [
        ("WHERE", "值链接、日期边界、隐含过滤", "value-linking skill"),
        ("JOIN", "连接路径、连接方向、冗余 join", "join repair skill"),
        ("GROUP / AGG", "聚合口径、别名、HAVING 引用", "aggregation repair skill"),
        ("SELECT", "输出列、别名、列顺序", "projection repair skill"),
        ("ORDER / LIMIT", "排序字段、方向、top-k", "order repair skill"),
    ]
    text(p, 100, 270, "SQL+ 步骤", "box-title")
    text(p, 320, 270, "主要诊断对象", "box-title")
    text(p, 760, 270, "对应 repair skill", "box-title")
    for i, (a, b, c) in enumerate(rows):
        y = 315 + i * 62
        box(p, 80, y - 28, 150, 42, LIGHT, BLUE, [a], "small")
        box(p, 270, y - 28, 390, 42, WHITE, BLUE, [b], "small")
        box(p, 720, y - 28, 330, 42, PALE_GREEN, GREEN, [c], "small")
    text(p, 60, 660, "解释：SQL+ 的步骤不是展示用标签，而是错误定位、技能路由和局部 patch 的操作单元。", "note")
    return end_svg(p)


def experiment_logic_map() -> str:
    p = svg_root()
    text(p, 60, 60, "实验组织逻辑：从研究问题到指标验证", "title")
    items = [
        ("H1 表达可行", "SQL+ 能否稳定转换并执行", "SQL+ 转换实验\nSpider smoke test"),
        ("H2 表达差异", "为什么使用 SQL+", "IR 复杂度实验\nIR 生成成本实验"),
        ("H3 生成效果", "中间表示是否改善初次生成", "Direct SQL vs SQL+ baseline"),
        ("H4 修复收益", "修复收益能否抵消额外开销", "repairability 指标\nSkill Router 实验"),
    ]
    for i, (h, q, e) in enumerate(items):
        y = 130 + i * 125
        box(p, 80, y, 180, 76, PALE_BLUE, BLUE, [h], "box-title")
        arrow(p, 270, y + 38, 330, y + 38)
        box(p, 350, y, 330, 76, LIGHT, BLUE, [q], "box-text")
        arrow(p, 690, y + 38, 750, y + 38)
        box(p, 770, y, 330, 76, PALE_GREEN, GREEN, e.split("\n"), "box-text")
    text(p, 60, 660, "实验不只是展示结果，而是逐项回答 SQL+ 的必要性、代价和修复收益。", "note")
    return end_svg(p)


def repair_skill_router() -> str:
    p = svg_root()
    text(p, 60, 60, "Critic Agent 与 Skill Router 的修复流程", "title")
    box(p, 90, 135, 210, 82, PALE_BLUE, BLUE, ["执行反馈", "错误信息 / 异常结果"], "box-text")
    arrow(p, 305, 176, 375, 176)
    box(p, 390, 135, 210, 82, PALE_GREEN, GREEN, ["Critic Agent", "错误类型 + 可疑步骤"], "box-text")
    arrow(p, 605, 176, 675, 176)
    box(p, 690, 135, 210, 82, PALE_ORANGE, ORANGE, ["Skill Router", "路由到局部技能"], "box-text")
    skills = [
        ("value-linking", "WHERE 值和过滤条件"),
        ("order", "ORDER / LIMIT"),
        ("aggregation", "GROUP / AGG / HAVING"),
        ("join", "JOIN path"),
        ("projection", "SELECT 输出列"),
    ]
    for i, (a, b) in enumerate(skills):
        x = 80 + i * 220
        box(p, x, 335, 185, 86, WHITE, ORANGE, [a, b], "small")
        arrow(p, 795, 225, x + 92, 330, ORANGE)
    box(p, 390, 535, 420, 78, PALE_GREEN, GREEN, ["Executor 重新验证", "SQL+ patch → SQL → 执行结果"], "box-text")
    for i in range(len(skills)):
        x = 80 + i * 220
        arrow(p, x + 92, 425, 565, 530, ORANGE)
    text(p, 60, 670, "对比整条 SQL 重写：该流程把修改限制在可疑步骤，便于控制 patch 范围。", "note")
    return end_svg(p)


def research_positioning() -> str:
    p = svg_root()
    text(p, 60, 60, "研究定位：SQL+ 与已有中间表示的区别", "title")
    text(p, 575, 650, "越接近 SQL 生态与执行链路", "subtitle", "middle")
    text(p, 48, 360, "越强调语义抽象", "subtitle")
    arrow(p, 160, 610, 1020, 610)
    arrow(p, 160, 610, 160, 120)
    items = [
        (300, 470, "NatSQL", "更自然语言化\n降低部分 SQL 书写复杂度", PALE_BLUE, BLUE),
        (360, 250, "SemQL", "语义解析树\n结构约束更强", PALE_GREEN, GREEN),
        (720, 470, "Pipe-style", "线性数据流\n贴近 SQL 扩展", PALE_ORANGE, ORANGE),
        (790, 260, "SQL+", "NL2SQL 中间表示\n可转换、可定位、可修复", "#FFF2CC", ORANGE),
    ]
    for x, y, name, desc, fill, stroke in items:
        box(p, x, y, 220, 110, fill, stroke, [name] + desc.split("\n"), "box-text")
    text(p, 60, 685, "SQL+ 的定位不是替代 SemQL 或 NatSQL，而是面向执行反馈和局部修复重新设计中间表示。", "note")
    return end_svg(p)


def main() -> None:
    figures = {
        "traditional_text_to_sql.svg": traditional_text_to_sql(),
        "sqlplus_multi_agent_loop.svg": sqlplus_multi_agent_loop(),
        "sqlplus_stepwise_ir.svg": sqlplus_stepwise_ir(),
        "experiment_logic_map.svg": experiment_logic_map(),
        "repair_skill_router.svg": repair_skill_router(),
        "research_positioning.svg": research_positioning(),
    }
    for name, content in figures.items():
        save(name, content)
        print(OUT_DIR / name)


if __name__ == "__main__":
    main()
