# Skill Distribution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 SKillsManager 增加一套可在内网 Gitee 与 npm 镜像中发布的 skill 分发能力，让用户可以通过 `npx` 或脚本把 skill 安装到本地 Codex。

**Architecture:** 以 Gitee 仓库作为技能源码与审计事实源，在仓库内新增统一 manifest 与 Node CLI。CLI 负责 `list/install/update/remove/validate` 等用例，脚本负责 PowerShell/Bash 兜底安装，最终安装目标为 `$CODEX_HOME/skills/<skill-name>`。

**Tech Stack:** Markdown、JSON manifest、Node.js ESM CLI、PowerShell、Bash、Gitee、内网 npm 镜像。

---

### Task 1: 归一化仓库中的 skill 目录

**Files:**
- Modify: `README.md`
- Create: `catalog/skills.json`
- Create: `docs/plans/2026-03-24-skill-import-checklist.md`
- Modify: `skills/<skill-name>/...`

**Step 1: 盘点本地 skill 来源**

确认以下来源目录的可安装 skill：

- `C:\Users\tealiving\.codex\skills`
- `C:\Users\tealiving\.agents\skills`
- `C:\Users\tealiving\.codex\superpowers\skills`

重点识别：

- 根目录直接包含 `SKILL.md` 的普通 skill
- 真实 skill 位于嵌套子目录的聚合仓
- 不适合分发的 `.system` 或内部依赖型 skill

**Step 2: 定义导入准则**

导入时只保留最终可安装目录，目录必须满足：

- 包含 `SKILL.md`
- 资源路径在 skill 目录内闭合
- 文件命名和路径安全

**Step 3: 写入导入检查清单**

在 `docs/plans/2026-03-24-skill-import-checklist.md` 中记录：

- 来源
- 导入后目录名
- 是否可安装
- 是否有外部依赖
- 是否需要人工整理

**Step 4: 建立 `catalog/skills.json` 初版**

为每个可安装 skill 写入元信息，至少包含：

```json
{
  "name": "git-report-summarizer",
  "version": "0.1.0",
  "path": "skills/git-report-summarizer",
  "installable": true,
  "channel": "stable"
}
```

**Step 5: 更新 README 的仓库职责说明**

补充“本仓库同时承担 skill 源码管理与分发目录”的说明，并引导用户优先使用后续 CLI。

### Task 2: 实现 manifest 读取与校验模块

**Files:**
- Create: `package.json`
- Create: `bin/codex-skills.mjs`
- Create: `lib/manifest.mjs`
- Create: `lib/validate.mjs`
- Create: `tests/manifest.test.mjs`

**Step 1: 写 manifest 校验的失败测试**

使用 `node:test` 编写：

- 缺失 `skills` 字段时报错
- skill 缺失 `name/path/installable` 字段时报错
- skill 路径越界时报错

**Step 2: 运行测试并确认失败**

Run:

```bash
node --test tests/manifest.test.mjs
```

Expected:

- 失败，提示 manifest loader 尚未实现

**Step 3: 写最小实现**

在 `lib/manifest.mjs` 中实现：

- 读取 `catalog/skills.json`
- 返回内存对象

在 `lib/validate.mjs` 中实现：

- manifest 结构校验
- 路径安全校验

**Step 4: 运行测试并确认通过**

Run:

```bash
node --test tests/manifest.test.mjs
```

Expected:

- 通过

**Step 5: Commit**

```bash
git add package.json bin/codex-skills.mjs lib/manifest.mjs lib/validate.mjs tests/manifest.test.mjs catalog/skills.json
git commit -m "feat: add skill catalog manifest validation"
```

### Task 3: 实现本地安装核心流程

**Files:**
- Create: `lib/install.mjs`
- Create: `lib/fs-utils.mjs`
- Create: `tests/install.test.mjs`

**Step 1: 写安装流程失败测试**

覆盖以下场景：

- 目标 skill 不存在
- `SKILL.md` 缺失
- 目标目录已存在且未传 `--force`
- 自定义 `CODEX_HOME` 时安装路径正确

**Step 2: 运行测试并确认失败**

Run:

```bash
node --test tests/install.test.mjs
```

Expected:

- 失败，提示 install 模块未实现

**Step 3: 写最小实现**

在 `lib/install.mjs` 中实现：

- 查找 manifest
- 解析目标 skill
- 复制到临时目录
- 校验 `SKILL.md`
- 原子安装到 `$CODEX_HOME/skills/<name>`

在 `lib/fs-utils.mjs` 中实现：

- 目录复制
- 临时目录创建
- 原子替换

**Step 4: 运行测试并确认通过**

Run:

```bash
node --test tests/install.test.mjs
```

