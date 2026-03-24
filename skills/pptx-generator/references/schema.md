# JSON 结构规范（通用 PPT）

## 顶层结构
```json
{
  "meta": {
    "title": "主题",
    "subtitle": "副标题/日期",
    "author": "汇报人/团队",
    "theme": "tech-neon",
    "template": "tech-neon",
    "output": "output.pptx"
  },
  "slides": [
    { "type": "title", "title": "...", "subtitle": "...", "tagline": "...", "meta": "..." },
    { "type": "agenda", "title": "目录", "items": ["...", "..."] },
    { "type": "section", "title": "章节标题", "subtitle": "章节说明" },
    { "type": "content", "title": "关键进展", "bullets": ["...", "..."] },
    {
      "type": "chart",
      "title": "核心指标",
      "bullets": ["结论 1", "结论 2"],
      "chart": {
        "type": "line",
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
          { "name": "DAU(万)", "values": [10.2, 11.4, 12.0, 12.6] }
        ]
      }
    },
    { "type": "timeline", "title": "里程碑", "items": ["M1 需求冻结", "M2 灰度发布"] },
    { "type": "content", "title": "总结", "bullets": ["行动 1", "行动 2"] }
  ]
}
```

## meta 字段
- `title/subtitle/author`：封面与默认信息。
- `theme`：主题提示词（会用于模板选择）。
- `template`：模板名称或模板文件名（可选）。
- `output`：输出文件名（可选）。
- `auto_agenda`：是否自动生成目录页（默认 true）。
- `auto_sections`：是否根据 section 自动生成章节页（默认 true）。

## slides 字段
- `type`：title/agenda/section/content/chart/timeline/table/icon-grid/comparison/pros-cons/swot/risk-matrix/matrix-2x2/four-quadrant
- `title`：页面标题
- `bullets/items`：要点列表（2–5 条）
- `layout_type`：可选，直接指定版式（chart/timeline/comparison 等）
- `section`：可选，标记所属章节，用于自动目录/章节页。
- `section_subtitle`：可选，自动章节页副标题。

> 若未显式提供 agenda/section，且 slides 中存在 section 字段，将自动插入目录页与章节页。

### chart 结构
- `chart.type`：column/line/stacked/stacked-100/area/multi-axis
- `chart.categories`：类目标签（可选）
- `chart.series`：系列列表

### comparison 结构（两列对比）
```json
{
  "type": "comparison",
  "title": "方案对比",
  "columns": [
    { "title": "方案 A", "items": ["优点 1", "优点 2"] },
    { "title": "方案 B", "items": ["优点 1", "优点 2"] }
  ]
}
```

### table 结构
```json
{
  "type": "table",
  "title": "指标明细",
  "bullets": ["结论 1", "结论 2"],
  "table": {
    "style": "striped",
    "headers": ["指标", "本周", "上周"],
    "rows": [
      ["DAU", "12.4万", "11.8万"],
      ["转化率", "3.8%", "3.4%"]
    ]
  }
}
```

- `table.style`：striped/contrast/soft，覆盖主题默认表格风格。

### icon-grid 结构
```json
{
  "type": "icon-grid",
  "title": "关键能力",
  "icons": [
    { "label": "稳定性", "value": "99.9%", "badge": "S" },
    { "label": "效率", "value": "+18%", "badge": "E" },
    { "label": "体验", "value": "4.8/5", "badge": "U" },
    { "label": "成本", "value": "-12%", "badge": "C" }
  ]
}
```

### pros-cons 结构
```json
{
  "type": "pros-cons",
  "title": "利弊分析",
  "pros": ["优势 1", "优势 2"],
  "cons": ["不足 1", "不足 2"]
}
```

### swot 结构
```json
{
  "type": "swot",
  "title": "SWOT 分析",
  "swot": {
    "strengths": ["S1", "S2"],
    "weaknesses": ["W1", "W2"],
    "opportunities": ["O1", "O2"],
    "threats": ["T1", "T2"]
  }
}
```

### risk-matrix 结构
```json
{
  "type": "risk-matrix",
  "title": "风险矩阵",
  "risks": [
    { "label": "供应延期", "impact": 4, "probability": 3 },
    { "label": "质量波动", "impact": 2, "probability": 4 }
  ]
}
```

### matrix-2x2 / four-quadrant
```json
{
  "type": "matrix-2x2",
  "title": "策略矩阵",
  "quadrants": [
    { "title": "高价值", "items": ["A", "B"] },
    { "title": "高潜力", "items": ["C"] },
    { "title": "低风险", "items": ["D"] },
    { "title": "待观察", "items": ["E"] }
  ]
}
```
