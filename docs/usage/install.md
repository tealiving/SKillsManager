# Skills 安装说明

## 适用场景

本文档面向内网用户，说明如何把本仓库中的 skills 安装到本地 Codex。

默认安装目录：

- Windows: `%USERPROFILE%\.codex\skills`
- 自定义: `$CODEX_HOME/skills`

安装完成后通常需要重启 Codex。

## 推荐方式：npx

当内网 npm 包可用后，推荐优先使用：

```bash
npx @your-org/codex-skills list
npx @your-org/codex-skills install <skill-name>
```

示例：

```bash
npx @your-org/codex-skills install git-report-summarizer
npx @your-org/codex-skills install planning-with-files
```

预期结果：

- skill 被复制到本地 `~/.codex/skills/<skill-name>`
- 控制台输出实际安装路径
- 控制台提示重启 Codex

## 从源码仓库安装

如果 npm 包尚未发布，或者需要调试当前仓库内容，可直接在仓库根目录执行。

### PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skill.ps1 -Name git-report-summarizer
```

自定义安装目录：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skill.ps1 `
  -Name planning-with-files `
  -CodexHome D:\temp\codex-home
```

### Bash

```bash
bash ./scripts/install-skill.sh git-report-summarizer
```

自定义安装目录：

```bash
bash ./scripts/install-skill.sh planning-with-files --codex-home /tmp/codex-home
```

## 常用命令

列出仓库中可安装的 skills：

```bash
node ./bin/codex-skills.mjs list --repo-root .
```

安装 skill：

```bash
node ./bin/codex-skills.mjs install brainstorming --repo-root .
```

校验 skill 目录：

```bash
node ./bin/codex-skills.mjs validate planning-with-files --repo-root .
```

## 已验证的安装方式

当前仓库已做本地验证：

- `node ./bin/codex-skills.mjs install brainstorming --repo-root . --codex-home <temp-dir>`
- `powershell -ExecutionPolicy Bypass -File .\scripts\install-skill.ps1 -Name git-report-summarizer -CodexHome <temp-dir>`
- `bash ./scripts/install-skill.sh git-report-summarizer --codex-home <temp-dir>`
- `node ./bin/codex-skills.mjs install planning-with-files --repo-root . --codex-home <temp-dir>`

## 常见问题

### 1. 安装成功但 Codex 看不到 skill

通常需要重启 Codex 才会重新扫描 skill 目录。

### 2. 目标目录已存在

当前安装器默认拒绝覆盖同名 skill，避免误覆盖已有本地版本。

### 3. Bash 环境找不到 `node`

当前 Bash 脚本会优先尝试 `node`，在 Windows 的 bash 环境下会回退到 `node.exe`。

### 4. 哪些目录没有被直接导入

`C:\Users\tealiving\.codex\skills\superpowers` 这个聚合目录没有整包导入，因为其内容已经由更明确的 `C:\Users\tealiving\.codex\superpowers\skills\*` 目录逐个导入。
