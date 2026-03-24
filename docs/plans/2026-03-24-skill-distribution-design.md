# 内网 Skill 分发设计

## 背景

当前仓库用于集中管理多个 Codex skill。后续目标是将本地已有 skills 归档到统一仓库，迁移到内网 Gitee，并让普通用户能够在本地低成本安装、更新和卸载这些 skills。

用户侧已经具备内网 npm 镜像能力，因此分发方案不必局限于“给一个仓库地址然后让用户手工复制目录”。更合适的目标是：

- `Gitee` 作为源码与审计的唯一事实源
- `npm/npx` 作为普通用户默认安装入口
- `PowerShell/Bash` 脚本作为离线或排障兜底入口

## 目标

- 让用户通过一条命令安装指定 skill
- 让仓库能够承载多个 skills 的版本化管理与内网迁移
- 让 skill 目录结构对 Codex 运行时保持兼容
- 为后续新增、下架、升级 skill 提供统一 manifest 和发布流程

## 非目标

- 当前阶段不做技能依赖自动解析
- 当前阶段不做跨终端的配置同步
- 当前阶段不做远程在线 marketplace UI

## Architecture Brief

### Layer Mapping

- Presentation
  - `npx @org/codex-skills ...`
  - `scripts/install-skill.ps1`
  - `scripts/install-skill.sh`
  - 面向用户的 `README.md`
- Application
  - `list/install/update/remove/validate` 用例编排
  - manifest 读取、参数校验、安装流程控制
- Domain
  - `SkillManifest`
  - `SkillPackage`
  - `InstallRequest`
  - `InstallResult`
- Infrastructure
  - Gitee 仓库读取
  - npm 包内容读取
  - 本地文件系统复制与原子替换
  - 临时目录、压缩包、哈希校验

### Dependency Direction

- 允许：`Presentation -> Application -> Domain`
- 允许：`Application -> Infrastructure abstraction`
- 禁止：领域模型直接依赖 Gitee、npm、PowerShell 或具体文件系统命令

### Data Contract Changes

新增统一目录索引文件，例如 `catalog/skills.json`，记录每个 skill 的安装元数据。建议字段：

```json
{
  "schemaVersion": 1,
  "skills": [
    {
      "name": "git-report-summarizer",
      "title": "Git Report Summarizer",
      "version": "0.1.0",
      "path": "skills/git-report-summarizer",
      "installable": true,
      "channel": "stable",
      "origin": "local-import",
      "tags": ["git", "report", "summary"]
    }
  ]
}
```

### Error Strategy

- 安装前校验 skill 目录必须存在 `SKILL.md`
- 安装过程先写入临时目录，成功后再原子替换目标目录
- 已存在目标目录时，默认拒绝覆盖；显式传 `--force` 才允许更新
- manifest 缺失、目录非法、路径越界时立即失败
- npm 安装入口失败时，提示使用 PowerShell/Bash 脚本兜底

### Test Strategy

- manifest 结构校验测试
- 安装流程单元测试
- 使用临时 `CODEX_HOME` 的集成测试
- Windows PowerShell 与 Linux/macOS Shell 的脚本烟雾测试

## 方案对比

### 方案 A：只提供 Gitee 下载 URL

用户流程：

1. 打开仓库
2. 下载 zip 或 clone
3. 手工找到 skill 目录
4. 复制到 `~/.codex/skills/<skill-name>`

优点：

- 实现最简单
- 不需要额外 CLI

缺点：

- 普通用户容易放错目录
- 不容易做版本控制与批量更新
- 用户体验差，排障成本高

### 方案 B：Gitee 仓库 + 安装脚本

用户流程：

1. clone 或下载仓库
2. 执行 `install-skill.ps1` 或 `install-skill.sh`

优点：

- 比手工复制稳定
- 实现复杂度可控
- 适合管理员批量分发

缺点：

- 对普通用户仍然偏重
- 仍然依赖用户先拿到仓库内容

### 方案 C：Gitee 作为事实源 + npm/npx 作为默认入口 + 脚本兜底

用户流程：

1. 执行 `npx @your-org/codex-skills list`
2. 执行 `npx @your-org/codex-skills install git-report-summarizer`
3. 如需排障，再使用仓库脚本

优点：

- 用户入口最轻
- 版本与发布节奏可控
- 适合内网规模化分发
- 可保留 Gitee 作为源码和审计来源

缺点：

- 需要一个小型 CLI 包
- 需要一次性建立发布流程

结论：推荐方案 C。

## 推荐目标架构

### 仓库角色

- `Gitee 仓库`
  - 作为 skills 源码、模板、脚本、测试与文档的唯一事实源
  - 供研发维护、审计、回滚与内网镜像
- `npm 包 @your-org/codex-skills`
  - 作为用户安装入口
  - 内含 manifest、安装器与随包发布的 skills 快照
