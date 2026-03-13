---
name: git-report-summarizer
description: 汇总当前 git 身份在多个仓库中的提交并生成日报、周报、月报。用于用户提出“根据 commit 生成汇报”“按模板输出工作日志”“统计某时间窗口 git 提交”这类请求，支持本地仓库扫描与可选 GitHub/Gitee API 补充。
---

# Git Report Summarizer

## Overview

根据当前 `git config user.name/user.email` 自动收集提交记录，过滤噪声提交后生成结构化工作汇报。优先走本地仓库 `git log`，可选启用 GitHub/Gitee API 发现远程仓库并补充提交。

## Quick Start

1. 进入技能目录后执行：

```powershell
python scripts/run_report.py --period daily --workspace D:\code --output report.md
```

2. 查看输出文件：
- `report.md`：最终汇报
- `raw_commits.json`：结构化原始数据（便于审计和二次加工）

## Workflow

1. 读取 git 身份：优先仓库级配置，失败回退全局配置。
2. 发现仓库：合并 `--repos` 显式列表与 `--workspace` 扫描结果。
3. 收集提交：按时间窗口并发执行本地 `git log`，可选调用 GitHub/Gitee API。
4. 去噪与聚合：过滤 merge/wip/chore 等噪声，按仓库聚合为汇报事项。
5. 模板渲染：优先用户模板；未提供时使用 `assets/templates/*.md.j2`。
6. 输出结果：写入 Markdown 报告与 JSON 明细。

## Command Options

- `--period`: `daily|weekly|monthly|custom`
- `--base-date`: 基准日期（`YYYY-MM-DD`）
- `--since --until`: 自定义时间窗口（用于 `custom`）
- `--workspace`: 本地仓库扫描目录
- `--repos`: 显式仓库路径列表
- `--platform`: `local|github|gitee|both`
- `--enable-remote-discovery`: 开启远程仓库发现与提交补充
- `--github-user --gitee-user`: 平台用户名（默认回退 git 用户名）
- `--github-token --gitee-token`: 平台 token（默认读取环境变量）
- `--style`: `concise|management|technical|repo-daily`
- `--template`: 用户自定义模板路径
- `--output --raw-output`: 输出文件路径
- `--table-output-csv`: 按仓库按天导出 CSV 表格
- `--max-workers`: 本地仓库并发采集线程数

## Examples

日报：

```powershell
python scripts/run_report.py --period daily --workspace D:\dev\repos
```

周报（指定上周窗口）：

```powershell
python scripts/run_report.py --period custom --since 2026-03-02 --until 2026-03-09 --workspace D:\dev\repos
```

月报（自定义模板）：

```powershell
python scripts/run_report.py --period monthly --workspace D:\dev\repos --template .\my_template.md
```

周报（管理汇报版）：

```powershell
python scripts/run_report.py --period weekly --workspace D:\dev\repos --style management
```

周报（多仓库按天明细 + 表格）：

```powershell
python scripts/run_report.py `
  --period weekly `
  --workspace D:\dev\repos `
  --style repo-daily `
  --table-output-csv .\weekly_table.csv
```

GitHub + Gitee 远程补充：

```powershell
python scripts/run_report.py `
  --period weekly `
  --workspace D:\dev\repos `
  --platform both `
  --enable-remote-discovery `
  --github-user your_github_user `
  --gitee-user your_gitee_user
```

## Resource Map

- `scripts/run_report.py`: 入口脚本，负责编排采集、渲染、输出。
- `scripts/report_core.py`: 时间窗口、去噪、聚合、渲染核心逻辑。
- `references/template_spec.md`: 模板占位符与最小示例。
- `references/commit_noise_rules.md`: 提交去噪规则说明。
- `assets/templates/*.md.j2`: 简洁版、管理版、技术版、仓库按天版模板。

## Notes

1. 若用户提供模板，优先使用用户模板。
2. 远程 API 受权限与限流影响，失败时不阻塞本地汇报输出。
3. 结果中会附带失败仓库列表，方便后续补采。
