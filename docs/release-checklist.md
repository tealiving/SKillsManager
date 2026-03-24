# Release Checklist

## 发布前检查

- `skills/` 目录中的新增或变更内容已检查
- `catalog/skills.json` 已同步更新
- `README.md` 的 Skills Index 已同步更新
- `docs/usage/install.md` 已覆盖最新安装方式
- `docs/usage/publish.md` 已覆盖最新发布方式

## 验证检查

- 执行 `npm run verify:release`
- 至少选择一个普通 skill 做安装验证
- 如涉及嵌套 skill，额外验证对应 skill 的模板或脚本资源

## 打包检查

- 执行 `npm run pack:dry-run`
- 确认 `bin/` 已打包
- 确认 `lib/` 已打包
- 确认 `skills/` 已打包
- 确认 `catalog/skills.json` 已打包
- 确认 `scripts/` 已打包
- 确认 `tests/` 与 `docs/plans/` 未被误打包

## 发布检查

- 最终包名已确认
- `package.json` 中的 `"private"` 设置已确认
- 内网 npm registry 地址已确认
- Gitee 流水线或本地发布账号可用

## 发布后检查

- 用 `npx` 在干净环境安装一个 skill
- 验证安装路径正确
- 验证 Codex 重启后可识别 skill
- 在内网文档或 Wiki 同步最新安装命令