- `本地 Codex skills 目录`
  - 作为最终运行态目录
  - 默认路径为 `%USERPROFILE%\\.codex\\skills` 或 `$CODEX_HOME/skills`

### 仓库目录建议

```text
SKillsManager/
  skills/
    git-report-summarizer/
    python-enterprise-development/
    ...
  catalog/
    skills.json
  bin/
    codex-skills.mjs
  lib/
    manifest.mjs
    install.mjs
    fs-utils.mjs
    validate.mjs
  scripts/
    install-skill.ps1
    install-skill.sh
  docs/
    plans/
  README.md
  package.json
```

说明：

- 推荐所有“可安装 skill”统一落在 `skills/<skill-name>`，不要再为来源做多层嵌套
- 来源、渠道、来源仓库等信息放进 `catalog/skills.json`
- 像 `planning-with-files` 这类多平台仓，需要先抽取出实际可安装的 Codex 子目录，再归一化发布

## 用户安装模型

### 默认安装命令

```bash
npx @your-org/codex-skills list
npx @your-org/codex-skills install git-report-summarizer
```

建议 CLI 子命令：

- `list`
- `install <name>`
- `install --all`
- `update <name>`
- `remove <name>`
- `validate <name>`
- `where <name>`

### 典型安装流程

1. CLI 读取内置 `catalog/skills.json`
2. 校验目标 skill 是否存在且 `installable=true`
3. 将 skill 复制到临时目录
4. 校验 `SKILL.md` 与相对资源是否完整
5. 复制到 `$CODEX_HOME/skills/<skill-name>`
6. 输出结果并提示用户重启 Codex

### 兜底脚本

PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skill.ps1 -Name git-report-summarizer
```

Shell：

```bash
bash ./scripts/install-skill.sh git-report-summarizer
```

适用场景：

- `npx` 不可用
- npm 包尚未发布
- 需要从源码仓库调试安装

## 安装行为约束

- 默认不覆盖同名 skill
- `--force` 时先备份旧目录，再替换新目录
- 所有路径必须做越界校验，禁止复制到 `skills` 目录外
- 安装完成后输出实际安装路径
- 安装器必须尊重 `CODEX_HOME`

## 技能清单治理

建议每个 skill 在 manifest 中补充以下元信息：

- `name`
- `title`
- `version`
- `path`
- `installable`
- `channel`
- `origin`
- `tags`
- `requiresRestart`
- `notes`

这样后续可以支持：

- 按标签列出 skills
- 区分 `stable` 与 `experimental`
- 区分“可分发”和“仅内部使用”
- 在安装结果里给出风险提示

## 发布流程建议

### 源码发布

1. 研发修改 Gitee 仓库中的 `skills/`
2. 同步更新 `catalog/skills.json`
3. 执行校验脚本与测试
4. 合并到主分支

### 包发布

1. 从主分支或 release tag 构建 npm 包
2. 发布到内网 npm 镜像
3. 用户通过 `npx` 拉取最新版本

## 风险点与应对

### 风险 1：导入目录不规范

本地 skill 来源可能存在多种布局，例如：

- 普通 skill：根目录直接有 `SKILL.md`
- 聚合仓：真实 skill 位于嵌套子目录
- 多平台仓：包含多个 agent 平台适配目录

应对：

- 导入阶段先做归一化，不合格目录不直接发布
- 用 manifest 只登记“最终可安装目录”

### 风险 2：用户本地已有旧版本

应对：

- 提供 `update` 与 `--force`
- 安装前自动备份原目录到 `.backup/<timestamp>-<name>`

### 风险 3：技能包含外部依赖

例如依赖 MCP、联网、外部账号或本地工具。

应对：

- 在 manifest 中增加 `notes` 或 `requirements`
- `validate` 命令提前给出环境提示

## 推荐的用户说明文案

面向普通用户，README 建议优先给这两条：

```bash
npx @your-org/codex-skills list
npx @your-org/codex-skills install <skill-name>
```

然后再补充：

- 默认安装到 `%USERPROFILE%\\.codex\\skills`
- 如果设置了 `CODEX_HOME`，则安装到 `$CODEX_HOME/skills`
- 安装后请重启 Codex
- 如 `npx` 不可用，可执行仓库中的安装脚本

## 最小可行落地顺序

1. 先把现有本地 skills 归一化到 `skills/<skill-name>`
2. 增加 `catalog/skills.json`
3. 先实现 `list/install/validate`
4. 再补 `update/remove`
5. 最后接入内网 npm 发布流程

## 结论

对于你的场景，最合适的落地方式不是“只给下载 URL”，也不是“只给 Gitee 地址让用户自己复制目录”，而是：

- `Gitee` 负责存源码、版本和审计
- `npx` 负责普通用户的安装体验
- 仓库脚本负责兜底与排障

这样既适合你后续迁移到内网 Gitee，也能让用户在本地安装 skills 的成本降到最低。
