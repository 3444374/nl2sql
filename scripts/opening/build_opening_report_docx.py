from __future__ import annotations

import argparse
import html
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
CONTENT_WIDTH = 8306
SYSTEM_FIGURE_MARKER = "{{FIGURE_SYSTEM_ARCHITECTURE}}"
TECHNICAL_ROUTE_MARKER = "{{FIGURE_TECHNICAL_ROUTE}}"
MOTIVATION_TEST_MARKER = "{{FIGURE_MOTIVATION_TEST_FLOW}}"
LOOP_FIGURE_MARKER = "{{FIGURE_SQLPLUS_MULTI_AGENT_LOOP}}"

FIGURES = {
    SYSTEM_FIGURE_MARKER: {
        "title": "\u56fe 1  SQL+ \u591a\u667a\u80fd\u4f53\u81ea\u7136\u8bed\u8a00\u6570\u636e\u5e93\u67e5\u8be2\u751f\u6210\u4e0e\u53cd\u9988\u4fee\u6b63\u6846\u67b6",
        "rel_id": "rIdSqlplusSystemArchitecture",
        "target": "media/docx_system_architecture.png",
        "source": "docs/opening/assets/png/docx_system_architecture.png",
        "name": "docx_system_architecture.png",
        "descr": "SQL+ \u591a\u667a\u80fd\u4f53\u53cd\u9988\u4fee\u6b63\u6846\u67b6",
        "doc_id": "1001",
        "explain": "\u56fe 1 \u5c55\u793a\u672c\u6587\u62df\u7814\u7a76\u7cfb\u7edf\u7684\u603b\u4f53\u95ed\u73af\uff1a\u7528\u6237\u95ee\u9898\u9996\u5148\u88ab\u8f6c\u5316\u4e3a SQL+ \u4e2d\u95f4\u8868\u793a\uff0c\u518d\u7ecf\u8f6c\u6362\u5668\u751f\u6210 SQL \u5e76\u6267\u884c\uff1b\u5f53\u6267\u884c\u7ed3\u679c\u6216\u8bed\u4e49\u68c0\u67e5\u53d1\u73b0\u95ee\u9898\u65f6\uff0c\u9519\u8bef\u53cd\u9988\u8fdb\u5165 Critic Agent\u3001Skill Router \u548c Repair Skill\uff0c\u7531\u5c40\u90e8\u6280\u80fd\u4fee\u6539 SQL+ \u7684\u5177\u4f53\u6b65\u9aa4\uff0c\u800c\u4e0d\u662f\u6574\u6761 SQL \u91cd\u65b0\u751f\u6210\u3002",
    },
    TECHNICAL_ROUTE_MARKER: {
        "title": "\u56fe 2  \u8bfe\u9898\u6280\u672f\u8def\u7ebf",
        "rel_id": "rIdSqlplusTechnicalRoute",
        "target": "media/docx_technical_route.png",
        "source": "docs/opening/assets/png/docx_technical_route.png",
        "name": "docx_technical_route.png",
        "descr": "SQL+ \u8bfe\u9898\u6280\u672f\u8def\u7ebf",
        "doc_id": "1002",
        "explain": "\u56fe 2 \u6982\u62ec\u672c\u6587\u7684\u6280\u672f\u8def\u7ebf\uff1a\u5148\u5b9a\u4e49 SQL+ \u8bed\u6cd5\u548c\u8f6c\u6362\u673a\u5236\uff0c\u518d\u7814\u7a76\u81ea\u7136\u8bed\u8a00\u5230 SQL+ \u7684\u751f\u6210\u65b9\u6cd5\uff0c\u968f\u540e\u5f15\u5165\u6267\u884c\u53cd\u9988\u3001\u9519\u8bef\u8bca\u65ad\u548c\u5c40\u90e8\u4fee\u590d\uff0c\u6700\u540e\u4ece\u6b63\u786e\u7387\u3001\u53ef\u6267\u884c\u7387\u3001\u4fee\u590d\u8f6e\u6570\u3001token \u6210\u672c\u3001\u5ef6\u8fdf\u548c patch minimality \u7b49\u7ef4\u5ea6\u8fdb\u884c\u8bc4\u4f30\u3002",
    },
    MOTIVATION_TEST_MARKER: {
        "title": "\u56fe 3  \u52a8\u673a\u6d4b\u8bd5\u4e0e\u521d\u6b65\u5b9e\u9a8c\u6d41\u7a0b",
        "rel_id": "rIdSqlplusMotivationTestFlow",
        "target": "media/docx_motivation_test_flow.png",
        "source": "docs/opening/assets/png/docx_motivation_test_flow.png",
        "name": "docx_motivation_test_flow.png",
        "descr": "SQL+ \u52a8\u673a\u6d4b\u8bd5\u5b9e\u9a8c\u6d41\u7a0b",
        "doc_id": "1003",
        "explain": "\u56fe 3 \u8bf4\u660e\u5f00\u9898\u9636\u6bb5\u7684\u521d\u6b65\u5b9e\u9a8c\u5982\u4f55\u670d\u52a1\u7814\u7a76\u52a8\u673a\u3002\u5b9e\u9a8c\u4e0d\u662f\u53ea\u6bd4\u8f83 SQL+ \u662f\u5426\u66f4\u77ed\uff0c\u800c\u662f\u6bd4\u8f83\u4e0d\u540c\u8868\u793a\u5728\u751f\u6210\u3001\u8f6c\u6362\u3001\u6267\u884c\u548c\u4fee\u590d\u9636\u6bb5\u7684\u6210\u672c\u4e0e\u6536\u76ca\uff0c\u91cd\u70b9\u89c2\u5bdf SQL+ \u662f\u5426\u80fd\u63d0\u4f9b\u66f4\u6e05\u6670\u7684\u6b65\u9aa4\u8fb9\u754c\u548c\u66f4\u7a33\u5b9a\u7684\u9519\u8bef\u5b9a\u4f4d\u5165\u53e3\u3002",
    },
    LOOP_FIGURE_MARKER: {
        "title": "\u56fe 4  SQL+ \u5c42\u5c40\u90e8\u8bca\u65ad\u4e0e\u53cd\u9988\u4fee\u6b63\u95ed\u73af",
        "rel_id": "rIdSqlplusMultiAgentLoop",
        "target": "media/docx_sqlplus_multi_agent_loop.png",
        "source": "docs/opening/assets/png/docx_sqlplus_multi_agent_loop.png",
        "name": "docx_sqlplus_multi_agent_loop.png",
        "descr": "SQL+ \u591a\u667a\u80fd\u4f53\u5c40\u90e8\u4fee\u590d\u95ed\u73af",
        "doc_id": "1004",
        "explain": "\u56fe 4 \u5c55\u793a\u53cd\u9988\u4fee\u6b63\u7684\u5c40\u90e8\u95ed\u73af\uff1aSQL+ \u5148\u8f6c\u6362\u4e3a SQL \u5e76\u6267\u884c\uff0cExecutor \u8fd4\u56de\u9519\u8bef\u6216\u7ed3\u679c\u5f02\u5e38\uff1bCritic Agent \u5224\u65ad\u9519\u8bef\u7c7b\u578b\u548c\u5bf9\u5e94 SQL+ \u6b65\u9aa4\uff0cSkill Router \u9009\u62e9\u4fee\u590d\u6280\u80fd\uff0cRepair Skill \u53ea\u751f\u6210\u5c40\u90e8 patch\uff0c\u968f\u540e\u91cd\u65b0\u8f6c\u6362\u548c\u6267\u884c\u9a8c\u8bc1\u3002",
    },
}

