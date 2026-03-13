# 提交去噪规则

当前版本默认过滤以下提交：

1. 合并提交（`is_merge=True` 或提交信息以 `merge` 开头）
2. 噪声关键词精确匹配：`wip`、`merge`、`format`、`typo`、`test`、`chore`
3. 提交信息前缀匹配：`merge `、`wip `

## 调整建议

- 如果团队约定中 `test` 也算有效工作，可在 `scripts/report_core.py` 的 `NOISE_KEYWORDS` 中移除该项。
- 如果想保留部分 merge（例如 squash merge），可以在 `is_noise_commit` 增加白名单规则。
