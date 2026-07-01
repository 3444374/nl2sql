const fs = require("fs");
const path = require("path");

const ECHARTS_HOME = process.env.ECHARTS_HOME || "D:/Tools/echarts";
const echarts = require(path.join(ECHARTS_HOME, "node_modules", "echarts"));
const sharp = require(path.join(ECHARTS_HOME, "node_modules", "sharp"));

const ROOT = path.resolve(__dirname, "../..");
const OUT_DIR = path.join(ROOT, "docs/opening/assets/charts");
fs.mkdirSync(OUT_DIR, { recursive: true });

const WIDTH = 1920;
const HEIGHT = 1080;
const palette = ["#1B4E7A", "#C43C35", "#4F8A5B", "#D18B22", "#6A5FA0", "#718096"];

function baseOption(title, subtitle, option) {
  return Object.assign({
    backgroundColor: "#ffffff",
    title: {
      text: title,
      subtext: subtitle,
      left: "center",
      top: 24,
      textStyle: { fontFamily: "Microsoft YaHei", fontSize: 46, fontWeight: "bold", color: "#17324D" },
      subtextStyle: { fontFamily: "Microsoft YaHei", fontSize: 26, color: "#5B6875" },
    },
    textStyle: { fontFamily: "Microsoft YaHei", fontSize: 26, color: "#17324D" },
    grid: { left: 150, right: 110, top: 205, bottom: 145 },
    legend: { top: 125, left: "center", itemWidth: 34, itemHeight: 18, textStyle: { fontFamily: "Microsoft YaHei", fontSize: 25 } },
    tooltip: { trigger: "axis" },
    color: palette,
  }, option);
}

const charts = {
  chart_baseline_generation: baseOption("初次生成对比：Direct SQL 与 NL2SQL+", "同一批 30 条自建查询；柱越高表示执行结果与 gold SQL 越一致", {
    xAxis: { type: "category", data: ["Direct SQL", "NL2SQL+ v1", "NL2SQL+ v2"], axisLabel: { fontSize: 28 } },
    yAxis: { type: "value", name: "执行一致数 / 30", max: 30, nameTextStyle: { fontSize: 26 }, axisLabel: { fontSize: 24 } },
    series: [{ name: "执行一致", type: "bar", barWidth: 96, data: [16, 13, 17], label: { show: true, position: "top", fontSize: 28, formatter: "{c}/30" } }],
  }),

  chart_ir_complexity: baseOption("中间表示复杂度对比", "SQL+ 不追求更短，而是降低别名依赖与跨子句引用", {
    grid: { left: 150, right: 110, top: 205, bottom: 175 },
    xAxis: { type: "category", data: ["Standard SQL", "SQL+", "SemQL proxy", "NatSQL proxy", "Pipe proxy"], axisLabel: { fontSize: 23, rotate: 12 } },
    yAxis: { type: "value", name: "平均次数", nameTextStyle: { fontSize: 26 }, axisLabel: { fontSize: 24 } },
    series: [
      { name: "别名依赖", type: "bar", data: [2.03, 0.70, 0.90, 1.37, 1.37], label: { show: true, position: "top", fontSize: 24 } },
      { name: "跨子句引用", type: "bar", data: [2.33, 1.00, 1.20, 1.67, 1.67], label: { show: true, position: "top", fontSize: 24 } },
    ],
  }),

  chart_ir_generation_cost: baseOption("不同表示的生成成本与执行效果", "柱表示执行一致数；折线表示平均 token 成本", {
    xAxis: { type: "category", data: ["Direct SQL", "SQL+", "NatSQL proxy", "SemQL proxy"], axisLabel: { fontSize: 25 } },
    yAxis: [
      { type: "value", name: "执行一致数 / 30", max: 30, nameTextStyle: { fontSize: 25 }, axisLabel: { fontSize: 23 } },
      { type: "value", name: "平均 token", nameTextStyle: { fontSize: 25 }, axisLabel: { fontSize: 23 } },
    ],
    series: [
      { name: "执行一致", type: "bar", barWidth: 78, data: [12, 14, 13, 12], label: { show: true, position: "top", fontSize: 25, formatter: "{c}/30" } },
      { name: "平均 token", type: "line", yAxisIndex: 1, smooth: true, symbolSize: 16, lineStyle: { width: 5 }, data: [599.17, 813.03, 740.77, 1028.97], label: { show: true, fontSize: 22 } },
    ],
  }),

  chart_repair_success: baseOption("反馈修正策略对比", "SQL+ Skill Router + Repair Skills 在当前已知失败集上修复成功最高", {
    grid: { left: 150, right: 80, top: 205, bottom: 190 },
    xAxis: { type: "category", data: ["SQL+ Refiner v2", "Direct SQL Refiner", "Schema-Critic", "Step-wise Critic", "SQL+ Router Skills"], axisLabel: { fontSize: 22, rotate: 18 } },
    yAxis: { type: "value", name: "修复成功率", max: 1, nameTextStyle: { fontSize: 26 }, axisLabel: { fontSize: 24, formatter: "{value}" } },
    series: [{ name: "修复成功率", type: "bar", barWidth: 72, data: [0.3077, 0.4286, 0.2308, 0.2308, 1.0], label: { show: true, position: "top", fontSize: 25, formatter: (p) => (p.value * 100).toFixed(1) + "%" } }],
  }),

  chart_spider_subset: baseOption("Spider 小规模子集验证", "conversion smoke test 使用 gold SQL 转 SQL+，不代表端到端生成成绩", {
    grid: { left: 150, right: 80, top: 205, bottom: 185 },
    xAxis: { type: "category", data: ["conversion smoke", "e2e v2", "fresh e2e", "fresh + repair"], axisLabel: { fontSize: 24, rotate: 12 } },
    yAxis: { type: "value", name: "执行一致数 / 20", max: 20, nameTextStyle: { fontSize: 26 }, axisLabel: { fontSize: 24 } },
    series: [{ name: "执行一致", type: "bar", barWidth: 78, data: [20, 13, 19, 20], label: { show: true, position: "top", fontSize: 28, formatter: "{c}/20" } }],
  }),
};

async function render() {
  for (const [name, option] of Object.entries(charts)) {
    const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: WIDTH, height: HEIGHT });
    chart.setOption(option);
    const svg = chart.renderToSVGString();
    const svgPath = path.join(OUT_DIR, `${name}.svg`);
    const pngPath = path.join(OUT_DIR, `${name}.png`);
    fs.writeFileSync(svgPath, svg, "utf8");
    await sharp(Buffer.from(svg)).resize(WIDTH, HEIGHT).png().toFile(pngPath);
    chart.dispose();
  }
  console.log(OUT_DIR);
}

render().catch((err) => {
  console.error(err);
  process.exit(1);
});
