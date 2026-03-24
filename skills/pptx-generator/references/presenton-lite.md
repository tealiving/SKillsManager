# Presenton-Lite（通用规则）

## 目标
- 将主题扩展为 5–15 页演示文稿。
- 必含：封面、目录、内容页、图表页（可选）、结束页。

## 内容规范
- 每页 2–5 条要点，避免过长段落。
- 标题与内容要匹配，避免“空标题”。
- 图表页需配简短结论（1–3 条）。

## 结构化数据
参见 `schema.md`，由 JSON 输出结构化内容。
如未提供 agenda/section，且 slides 中包含 section 字段，将自动生成目录与章节页（可通过 meta.auto_agenda/auto_sections 关闭）。

## 版式类型
- content / image-left / image-right
- chart / timeline
- table / icon-grid
- comparison / pros-cons
- swot / risk-matrix / matrix-2x2 / four-quadrant
