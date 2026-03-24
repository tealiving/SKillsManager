# SKillsManager

用于集中管理、归档与分发多个 Codex skills。

## What This Repo Stores

- `skills/`: 各个独立 skill 的完整目录
- `catalog/skills.json`: 可分发 skills 清单与安装元数据
- `docs/plans/`: 迁移、分发、实施计划文档

## Distribution Model

本仓库同时承担两个角色：

- 源码仓库：维护每个 skill 的目录、模板、脚本和文档
- 分发仓库：为后续内网 Gitee 与 npm/npx 安装入口提供统一目录和 manifest

推荐的用户安装方式会是：

```bash
npx @your-org/codex-skills list
npx @your-org/codex-skills install <skill-name>
```

在 npm 入口未就绪前，可继续通过仓库脚本或手工复制目录安装到 `%USERPROFILE%\\.codex\\skills`。

更多说明见：

- `docs/usage/install.md`
- `docs/usage/publish.md`
- `docs/release-checklist.md`

## Skills Index

当前仓库已导入 35 个可直接安装的 skills。

| Skill | 技能简介 | 目录 | 来源 | 人类入口 | Agent 入口 | 分发状态 |
|---|---|---|---|---|---|---|
| `architecture-review-checklist` | 架构评审与分层合规检查 | `skills/architecture-review-checklist/` | `codex` | `-` | `SKILL.md` | `installable` |
| `better-auth-best-practices` | Better Auth 集成最佳实践 | `skills/better-auth-best-practices/` | `agents` | `-` | `SKILL.md` | `installable` |
| `brainstorming` | 创意需求澄清与方案探索 | `skills/brainstorming/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `chinese-code-comments` | 中文注释与 reST 文档规范 | `skills/chinese-code-comments/` | `codex` | `-` | `SKILL.md` | `installable` |
| `dispatching-parallel-agents` | 并行拆分多代理任务 | `skills/dispatching-parallel-agents/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `enterprise-layered-architecture` | 企业分层架构设计约束 | `skills/enterprise-layered-architecture/` | `codex` | `-` | `SKILL.md` | `installable` |
| `executing-plans` | 按计划分阶段执行实现 | `skills/executing-plans/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `figma` | Figma 设计上下文转代码 | `skills/figma/` | `codex` | `-` | `SKILL.md` | `installable` |
| `find-skills` | 发现并安装合适 skills | `skills/find-skills/` | `agents` | `-` | `SKILL.md` | `installable` |
| `finishing-a-development-branch` | 开发分支收尾与集成 | `skills/finishing-a-development-branch/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `frontend-design` | 高质量前端界面设计 | `skills/frontend-design/` | `agents` | `-` | `SKILL.md` | `installable` |
| `git-report-summarizer` | Git 提交日报周报月报生成 | `skills/git-report-summarizer/` | `codex` | `README.md` | `SKILL.md` | `installable` |
| `openai-docs` | OpenAI 官方文档检索与选型 | `skills/openai-docs/` | `codex-system` | `-` | `SKILL.md` | `installable` |
| `planning-with-files` | 文件化复杂任务规划与跟踪 | `skills/planning-with-files/` | `codex-nested` | `-` | `SKILL.md` | `installable` |
| `pdf` | PDF 读写审阅与渲染检查 | `skills/pdf/` | `codex` | `-` | `SKILL.md` | `installable` |
| `ppt-agent-llm-orchestration` | 多代理 PPT 编排生成 | `skills/ppt-agent-llm-orchestration/` | `codex` | `-` | `SKILL.md` | `installable` |
| `pptx` | PPTX 读取编辑与处理 | `skills/pptx/` | `codex` | `-` | `SKILL.md` | `installable` |
| `pptx-generator` | PPT 模板生成与渲染 | `skills/pptx-generator/` | `codex` | `-` | `SKILL.md` | `installable` |
| `pyqt-fluent-ui-design` | PyQt Fluent UI 主题与布局 | `skills/pyqt-fluent-ui-design/` | `codex` | `-` | `SKILL.md` | `installable` |
| `python-enterprise-development` | Python 企业级分层开发 | `skills/python-enterprise-development/` | `codex` | `-` | `SKILL.md` | `installable` |
| `python-project-structure` | Python 项目结构与 API 规划 | `skills/python-project-structure/` | `agents` | `-` | `SKILL.md` | `installable` |
| `receiving-code-review` | 消化并验证评审意见 | `skills/receiving-code-review/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `requesting-code-review` | 发起代码评审前检查 | `skills/requesting-code-review/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `skill-creator` | 创建或升级 skill 模板 | `skills/skill-creator/` | `codex-system` | `-` | `SKILL.md` | `installable` |
| `skill-installer` | 从仓库安装 Codex skills | `skills/skill-installer/` | `codex-system` | `-` | `SKILL.md` | `installable` |
| `subagent-driven-development` | 子代理驱动的分工开发 | `skills/subagent-driven-development/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `systematic-debugging` | 系统化定位和修复问题 | `skills/systematic-debugging/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `test-driven-development` | TDD 驱动实现与回归验证 | `skills/test-driven-development/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `ui-ux-pro-max` | UI/UX 方案设计与优化 | `skills/ui-ux-pro-max/` | `agents` | `-` | `SKILL.md` | `installable` |
| `using-git-worktrees` | 用 git worktree 隔离开发 | `skills/using-git-worktrees/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `using-superpowers` | 启用并规范使用 superpowers | `skills/using-superpowers/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `verification-before-completion` | 完成前强制验证结果 | `skills/verification-before-completion/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `writing-plans` | 多步骤实施计划编写 | `skills/writing-plans/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `writing-skills` | skill 编写与验证规范 | `skills/writing-skills/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `xlsx` | 表格文件处理与生成 | `skills/xlsx/` | `agents` | `-` | `SKILL.md` | `installable` |

## Planned Catalog Governance

- 所有可安装 skill 统一落在 `skills/<skill-name>/`
- 只有实际存在于仓库中的 skill 才进入 `catalog/skills.json`
- 本地来源盘点、去重和待导入项记录在 `docs/plans/2026-03-24-skill-import-checklist.md`
- 新增或删除 skill 时，同时更新本页的 `Skills Index` 和 `catalog/skills.json`
- `C:\Users\tealiving\.codex\skills\superpowers` 聚合目录当前不再单独导入，因为其内容已由 `C:\Users\tealiving\.codex\superpowers\skills\*` 显式目录覆盖

## Suggested README Pattern

父层 `README.md` 建议承担“索引页 + 分发入口”职责：

- 说明仓库用途
- 用表格列出所有 skill 的目录和功能
- 提供人类入口与 agent 入口
- 说明默认安装命令和安装目录
- 约定新增 skill 时同步更新索引与 manifest

子目录建议分工如下：

- `README.md`：给人看，说明用途、目录结构、常用命令、输出物
- `SKILL.md`：给 agent 用，描述触发条件和执行工作流

## Maintenance Rule

新增或删除 skill 时，同时更新本页的 `Skills Index` 表格（含技能简介）和 `catalog/skills.json`。
