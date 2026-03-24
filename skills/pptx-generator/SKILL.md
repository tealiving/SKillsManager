---
name: pptx-generator
description: 通用 PPT/PPTX 生成与模板渲染技能。用于用户要求生成演示文稿/幻灯片/汇报/周报/大纲/图表页/时间线，或需要把结构化 JSON 自动渲染成 PPTX，或需要选择主题模板并输出可运行的 Python 脚本时使用。
---

# PPTX Generator

## 首选工作流（通用 PPT）
1. 明确输入：主题、受众、语气、页数、风格/主题、关键数据（用户仅提供内容也可以）。
2. 产出大纲：5–15 页（含封面、目录、章节页、内容页、图表页、结束页）。
3. 生成结构化 JSON：见 `references/schema.md`。
4. 选择主题模板：见 `references/themes.md`。
5. **自动选主题并渲染**：未指定主题时按内容自动选择模板，再调用 `scripts/json_pptx_runner.py`（JSON -> PPTX）。
6. **仅当用户明确要求**，才只输出 JSON 或脚本而不渲染。

## 触发模板（LLM 输出格式）
请输出 **JSON**，不要输出解释文字。JSON 结构必须符合 `references/schema.md`：
```json
{
  "meta": {
    "title": "演示主题",
    "subtitle": "日期/范围",
    "author": "汇报人/团队",
    "theme": "tech-neon"
  },
  "slides": [
    { "type": "title", "title": "...", "subtitle": "...", "tagline": "...", "meta": "..." },
    { "type": "agenda", "title": "目录", "items": ["...", "..."] },
    { "type": "content", "title": "关键进展", "bullets": ["...", "..."] },
    { "type": "chart", "title": "核心指标", "bullets": ["结论 1"], "chart": { "type": "line", "categories": ["Q1","Q2"], "series": [{"name":"DAU","values":[10,12]}] } },
    { "type": "timeline", "title": "里程碑", "items": ["M1", "M2"] },
    { "type": "content", "title": "总结", "bullets": ["行动 1", "行动 2"] }
  ]
}
```

## 何时使用哪条路径
- **常规生成（默认）**：输出 JSON 后立即执行 `scripts/json_pptx_runner.py` 生成 PPTX。
- **有模板文件**：将模板放入 `assets/templates/`（或 `assets/templates/external/`），并在 JSON 的 `meta.template` 指定模板名。
- **仅输出代码**：用户明确要求时，才只生成 Python 脚本或 JSON，不执行渲染。

## 输出要求
- 每页 2–5 个要点，避免过长段落。
- 图表页必须包含 `chart.type` 与 `chart.series`。
- 时间线页使用 `type: timeline`。
- 必含封面与结束页。
- 目录/章节页可省略，系统将根据 `section` 字段自动生成（可用 `meta.auto_agenda/auto_sections` 关闭）。
- 用户只提供内容时：先生成 JSON，再渲染成 PPTX。
- `meta.theme` 可省略；缺省时按标题/内容自动匹配主题模板。

## 资源
- `scripts/json_pptx_runner.py`：JSON -> slides_data -> PPTX。
- `scripts/pptx_template_renderer.py`：主题模板渲染器（支持 chart/timeline/comparison/swot/risk-matrix 等版式）。
- `assets/templates/`：主题模板库。
- `references/schema.md`：JSON 结构规范。
- `references/themes.md`：主题映射与推荐场景。

## ?????QA?
- ??????????? `--qa`??? JSON ? `meta.qa` ?? `true`?
- ?????`--qa-strict` ? `meta.qa.strict` ? `true` ?????????? 0 ????
- ?????`--qa-out` ? `meta.qa.report` ??????? `<output>.qa.txt`?
- ????????? markitdown ?? PPTX ????? `tools.pptx_qa.scan_placeholders()` ??????
- ?? QA?`--qa-thumbs` ??????????????????????