CHARTS = {
    "baseline_generation": {
        "title": "图 5  初次生成对比实验结果",
        "rel_id": "rIdChartBaselineGeneration",
        "target": "media/chart_baseline_generation.svg",
        "source": "docs/opening/assets/charts/chart_baseline_generation.svg",
        "name": "chart_baseline_generation.svg",
        "descr": "Direct SQL 与 NL2SQL+ 初次生成执行一致数对比",
        "doc_id": "2001",
        "explain": "图 5 将 Direct SQL、NL2SQL+ prompt v1 和 NL2SQL+ prompt v2 的执行一致数转化为柱状图。该实验使用同一批 30 条自建订单分析查询，判断生成 SQL 或 SQL+ 转换后 SQL 的执行结果是否与 gold SQL 一致。结果说明，仅把输出形式换成 SQL+ 并不能显著提高初次生成准确率，SQL+ 的价值需要结合后续诊断与修复环节评估。",
    },
    "ir_complexity": {
        "title": "图 6  中间表示结构复杂度对比",
        "rel_id": "rIdChartIrComplexity",
        "target": "media/chart_ir_complexity.svg",
        "source": "docs/opening/assets/charts/chart_ir_complexity.svg",
        "name": "chart_ir_complexity.svg",
        "descr": "SQL+ 与 Standard SQL、SemQL-style、NatSQL-style、Pipe-style 的结构复杂度对比",
        "doc_id": "2002",
        "explain": "图 6 展示别名依赖和跨子句引用两个与修复难度直接相关的指标。SQL+ 的平均 token 数并不最低，但别名依赖和跨子句引用低于 Standard SQL，说明 SQL+ 的优势不是压缩表达长度，而是把复杂依赖拆到更清晰的步骤边界上，便于后续 Critic Agent 定位错误和 Repair Skill 做局部 patch。",
    },
    "ir_generation_cost": {
        "title": "图 7  不同中间表示的生成成本与执行效果",
        "rel_id": "rIdChartIrGenerationCost",
        "target": "media/chart_ir_generation_cost.svg",
        "source": "docs/opening/assets/charts/chart_ir_generation_cost.svg",
        "name": "chart_ir_generation_cost.svg",
        "descr": "Direct SQL、SQL+、NatSQL-style proxy、SemQL-style proxy 的生成成本与执行一致数对比",
        "doc_id": "2003",
        "explain": "图 7 同时展示执行一致数和平均 token 成本。SQL+ 在当前 30 条样例上执行一致数略高于 Direct SQL 和两个 proxy 表示，但平均 token 与延迟也更高。因此，开题阶段不能把 SQL+ 论证为更省成本的表示，而应重点验证它在错误定位、最小 patch 和修复成功率上的补偿性收益。",
    },
    "repair_success": {
        "title": "图 8  反馈修正策略对比",
        "rel_id": "rIdChartRepairSuccess",
        "target": "media/chart_repair_success.svg",
        "source": "docs/opening/assets/charts/chart_repair_success.svg",
        "name": "chart_repair_success.svg",
        "descr": "不同反馈修正方法在当前失败样例集上的修复成功率对比",
        "doc_id": "2004",
        "explain": "图 8 比较单 Refiner、Critic-Refiner 和 SQL+ Skill Router + Repair Skills 的修复成功率。结果显示，单纯增加 Critic 文本或多 Agent 串联并不稳定，明显收益来自“错误类型识别 -> Skill Router -> 局部 Repair Skill -> Executor 验证”的可检查闭环。该结果仍限于当前 13 条已知失败样例，不能表述为大规模 benchmark 结论。",
    },
    "spider_subset": {
        "title": "图 9  Spider 小规模子集验证结果",
        "rel_id": "rIdChartSpiderSubset",
        "target": "media/chart_spider_subset.svg",
        "source": "docs/opening/assets/charts/chart_spider_subset.svg",
        "name": "chart_spider_subset.svg",
        "descr": "Spider concert_singer 20 条小规模子集上的转换、生成与修复结果",
        "doc_id": "2005",
        "explain": "图 9 区分了 gold SQL 转 SQL+ 的 conversion smoke test 与端到端生成实验。conversion smoke test 的 20/20 只证明 SQL+ 转换机制在该子集上可迁移；fresh e2e 的 19/20 和同一输出经 semantic repair 后的 20/20，才是当前端到端可行性的初步证据。该实验仍是小规模子集验证，不是完整 Spider benchmark 成绩。",
    },
}


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def run_props(font_east_asia: str = "宋体", size: int = 24, bold: bool = False, mono: bool = False) -> str:
    ascii_font = "Consolas" if mono else "Times New Roman"
    parts = [
        "<w:rPr>",
        f'<w:rFonts w:ascii="{ascii_font}" w:hAnsi="{ascii_font}" w:eastAsia="{font_east_asia}"/>',
    ]
    if bold:
        parts.append("<w:b/>")
    parts.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    parts.append("</w:rPr>")
    return "".join(parts)


