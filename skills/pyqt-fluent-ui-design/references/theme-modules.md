# 主题模块与注册策略

## 目录建议
- themes/
  - __init__.py
  - registry.py
  - light.py
  - dark.py
  - types.py

## 模块职责
- light.py/dark.py：只返回 token 字典
- types.py：定义 token 结构（TypedDict 或 dataclass）
- registry.py：注册主题、切换主题、生成全局样式

## 伪代码骨架
```python
# types.py
from typing import TypedDict

class ThemeTokens(TypedDict):
    text_primary: str
    bg_base: str
    accent_primary: str
    # ...

# light.py
from .types import ThemeTokens

def build_tokens() -> ThemeTokens:
    return {
        "text_primary": "#111111",
        "bg_base": "#FFFFFF",
        "accent_primary": "#0F6CBD",
    }

# registry.py
from . import light, dark

THEMES = {
    "light": light.build_tokens,
    "dark": dark.build_tokens,
}

def get_tokens(theme_name: str) -> dict:
    return THEMES[theme_name]()

# apply_theme 应用到 QSS/QPalette/库主题 API
```

## 要点
- 新增主题时：新增模块 + 注册
- 组件逻辑不感知主题，仅消费 token
- 若需要调用库主题 API，集中在 registry 里处理