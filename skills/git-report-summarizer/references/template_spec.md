# 模板占位符规范

`scripts/run_report.py` 支持以下占位符，模板文件建议使用 UTF-8：

- `{{period_title}}`：周期标题（今日日报/本周周报/本月月报/自定义汇报）
- `{{time_range}}`：时间范围文本
- `{{completed_items}}`：按仓库展开的完成事项 Markdown 列表
- `{{in_progress_items}}`：进行中事项 Markdown 列表
- `{{risk_items}}`：风险与阻塞事项 Markdown 列表
- `{{next_plan_items}}`：下阶段计划 Markdown 列表
- `{{period_overview}}`：本周期总结（按仓库提炼的重点事项）
- `{{repo_daily_details}}`：按仓库+日期展开的明细文本
- `{{daily_table}}`：按日期/仓库聚合的 Markdown 表格
- `{{failed_repos}}`：采集失败仓库 Markdown 列表
- `{{filtered_count}}`：被过滤的噪声提交数量

## 样式模板命名

- 简洁版：`{period}.md.j2`
- 管理版：`{period}.management.md.j2`
- 技术版：`{period}.technical.md.j2`
- 仓库按天版：`{period}.repo-daily.md.j2`

其中 `period` 为 `daily`、`weekly`、`monthly`。

## 模板最小示例

```md
# {{period_title}}
时间：{{time_range}}

## 完成事项
{{completed_items}}

## 风险与问题
{{risk_items}}
```

## 推荐导出格式

- 读者汇报：优先 Markdown（结构化标题 + 列表）
- 跨仓库按天统计：使用 `{{daily_table}}` 或 `--table-output-csv`
- 二次加工/系统集成：使用 `raw_commits.json`