def text_run(text: str, *, font: str = "宋体", size: int = 24, bold: bool = False, mono: bool = False) -> str:
    space = ' xml:space="preserve"' if text[:1].isspace() or text[-1:].isspace() else ""
    return f"<w:r>{run_props(font, size, bold, mono)}<w:t{space}>{esc(text)}</w:t></w:r>"


def paragraph(
    text: str = "",
    *,
    style: str = "body",
    align: str | None = None,
    page_break_before: bool = False,
    shade: str | None = None,
) -> str:
    p_pr: list[str] = ["<w:pPr>"]
    if page_break_before:
        p_pr.append("<w:pageBreakBefore/>")

    if style == "cover_title":
        p_pr.append('<w:spacing w:before="240" w:after="240" w:line="360" w:lineRule="auto"/>')
        p_pr.append('<w:jc w:val="center"/>')
        p_pr.append(f"{run_props('黑体', 36, True)}")
        run = text_run(text, font="黑体", size=36, bold=True)
    elif style == "cover_subtitle":
        p_pr.append('<w:spacing w:before="160" w:after="160" w:line="360" w:lineRule="auto"/>')
        p_pr.append('<w:jc w:val="center"/>')
        run = text_run(text, font="宋体", size=28, bold=True)
    elif style == "h1":
        p_pr.append('<w:spacing w:before="260" w:after="160" w:line="360" w:lineRule="auto"/>')
        p_pr.append(f"{run_props('黑体', 30, True)}")
        run = text_run(text, font="黑体", size=30, bold=True)
    elif style == "h2":
        p_pr.append('<w:spacing w:before="180" w:after="100" w:line="360" w:lineRule="auto"/>')
        p_pr.append(f"{run_props('黑体', 26, True)}")
        run = text_run(text, font="黑体", size=26, bold=True)
    elif style == "h3":
        p_pr.append('<w:spacing w:before="120" w:after="80" w:line="360" w:lineRule="auto"/>')
        p_pr.append(f"{run_props('宋体', 24, True)}")
        run = text_run(text, font="宋体", size=24, bold=True)
    elif style == "code":
        p_pr.append('<w:spacing w:before="80" w:after="80" w:line="300" w:lineRule="auto"/>')
        p_pr.append('<w:ind w:left="420"/>')
        if shade:
            p_pr.append(f'<w:shd w:fill="{shade}"/>')
        run = text_run(text, font="宋体", size=20, mono=True)
    elif style == "reference":
        p_pr.append('<w:spacing w:before="0" w:after="60" w:line="360" w:lineRule="auto"/>')
        p_pr.append('<w:ind w:left="420" w:hanging="420"/>')
        run = text_run(text, font="宋体", size=22)
    else:
        p_pr.append('<w:spacing w:before="0" w:after="80" w:line="360" w:lineRule="auto"/>')
        p_pr.append('<w:ind w:firstLine="480"/>')
        run = text_run(text, font="宋体", size=24)

    if align:
        p_pr.append(f'<w:jc w:val="{align}"/>')
    p_pr.append("</w:pPr>")
    return f"<w:p>{''.join(p_pr)}{run}</w:p>"


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def figure_title(text: str) -> str:
    return (
        "<w:p>"
        '<w:pPr><w:spacing w:before="120" w:after="80" w:line="360" w:lineRule="auto"/>'
        '<w:jc w:val="center"/></w:pPr>'
        f"{text_run(text, font='宋体', size=22, bold=True)}"
        "</w:p>"
    )


