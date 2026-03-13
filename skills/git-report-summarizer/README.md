# git-report-summarizer

用于汇总当前 Git 身份在多个仓库中的提交记录，并生成日报、周报、月报。

## What It Does

- 扫描本地多个 Git 仓库，或补充调用 GitHub/Gitee API。
- 过滤噪声提交，提炼每天的工作内容与周期总结。
- 输出 Markdown 周报、CSV 表格和 JSON 原始数据。

## Directory Layout

- `SKILL.md`: 给 agent 使用的技能说明
- `scripts/`: 提交采集、摘要提炼、报告渲染脚本
- `assets/templates/`: 内置模板
- `references/`: 模板占位符与去噪规则说明
- `tests/`: 回归测试

## Common Commands

生成单仓库本周周报：

```powershell
python scripts/run_report.py --period weekly --workspace D:\your\repo --output weekly_report.md
```

生成多仓库按天周报并导出表格：

```powershell
python scripts/run_report.py `
  --period weekly `
  --style repo-daily `
  --workspace D:\your\repos `
  --output weekly_report.md `
  --table-output-csv weekly_table.csv `
  --raw-output weekly_raw.json
```

## Outputs

- `report.md`: 汇报正文
- `*.csv`: 按仓库按天的表格视图
- `*.json`: 原始提交、摘要结果和聚合结果

## Notes

- 人类阅读入口使用本文件。
- agent 运行时入口使用 `SKILL.md`。
