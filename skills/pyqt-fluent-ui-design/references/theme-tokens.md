# 主题 Token 规范

## 命名原则
- 使用语义命名（text_primary、bg_card），不要直接使用色值
- 所有主题提供同一套 token 名称

## 建议 Token 分类
### 颜色（语义）
- text_primary, text_secondary, text_muted
- bg_base, bg_card, bg_surface
- border_default, border_strong
- accent_primary, accent_hover, accent_pressed
- success, warning, error, info

### 排版
- font_family_base
- font_size_xs, font_size_s, font_size_m, font_size_l, font_size_xl
- font_weight_regular, font_weight_medium, font_weight_bold
- line_height_s, line_height_m, line_height_l

### 间距
- space_2, space_4, space_8, space_12, space_16, space_24, space_32

### 圆角
- radius_s, radius_m, radius_l, radius_xl

### 阴影/层级
- elevation_1, elevation_2, elevation_3

## 实施要点
- 组件只读取 token，不读取主题色值
- token 变更应自动覆盖全局样式输出