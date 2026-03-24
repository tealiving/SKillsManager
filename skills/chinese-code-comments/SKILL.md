---
name: chinese-code-comments
description: "Require concise Chinese comments and reST-style docstrings for all functions. Use when user requests Chinese annotations or the project standard is Chinese comments/docstrings."
---

# 中文注释与 Docstring 规范

## 概述
在编写/修改代码时补充简洁中文注释，并为所有函数提供 reST 风格 docstring。

## 必须规则
- 所有函数必须写 docstring（包括私有/内部函数）。
- docstring 使用 reST 格式：`:param` / `:return`。
- docstring 以中文为主，描述意图与输入输出。
- 有返回值的函数必须写 `:return:`；无返回值则写 `:return: None`。
- 参数为可选或关键字参数时也要写 `:param`，名称保持一致。

## 注释原则
- 仅在复杂或易误解处添加中文注释，避免复述实现细节。
- 优先说明“意图/约束/为什么”，保持简短。
- 保留既有英文注释，除非用户要求翻译。
- 新增模块或文件时，可添加一句中文模块级说明。

## 简短示例
```python
def build_index(paths: list[str], *, strict: bool = False) -> dict[str, int]:
    """构建索引映射。

    :param paths: 输入路径列表
    :param strict: 是否严格校验
    :return: 索引字典
    """
    ...
```