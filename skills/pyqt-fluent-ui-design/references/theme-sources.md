# 外部样式源配置与下载策略

## 目标
- 为 PyQt/PySide 项目提供可控的样式源引入方式。
- 默认“手动触发下载”，禁止隐式在线拉取。
- 通过固定版本与哈希校验保证可复现。

## 配置文件
- 路径：`references/theme_sources.json`
- 每个源至少包含：
  - `name`：唯一标识
  - `url`：压缩包下载地址（建议 codeload + commit/tag）
  - `version`：人类可读版本标识
  - `sha256`：下载包校验值
  - `license`：许可证标识

## 使用方式
```bash
python scripts/fetch_theme_assets.py --list
python scripts/fetch_theme_assets.py --provider pyqt-fluent-widgets
python scripts/fetch_theme_assets.py --provider qt-material --dry-run
python scripts/fetch_theme_assets.py --provider pyqt-fluent-widgets --allow-license GPL-3.0
```

## 约束策略
- `--all` 只在一次性初始化或镜像同步时使用。
- 默认开启 SHA256 校验；仅临时排障才使用 `--skip-checksum`。
- 下载目录建议纳入缓存目录，不直接混入业务源码。
- 默认屏蔽 GPL/AGPL/LGPL；确需下载时使用 `--allow-copyleft` 或 `--allow-license`。
- 可通过 `--block-license` 添加额外限制，例如 `--block-license MIT`。

## 许可证提示
- `GPL-3.0`：闭源分发时风险较高，先做法务评估。
- `MIT/BSD`：通常更宽松，但仍需保留版权声明。
