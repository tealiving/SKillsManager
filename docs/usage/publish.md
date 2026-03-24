# Skills 发布说明

## 目标

本仓库的推荐分发模型是：

- `Gitee` 作为源码、审计和版本事实源
- `npm/npx` 作为普通用户默认安装入口
- 仓库脚本作为排障和源码调试兜底

## 发布前提

在真正发布到内网 npm 之前，需要确认以下信息：

- 最终包名
- 内网 npm registry 地址
- 发布账号或 CI 凭证
- 是否移除 `package.json` 中的 `"private": true`

当前仓库中的包名 `@your-org/codex-skills` 只是占位名。

## 推荐发布流程

### 1. 源码整理

确认以下内容已经同步：

- `skills/<skill-name>/` 目录内容
- `catalog/skills.json`
- `README.md`
- `docs/usage/install.md`

### 2. 本地验证

在仓库根目录执行：

```bash
npm run verify:release
```

必要时再做安装烟雾验证：

```bash
node ./bin/codex-skills.mjs install git-report-summarizer --repo-root . --codex-home <temp-dir>
```

### 3. 打包预检查

在发布前建议先执行：

```bash
npm run pack:dry-run
```

重点确认：

- `bin/`
- `lib/`
- `skills/`
- `catalog/skills.json`
- `scripts/`

都已进入包内容。

当前包内容由 `package.json` 中的 `files` 白名单控制，默认不会把 `tests/` 与 `docs/plans/` 这类非运行时内容带入发布包。

### 4. 发布到内网 npm

在确认包名和 registry 后，再执行类似流程：

```bash
npm publish --registry <your-internal-registry>
```

如果你们走 CI/CD，则建议将发布动作交给 Gitee 流水线。

## Gitee 仓库职责

Gitee 仓库中建议保留：

- 全量 `skills/` 目录
- `catalog/skills.json`
- CLI 入口和脚本
- 安装与发布文档

这样用户既可以：

- 通过 `npx` 安装正式版本
- 也可以在紧急情况下直接 clone 仓库并执行 `scripts/install-skill.*`

## 关于 `.system` 与嵌套 skill

当前仓库已经完成以下归一化：

- `.system` 被拆分为：
  - `openai-docs`
  - `skill-creator`
  - `skill-installer`
- `planning-with-files` 采用 Codex 对应的 skill 根目录，而不是整包多平台目录

这意味着发布给用户的是“最终可安装目录”，而不是来源仓的原始聚合结构。

## 关于 `superpowers` 聚合目录

当前没有直接发布 `C:\Users\tealiving\.codex\skills\superpowers` 这个聚合目录，原因是：

- 它与 `C:\Users\tealiving\.codex\superpowers\skills\*` 中逐个 skill 的内容重复
- 当前仓库已经导入后者
- 继续保留聚合目录会增加重复和维护成本

## 建议的内网用户文案

推荐在内网文档或 Wiki 中直接提供：

```bash
npx @your-org/codex-skills list
npx @your-org/codex-skills install <skill-name>
```

并补充：

- 默认安装到 `%USERPROFILE%\.codex\skills`
- 如设置了 `CODEX_HOME`，则安装到 `$CODEX_HOME/skills`
- 安装完成后请重启 Codex
- 如 `npx` 不可用，可使用仓库中的 PowerShell/Bash 安装脚本
