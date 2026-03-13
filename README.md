# SKillsManager

用于集中管理多个 Codex skill 项目。

## What This Repo Stores

- `skills/`: 各个独立 skill 的完整目录

## Skills Index

| Skill | 目录 | 主要功能 | 典型输出 | 人类入口 | Agent 入口 |
|---|---|---|---|---|---|
| `git-report-summarizer` | `skills/git-report-summarizer/` | 汇总多个 Git 仓库提交，提炼日报/周报/月报，支持多仓库按天明细、表格和 JSON 数据 | `Markdown`、`CSV`、`JSON` | `README.md` | `SKILL.md` |

## Suggested README Pattern

父层 `README.md` 建议只承担“索引页”职责：

- 说明这个仓库是做什么的
- 用表格列出所有 skill 的目录和功能
- 提供每个 skill 的人类入口和 agent 入口
- 约定新增 skill 时同步更新本表

子目录建议分工如下：

- `README.md`：给人看，说明用途、目录结构、常用命令、输出物
- `SKILL.md`：给 agent 用，描述触发条件和执行工作流

## Maintenance Rule

新增或删除 skill 时，同时更新本页的 `Skills Index` 表格。