def image_paragraph(rel_id: str, name: str, descr: str, doc_id: str) -> str:
    cx = 5275000
    cy = 2967000
    return f"""
<w:p>
  <w:pPr><w:jc w:val="center"/><w:spacing w:before="80" w:after="120" w:line="360" w:lineRule="auto"/></w:pPr>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{cx}" cy="{cy}"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:docPr id="{doc_id}" name="{esc(name)}"/>
        <wp:cNvGraphicFramePr>
          <a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>
        </wp:cNvGraphicFramePr>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="{doc_id}" name="{esc(name)}" descr="{esc(descr)}"/>
                <pic:cNvPicPr><a:picLocks noChangeAspect="1" noChangeArrowheads="1"/></pic:cNvPicPr>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="{rel_id}" cstate="print"/>
                <a:stretch><a:fillRect/></a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
""".strip()


def table_cell(text: str, width: int, *, header: bool = False) -> str:
    fill = "D9EAF7" if header else "FFFFFF"
    font = "黑体" if header else "宋体"
    bold = header
    size = 22 if header else 21
    return (
        "<w:tc>"
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
        '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>'
        f'<w:shd w:fill="{fill}"/>'
        "</w:tcPr>"
        f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:line="300" w:lineRule="auto"/></w:pPr>'
        f'{text_run(text, font=font, size=size, bold=bold)}</w:p>'
        "</w:tc>"
    )


