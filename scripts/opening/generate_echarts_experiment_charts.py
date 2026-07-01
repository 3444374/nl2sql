from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "opening" / "assets" / "charts"
HTML_DIR = OUT_DIR / "html"
ECHARTS_JS = ROOT / "tools" / "echarts" / "node_modules" / "echarts" / "dist" / "echarts.min.js"


def find_chrome() -> Path:
    candidates = [
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Chrome or Edge was not found.")


def chart_option(title: str, subtitle: str, option: dict) -> dict:
    base = {
        "backgroundColor": "#ffffff",
        "title": {
            "text": title,
            "subtext": subtitle,
            "left": "center",
            "top": 18,
            "textStyle": {"fontFamily": "Microsoft YaHei", "fontSize": 34, "fontWeight": "bold", "color": "#17324D"},
            "subtextStyle": {"fontFamily": "Microsoft YaHei", "fontSize": 18, "color": "#5B6875"},
        },
        "textStyle": {"fontFamily": "Microsoft YaHei", "fontSize": 18, "color": "#17324D"},
        "grid": {"left": 110, "right": 80, "top": 150, "bottom": 105},
        "legend": {"top": 95, "left": "center", "textStyle": {"fontFamily": "Microsoft YaHei", "fontSize": 17}},
        "tooltip": {"trigger": "axis"},
        "color": ["#2E5E8C", "#B23A3A", "#5C8A4B", "#D99A30", "#6B5B95"],
    }
    base.update(option)
    return base


def html_for(option: dict) -> str:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    html, body {{ margin: 0; padding: 0; width: 1600px; height: 900px; background: white; }}
    #chart {{ width: 1600px; height: 900px; }}
  </style>
  <script src="{ECHARTS_JS.as_uri()}"></script>
</head>
<body>
  <div id="chart"></div>
  <script>
    const chart = echarts.init(document.getElementById('chart'), null, {{ renderer: 'canvas', devicePixelRatio: 2 }});
    chart.setOption({json.dumps(option, ensure_ascii=False)});
  </script>
</body>
</html>"""


def render_chart(name: str, option: dict, chrome: Path) -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = HTML_DIR / f"{name}.html"
    png_path = OUT_DIR / f"{name}.png"
    html_path.write_text(html_for(option), encoding="utf-8")
    cmd = [
        str(chrome),
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--user-data-dir={(OUT_DIR / 'chrome-profile')}",
        "--window-size=1600,900",
        "--virtual-time-budget=2500",
        f"--screenshot={png_path}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, cwd=ROOT)


def charts() -> dict[str, dict]:
    return {
        "chart_baseline_generation": chart_option(
            "初次生成对比：Direct SQL 与 NL2SQL+",
            "样例数均为 30，执行一致数量越高越好",
            {
                "xAxis": {"type": "category", "data": ["Direct SQL", "NL2SQL+ v1", "NL2SQL+ v2"], "axisLabel": {"fontSize": 18}},
                "yAxis": {"type": "value", "name": "执行一致数量 / 30", "max": 30, "axisLabel": {"fontSize": 16}},
                "series": [
                    {
                        "name": "执行一致",
                        "type": "bar",
                        "barWidth": 72,
                        "data": [16, 13, 17],
                        "label": {"show": True, "position": "top", "fontSize": 18, "formatter": "{c}/30"},
                    }
                ],
            },
        ),
        "chart_ir_complexity": chart_option(
            "中间表示复杂度对比",
            "SQL+ 的优势不在更短，而在降低别名依赖和跨子句引用",
            {
                "legend": {"top": 95},
                "xAxis": {"type": "category", "data": ["Standard SQL", "SQL+", "SemQL proxy", "NatSQL proxy", "Pipe proxy"], "axisLabel": {"fontSize": 15, "rotate": 15}},
                "yAxis": {"type": "value", "name": "平均次数", "axisLabel": {"fontSize": 16}},
                "series": [
                    {"name": "别名依赖", "type": "bar", "data": [2.03, 0.70, 0.90, 1.37, 1.37], "label": {"show": True, "position": "top", "fontSize": 15}},
                    {"name": "跨子句引用", "type": "bar", "data": [2.33, 1.00, 1.20, 1.67, 1.67], "label": {"show": True, "position": "top", "fontSize": 15}},
                ],
            },
        ),
        "chart_ir_generation_cost": chart_option(
            "不同表示的生成成本与执行效果",
            "柱表示执行一致数量，折线表示平均 token 成本",
            {
                "legend": {"top": 95},
                "xAxis": {"type": "category", "data": ["Direct SQL", "SQL+", "NatSQL proxy", "SemQL proxy"], "axisLabel": {"fontSize": 17}},
                "yAxis": [
                    {"type": "value", "name": "执行一致数量 / 30", "max": 30, "axisLabel": {"fontSize": 16}},
                    {"type": "value", "name": "平均 token", "axisLabel": {"fontSize": 16}},
                ],
                "series": [
                    {"name": "执行一致", "type": "bar", "barWidth": 62, "data": [12, 14, 13, 12], "label": {"show": True, "position": "top", "fontSize": 16, "formatter": "{c}/30"}},
                    {"name": "平均 token", "type": "line", "yAxisIndex": 1, "smooth": True, "symbolSize": 12, "data": [599.17, 813.03, 740.77, 1028.97], "label": {"show": True, "fontSize": 15}},
                ],
            },
        ),
        "chart_repair_success": chart_option(
            "反馈修正策略对比",
            "SQL+ Skill Router + Repair Skills 在已知失败集上修复成功率最高",
            {
                "grid": {"left": 130, "right": 70, "top": 150, "bottom": 135},
                "xAxis": {"type": "category", "data": ["SQL+ Refiner v2", "Direct SQL Refiner", "Schema-Critic", "Step-wise Critic", "SQL+ Router Skills"], "axisLabel": {"fontSize": 15, "rotate": 20}},
                "yAxis": {"type": "value", "name": "修复成功率", "max": 1, "axisLabel": {"fontSize": 16, "formatter": "{value}"}},
                "series": [
                    {
                        "name": "修复成功率",
                        "type": "bar",
                        "barWidth": 58,
                        "data": [0.3077, 0.4286, 0.2308, 0.2308, 1.0],
                        "label": {"show": True, "position": "top", "fontSize": 16, "formatter": "{c}"},
                    }
                ],
            },
        ),
        "chart_spider_subset": chart_option(
            "Spider 小规模子集验证",
            "注意：conversion smoke test 使用 gold SQL 转 SQL+，不是端到端生成成绩",
            {
                "grid": {"left": 110, "right": 70, "top": 150, "bottom": 135},
                "xAxis": {"type": "category", "data": ["conversion smoke", "e2e v2", "fresh e2e", "fresh + repair"], "axisLabel": {"fontSize": 16, "rotate": 15}},
                "yAxis": {"type": "value", "name": "执行一致数量 / 20", "max": 20, "axisLabel": {"fontSize": 16}},
                "series": [
                    {
                        "name": "执行一致",
                        "type": "bar",
                        "barWidth": 62,
                        "data": [20, 13, 19, 20],
                        "label": {"show": True, "position": "top", "fontSize": 18, "formatter": "{c}/20"},
                    }
                ],
            },
        ),
    }


def main() -> None:
    if not ECHARTS_JS.exists():
        raise FileNotFoundError(f"ECharts was not found at {ECHARTS_JS}")
    chrome = find_chrome()
    for name, option in charts().items():
        render_chart(name, option, chrome)
    print(OUT_DIR)


if __name__ == "__main__":
    main()