Expected:

- 通过

**Step 5: Commit**

```bash
git add lib/install.mjs lib/fs-utils.mjs tests/install.test.mjs
git commit -m "feat: add local skill installation flow"
```

### Task 4: 暴露 `npx` CLI 命令

**Files:**
- Modify: `bin/codex-skills.mjs`
- Create: `lib/commands/list.mjs`
- Create: `lib/commands/install.mjs`
- Create: `lib/commands/validate.mjs`
- Create: `tests/cli.test.mjs`

**Step 1: 写 CLI 行为测试**

覆盖以下命令：

- `list`
- `install <name>`
- `validate <name>`

校验输出包含：

- skill 名称
- 安装结果路径
- “请重启 Codex”提示

**Step 2: 运行测试并确认失败**

Run:

```bash
node --test tests/cli.test.mjs
```

Expected:

- 失败，提示子命令尚未接线

**Step 3: 写最小实现**

在 `bin/codex-skills.mjs` 中：

- 解析 `process.argv`
- 分发到 `list/install/validate`

在命令模块中实现：

- `list`: 输出 manifest 中的 installable skills
- `install`: 调用 `lib/install.mjs`
- `validate`: 校验目标 skill 目录结构

**Step 4: 运行测试并确认通过**

Run:

```bash
node --test tests/cli.test.mjs
```

Expected:

- 通过

**Step 5: Commit**

```bash
git add bin/codex-skills.mjs lib/commands tests/cli.test.mjs
git commit -m "feat: add codex skills cli commands"
```

### Task 5: 增加 PowerShell 与 Bash 兜底安装脚本

**Files:**
- Create: `scripts/install-skill.ps1`
- Create: `scripts/install-skill.sh`
- Create: `tests/scripts-smoke.md`

**Step 1: 定义脚本输入输出**

PowerShell 参数建议：

- `-Name`
- `-Force`
- `-CodexHome`

Shell 参数建议：

- `install-skill.sh <name> [--force] [--codex-home PATH]`

**Step 2: 写最小脚本**

脚本职责保持最小：

- 定位仓库根目录
- 校验 `skills/<name>/SKILL.md`
- 复制到目标 `skills` 目录

**Step 3: 手工烟雾测试**

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skill.ps1 -Name git-report-summarizer
```

Linux/macOS:

```bash
bash ./scripts/install-skill.sh git-report-summarizer
```

Expected:

- 安装成功
- 输出目标目录
- 提示重启 Codex

**Step 4: Commit**

```bash
git add scripts/install-skill.ps1 scripts/install-skill.sh tests/scripts-smoke.md
git commit -m "feat: add fallback skill install scripts"
```

### Task 6: 补充用户文档与发布说明

**Files:**
- Modify: `README.md`
- Create: `docs/usage/install.md`
- Create: `docs/usage/publish.md`

**Step 1: 更新 README 首页**

增加以下说明：

- 仓库除了存储 skills，也提供分发能力
- 用户优先用 `npx`
- 管理员可用安装脚本或直接从 Gitee 调试

**Step 2: 写用户安装文档**

至少包含：

- `npx @your-org/codex-skills list`
- `npx @your-org/codex-skills install <name>`
- 安装目录
- 重启提示
- 常见错误与兜底脚本

**Step 3: 写发布文档**

说明：

- Gitee 主分支如何发布 npm 包
- manifest 如何更新
- 新增 skill 的检查项

**Step 4: Commit**

```bash
git add README.md docs/usage/install.md docs/usage/publish.md
git commit -m "docs: add skill distribution usage and publishing guide"
```

### Task 7: 接入内网发布与试点验证

**Files:**
- Create: `gitee-ci.yml` 或对应流水线配置
- Modify: `package.json`
- Create: `docs/release-checklist.md`

**Step 1: 定义发布方式**

选择其一：

- tag 发布
- 手工 release 发布
- 主分支自动发布到测试源，tag 发布到正式源

**Step 2: 增加 npm 发布脚本**

在 `package.json` 增加：

- `test`
- `validate`
- `release:dry-run`
- `release`

**Step 3: 用 2 到 3 个 skill 做试点**

建议试点：

- `git-report-summarizer`
- `python-enterprise-development`
- `frontend-design`

**Step 4: 记录发布与回滚检查清单**

包含：

- manifest 更新
- 安装测试
- npm 发版
- 回滚版本

**Step 5: Commit**

```bash
git add package.json docs/release-checklist.md
git commit -m "chore: add internal release workflow for skills package"
```

Plan complete and saved to `docs/plans/2026-03-24-skill-distribution-implementation.md`. Proceeding with Subagent-Driven execution (this session).
