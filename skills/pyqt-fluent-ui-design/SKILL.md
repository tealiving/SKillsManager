---
name: pyqt-fluent-ui-design
description: "Design PyQt-Fluent-Widgets UIs with a consistent visual system and modular theming. Use for UI layout/styling tasks, Light/Dark theme design, and extensible theme architecture that avoids per-widget configuration by centralizing tokens, styles, and theme modules."
---

# PyQt-Fluent-Widgets UI 设计与主题体系

## 快速使用
- 澄清界面范围、核心场景、平台约束与品牌风格
- 统一 token 与主题注册，避免在控件里硬编码
- 需要细节时读取 references/ 下的说明

## 交付目标
- 输出主题模块骨架与注册点
- 输出 token 列表与映射规则
- 输出组件级样式策略（按模块/页面统一处理）

## 工作流
1. 盘点已有 UI/主题入口（搜索 qfluentwidgets、setStyleSheet、theme 等）
2. 定义 token schema（语义色/排版/间距/圆角/阴影/动效）
3. 为每个主题建立独立模块并实现同一接口
4. 建立 ThemeRegistry/ThemeManager 并广播主题变更
5. 用模块化样式生成器批量应用，避免逐控件配置
6. 仅在少数例外场景做局部 override，并记录原因

## 外部样式源（可选）
- 默认不自动下载第三方样式资源，避免不可控升级
- 默认屏蔽 GPL/AGPL/LGPL 资源下载，避免误触许可证风险
- 需要引入开源样式时，先读取 `references/theme-sources.md`
- 样式源配置放在 `references/theme_sources.json`
- 下载脚本为 `scripts/fetch_theme_assets.py`
- 必须固定版本（tag/commit）+ 校验 SHA256，再进入项目
- 如确需放行，可使用 `--allow-copyleft` 或 `--allow-license GPL-3.0`
- 引用前确认许可证兼容（例如 GPL 对闭源分发有约束）

## 变体处理
- 新增主题时：只新增模块 + 注册，不修改组件样式逻辑
- 需要品牌化时：优先调整 token 与少量映射规则
- 使用第三方样式时：先下载到本地缓存，再做 token 映射，不直接在线引用

## 参考
- references/workflow.md
- references/theme-tokens.md
- references/theme-modules.md
- references/component-guidelines.md
- references/theme-sources.md