def make_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    cols = max(len(row) for row in rows)
    width = max(900, CONTENT_WIDTH // cols)
    tbl = [
        "<w:tbl>",
        "<w:tblPr>",
        f'<w:tblW w:w="{CONTENT_WIDTH}" w:type="dxa"/>',
        '<w:tblBorders><w:top w:val="single" w:sz="8" w:color="4F81BD"/>'
        '<w:left w:val="single" w:sz="4" w:color="A6A6A6"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="A6A6A6"/>'
        '<w:right w:val="single" w:sz="4" w:color="A6A6A6"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D9D9D9"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D9D9D9"/></w:tblBorders>',
        '<w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>',
        "</w:tblPr>",
        f'<w:tblGrid>{"".join(f"<w:gridCol w:w=\"{width}\"/>" for _ in range(cols))}</w:tblGrid>',
    ]
    for i, row in enumerate(rows):
        row = row + [""] * (cols - len(row))
        tbl.append("<w:tr>")
        for cell in row:
            tbl.append(table_cell(clean_inline(cell), width, header=(i == 0)))
        tbl.append("</w:tr>")
    tbl.append("</w:tbl>")
    tbl.append(paragraph(""))
    return "".join(tbl)


def chart_for_table(rows: list[list[str]]) -> dict[str, str] | None:
    if not rows:
        return None
    header = [clean_inline(cell) for cell in rows[0]]
    header_text = "|".join(header)
    if header == ["方法", "样例数", "SQL/SQL+ 有效", "SQL 可执行", "执行结果一致"]:
        return CHARTS["baseline_generation"]
    if header == ["表示形式", "平均 token", "平均步骤/子句", "平均嵌套深度", "平均别名依赖", "平均跨子句引用", "转换成功"]:
        return CHARTS["ir_complexity"]
    if header == ["方法", "表示有效", "SQL 可执行", "执行一致", "平均总 token", "平均延迟"]:
        return CHARTS["ir_generation_cost"]
    if header[:5] == ["方法", "初始失败样例", "SQL+ 有效", "SQL 可执行", "修复成功"]:
        return CHARTS["repair_success"]
    if header[:5] == ["实验", "样例数", "SQL+ 有效", "SQL 可执行", "执行一致"]:
        return CHARTS["spider_subset"]
    if "平均总 token" in header_text and "平均延迟" in header_text:
        return CHARTS["ir_generation_cost"]
    return None


def image_assets() -> list[dict[str, str]]:
    return list(FIGURES.values()) + list(CHARTS.values())


def clean_inline(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def extract_section(md: str, heading: str, next_heading: str | None) -> str:
    start = md.index(heading)
    if next_heading:
        end = md.index(next_heading, start + len(heading))
        return md[start:end].strip()
    return md[start:].strip()


def demote_headings(text: str, level_shift: int = 0) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("#"):
            hashes, title = line.split(" ", 1)
            new_level = min(6, len(hashes) + level_shift)
            lines.append("#" * new_level + " " + title)
        else:
            lines.append(line)
    return "\n".join(lines)


def build_template_aligned_markdown(source_md: str) -> str:
    background = extract_section(source_md, "# 一、课题背景、目的和意义", "# 二、国内外研究现状")
    status = extract_section(source_md, "# 二、国内外研究现状", "# 三、研究目标与拟解决的关键问题")
    goals = extract_section(source_md, "# 三、研究目标与拟解决的关键问题", "# 四、研究内容")
    content = extract_section(source_md, "# 四、研究内容", "# 五、技术路线")
    route = extract_section(source_md, "# 五、技术路线", "# 六、实验设计与初步结果")
    experiments = extract_section(source_md, "# 六、实验设计与初步结果", "# 七、可行性分析")
    feasibility = extract_section(source_md, "# 七、可行性分析", "# 八、预期创新点")
    innovation = extract_section(source_md, "# 八、预期创新点", "# 九、后续实验计划与进度安排")
    schedule = extract_section(source_md, "# 九、后续实验计划与进度安排", "# 十、预期成果")
    outputs = extract_section(source_md, "# 十、预期成果", "# 十一、精读文献清单")
    intensive = extract_section(source_md, "# 十一、精读文献清单", "# 十二、主要参考文献")
    refs = extract_section(source_md, "# 十二、主要参考文献", "# 签字页")
    sign = extract_section(source_md, "# 签字页", None)

    return "\n\n".join(
        [
            background,
            status,
            "# 三、研究目标与研究内容\n\n"
            + demote_headings(goals.replace("# 三、研究目标与拟解决的关键问题", "").strip(), 1)
            + "\n\n"
            + demote_headings(content.replace("# 四、研究内容", "## 3.3 研究内容"), 1),
            "# 四、研究方案与可行性分析\n\n"
            + SYSTEM_FIGURE_MARKER
            + "\n\n"
            + demote_headings(route.replace("# 五、技术路线", "## 4.1 技术路线"), 1)
            + "\n\n"
            + TECHNICAL_ROUTE_MARKER
            + "\n\n"
            + demote_headings(experiments.replace("# 六、实验设计与初步结果", "## 4.2 实验设计与初步结果"), 1)
            + "\n\n"
            + MOTIVATION_TEST_MARKER
            + "\n\n"
            + LOOP_FIGURE_MARKER
            + "\n\n"
            + demote_headings(feasibility.replace("# 七、可行性分析", "## 4.3 可行性分析"), 1),
            "# 五、进度安排\n\n" + demote_headings(schedule.replace("# 九、后续实验计划与进度安排", "").strip(), 1),
            "# 六、预期成果\n\n"
            + demote_headings(innovation.replace("# 八、预期创新点", "## 6.1 预期创新点"), 1)
            + "\n\n"
            + demote_headings(outputs.replace("# 十、预期成果", "## 6.2 成果形式"), 1),
            "# 七、主要参考文献\n\n"
            + demote_headings(intensive.replace("# 十一、精读文献清单", "## 7.1 精读文献清单"), 1)
            + "\n\n"
            + demote_headings(refs.replace("# 十二、主要参考文献", "## 7.2 主要参考文献"), 1),
            sign,
        ]
    )


def parse_markdown_to_xml(md: str) -> str:
    xml_parts: list[str] = []
    lines = md.splitlines()
    i = 0
    in_code = False
    code_buf: list[str] = []
    while i < len(lines):
        line = lines[i].rstrip()
        if line.strip().startswith("```"):
            if in_code:
                for code_line in code_buf:
                    xml_parts.append(paragraph(code_line, style="code", shade="F2F2F2"))
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue
        if not line.strip() or line.strip() == "---":
            i += 1
            continue
        if line.strip() in FIGURES:
            figure = FIGURES[line.strip()]
            xml_parts.append(image_paragraph(figure["rel_id"], figure["name"], figure["descr"], figure["doc_id"]))
            xml_parts.append(figure_title(figure["title"]))
            xml_parts.append(paragraph(figure["explain"], style="body"))
            i += 1
            continue
        if line.lstrip().startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows: list[list[str]] = []
            for table_line in table_lines:
                cells = [cell.strip() for cell in table_line.strip("|").split("|")]
                if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
                    continue
                rows.append(cells)
            chart = chart_for_table(rows)
            if chart:
                xml_parts.append(image_paragraph(chart["rel_id"], chart["name"], chart["descr"], chart["doc_id"]))
                xml_parts.append(figure_title(chart["title"]))
                xml_parts.append(paragraph(chart["explain"], style="body"))
            else:
                xml_parts.append(make_table(rows))
            continue
        if line.startswith("# "):
            xml_parts.append(paragraph(clean_inline(line[2:]), style="h1"))
        elif line.startswith("## "):
            xml_parts.append(paragraph(clean_inline(line[3:]), style="h2"))
        elif line.startswith("### "):
            xml_parts.append(paragraph(clean_inline(line[4:]), style="h3"))
        elif re.match(r"^\[\d+\]", line.strip()):
            xml_parts.append(paragraph(clean_inline(line.strip()), style="reference"))
        elif re.match(r"^\d+\.\s+", line.strip()):
            xml_parts.append(paragraph(clean_inline(line.strip()), style="body"))
        elif line.strip().startswith("- "):
            xml_parts.append(paragraph(clean_inline(line.strip()[2:]), style="body"))
        else:
            xml_parts.append(paragraph(clean_inline(line.strip()), style="body"))
        i += 1
    return "".join(xml_parts)


def cover_xml() -> str:
    rows = [
        ["学号", "（待填写）"],
        ["姓名", "（待填写）"],
        ["专业", "（待填写）"],
        ["指导教师", "（待填写）"],
        ["院（系、所）", "计算机科学与技术学院"],
    ]
    return "".join(
        [
            paragraph("硕士生论文开题报告", style="cover_title"),
            paragraph("面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究", style="cover_subtitle"),
            paragraph(""),
            make_table(rows),
            paragraph("说明：本报告根据学校硕士研究生论文开题报告模板编排，正文采用中文宋体小四、英文和数字 Times New Roman、小四，1.5 倍行距。", style="body"),
            page_break(),
        ]
    )


def build_docx(template: Path, markdown: Path, output: Path) -> None:
    md = markdown.read_text(encoding="utf-8")
    aligned = build_template_aligned_markdown(md)
    original_xml = zipfile.ZipFile(template).read("word/document.xml").decode("utf-8")
    sect_pr_match = re.findall(r"<w:sectPr[\s\S]*?</w:sectPr>", original_xml)
    if not sect_pr_match:
        raise RuntimeError("Template document.xml does not contain w:sectPr.")
    sect_pr = sect_pr_match[-1]
    prefix = original_xml[: original_xml.index("<w:body>") + len("<w:body>")]
    new_body = cover_xml() + parse_markdown_to_xml(aligned) + sect_pr
    new_xml = prefix + new_body + "</w:body></w:document>"
    ElementTree.fromstring(new_xml.encode("utf-8"))

    output.parent.mkdir(parents=True, exist_ok=True)
    for figure in image_assets():
        figure_path = Path(figure["source"])
        if not figure_path.exists():
            raise FileNotFoundError(figure_path)

    with zipfile.ZipFile(template, "r") as src, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/document.xml":
                data = new_xml.encode("utf-8")
            elif item.filename == "word/_rels/document.xml.rels":
                for figure in image_assets():
                    data = add_image_relationship(data, figure["rel_id"], figure["target"])
            elif item.filename == "[Content_Types].xml":
                data = add_png_content_type(data)
                data = add_svg_content_type(data)
            dst.writestr(item, data)
        for figure in image_assets():
            dst.writestr("word/" + figure["target"], Path(figure["source"]).read_bytes())

    # Final archive-level XML validation.
    with zipfile.ZipFile(output, "r") as check:
        ElementTree.fromstring(check.read("word/document.xml"))
        ElementTree.fromstring(check.read("word/_rels/document.xml.rels"))
        ElementTree.fromstring(check.read("[Content_Types].xml"))


def add_image_relationship(data: bytes, rel_id: str, target: str) -> bytes:
    ElementTree.register_namespace("", REL_NS)
    root = ElementTree.fromstring(data)
    for rel in root:
        if rel.attrib.get("Id") == rel_id:
            return data
    rel = ElementTree.SubElement(root, f"{{{REL_NS}}}Relationship")
    rel.set("Id", rel_id)
    rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel.set("Target", target)
    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)


def add_png_content_type(data: bytes) -> bytes:
    ElementTree.register_namespace("", CONTENT_NS)
    root = ElementTree.fromstring(data)
    for default in root.findall(f"{{{CONTENT_NS}}}Default"):
        if default.attrib.get("Extension") == "png":
            return data
    default = ElementTree.SubElement(root, f"{{{CONTENT_NS}}}Default")
    default.set("Extension", "png")
    default.set("ContentType", "image/png")
    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)


def add_svg_content_type(data: bytes) -> bytes:
    ElementTree.register_namespace("", CONTENT_NS)
    root = ElementTree.fromstring(data)
    for default in root.findall(f"{{{CONTENT_NS}}}Default"):
        if default.attrib.get("Extension") == "svg":
            return data
    default = ElementTree.SubElement(root, f"{{{CONTENT_NS}}}Default")
    default.set("Extension", "svg")
    default.set("ContentType", "image/svg+xml")
    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", default="docs/opening/硕士生开题报告模板0604.docx")
    parser.add_argument("--markdown", default="docs/opening/opening_report_feishu_an_v2.md")
    parser.add_argument("--output", default="docs/opening/硕士生开题报告_SQLPlus多智能体_模板版_曲线图.docx")
    args = parser.parse_args()
    build_docx(Path(args.template), Path(args.markdown), Path(args.output))
    print(args.output)


if __name__ == "__main__":
    main()




