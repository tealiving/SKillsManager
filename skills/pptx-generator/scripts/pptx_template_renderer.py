#!/usr/bin/env python3
"""基于模板渲染 PPTX 幻灯片。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


TEMPLATE_STYLES = {
    "minimal-business": {
        "bg": RGBColor(250, 250, 252),
        "title": RGBColor(26, 26, 26),
        "body": RGBColor(60, 60, 60),
        "accent": RGBColor(28, 99, 235),
        "font": "Microsoft YaHei UI",
        "font_title": "Microsoft YaHei UI",
        "table_style": "striped",
    },
    "dark-contrast": {
        "bg": RGBColor(18, 22, 33),
        "title": RGBColor(255, 255, 255),
        "body": RGBColor(210, 216, 226),
        "accent": RGBColor(0, 194, 255),
        "font": "Microsoft YaHei UI",
        "font_title": "Microsoft YaHei UI",
        "table_style": "contrast",
    },
    "warm-light": {
        "bg": RGBColor(255, 250, 243),
        "title": RGBColor(50, 43, 40),
        "body": RGBColor(96, 83, 77),
        "accent": RGBColor(230, 126, 34),
        "font": "Microsoft YaHei UI",
        "font_title": "Microsoft YaHei UI",
        "table_style": "soft",
    },
    "tech-neon": {
        "bg": RGBColor(10, 12, 20),
        "title": RGBColor(233, 243, 255),
        "body": RGBColor(167, 184, 204),
        "accent": RGBColor(91, 255, 223),
        "font": "Microsoft YaHei UI",
        "font_title": "Segoe UI Semibold",
        "table_style": "contrast",
    },
    "tech-premium": {
        "bg": RGBColor(8, 12, 24),
        "title": RGBColor(235, 245, 255),
        "body": RGBColor(180, 196, 220),
        "accent": RGBColor(79, 140, 255),
        "font": "Microsoft YaHei UI",
        "font_title": "Segoe UI Semibold",
        "table_style": "contrast",
    },
    "executive-graphite": {
        "bg": RGBColor(15, 17, 22),
        "title": RGBColor(245, 245, 245),
        "body": RGBColor(186, 192, 201),
        "accent": RGBColor(255, 173, 74),
        "font": "Microsoft YaHei UI",
        "font_title": "Segoe UI Semibold",
        "table_style": "contrast",
    },
    "slate-minimal": {
        "bg": RGBColor(245, 247, 251),
        "title": RGBColor(30, 38, 52),
        "body": RGBColor(88, 98, 112),
        "accent": RGBColor(46, 88, 160),
        "font": "Microsoft YaHei UI",
        "font_title": "Segoe UI Semibold",
        "table_style": "striped",
    },
    "elegant-serif": {
        "bg": RGBColor(248, 246, 242),
        "title": RGBColor(36, 34, 32),
        "body": RGBColor(90, 85, 80),
        "accent": RGBColor(163, 122, 74),
        "font": "Microsoft YaHei UI",
        "font_title": "Microsoft YaHei UI",
        "table_style": "soft",
    },
    "fresh-green": {
        "bg": RGBColor(246, 251, 248),
        "title": RGBColor(30, 51, 40),
        "body": RGBColor(76, 96, 86),
        "accent": RGBColor(46, 177, 120),
        "font": "Microsoft YaHei UI",
        "font_title": "Microsoft YaHei UI",
        "table_style": "soft",
    },
    "bold-corporate": {
        "bg": RGBColor(244, 247, 252),
        "title": RGBColor(20, 32, 48),
        "body": RGBColor(69, 79, 92),
        "accent": RGBColor(255, 111, 0),
        "font": "Microsoft YaHei UI",
        "font_title": "Microsoft YaHei UI",
        "table_style": "striped",
    },
}

_LAYOUT_CONFIG_CACHE: dict[str, Any] | None = None


def _default_layout_config() -> dict[str, Any]:
    """返回内置版式 schema 与语义规则配置。

    :return: 配置字典。
    """
    return {
        "schemas": {
            "content": {"max_bullets": 5, "max_paragraph_chars": 220},
            "image-left": {"max_bullets": 4, "max_paragraph_chars": 180},
            "image-right": {"max_bullets": 4, "max_paragraph_chars": 180},
            "chart": {"max_bullets": 3, "max_paragraph_chars": 160},
            "timeline": {"max_bullets": 5, "max_paragraph_chars": 160},
            "table": {"max_bullets": 3, "max_paragraph_chars": 140},
            "icon-grid": {"max_bullets": 4, "max_paragraph_chars": 120},
            "comparison": {"max_bullets": 6, "max_paragraph_chars": 160},
            "pros-cons": {"max_bullets": 6, "max_paragraph_chars": 160},
            "matrix-2x2": {"max_bullets": 4, "max_paragraph_chars": 140},
            "swot": {"max_bullets": 8, "max_paragraph_chars": 160},
            "risk-matrix": {"max_bullets": 8, "max_paragraph_chars": 160},
            "four-quadrant": {"max_bullets": 8, "max_paragraph_chars": 160},
        },
        "semantic_rules": [
            {
                "layout_type": "swot",
                "keywords": ["swot"],
                "priority": 95,
            },
            {
                "layout_type": "risk-matrix",
                "keywords": ["risk", "matrix"],
                "priority": 88,
            },
            {
                "layout_type": "four-quadrant",
                "keywords": ["quadrant", "4-quadrant", "four-quadrant", "2x2"],
                "priority": 86,
            },
            {
                "layout_type": "pros-cons",
                "keywords": ["pros", "cons", "advantage", "disadvantage"],
                "priority": 90,
            },
            {
                "layout_type": "matrix-2x2",
                "keywords": ["matrix", "2x2", "swot", "quadrant"],
                "priority": 85,
            },
            {
                "layout_type": "comparison",
                "keywords": ["compare", "comparison", "vs"],
                "priority": 80,
            },
            {
                "layout_type": "timeline",
                "keywords": ["timeline", "milestone", "phase", "roadmap"],
                "priority": 70,
            },
            {
                "layout_type": "chart",
                "keywords": ["trend", "data", "metric", "chart"],
                "priority": 60,
            },
            {
                "layout_type": "table",
                "keywords": ["table", "sheet", "表格", "明细", "列表"],
                "priority": 58,
            },
            {
                "layout_type": "icon-grid",
                "keywords": ["kpi", "card", "icon", "指标卡", "卡片", "仪表"],
                "priority": 56,
            },
            {
                "layout_type": "image",
                "keywords": ["event", "scene", "photo", "activity"],
                "priority": 50,
            },
        ],
        "quadrant_colors": {
            "swot": {
                "strength": "#4CAF50",
                "weakness": "#F44336",
                "opportunity": "#2196F3",
                "threat": "#FF9800",
            },
            "risk-matrix": {
                "high_low": "#FFA726",
                "high_high": "#E53935",
                "low_low": "#66BB6A",
                "low_high": "#42A5F5",
            },
            "four-quadrant": ["#8BC34A", "#03A9F4", "#FFB74D", "#9575CD"],
            "matrix-2x2": ["#8BC34A", "#03A9F4", "#FFB74D", "#9575CD"],
        },
        "icon_assets": {
            "strength": "icons/strength.png",
            "weakness": "icons/weakness.png",
            "opportunity": "icons/opportunity.png",
            "threat": "icons/threat.png",
            "risk": "icons/risk.png",
        },
    }


def _is_dark(color: RGBColor) -> bool:
    """判断颜色是否偏暗。

    :param color: RGBColor
    :return: True 表示偏暗
    """
    r, g, b = color[0], color[1], color[2]
    return (r + g + b) / 3 < 140


def _mix_color(base: RGBColor, target: RGBColor, ratio: float) -> RGBColor:
    """混合颜色。

    :param base: 基础色
    :param target: 目标色
    :param ratio: 混合比例 0-1
    :return: 混合后的颜色
    """
    ratio = max(0.0, min(1.0, ratio))
    r = int(base[0] + (target[0] - base[0]) * ratio)
    g = int(base[1] + (target[1] - base[1]) * ratio)
    b = int(base[2] + (target[2] - base[2]) * ratio)
    return RGBColor(r, g, b)


def _merge_layout_config(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """合并外置配置与默认配置。

    :param base: 默认配置。
    :param override: 外置配置。
    :return: 合并后的配置。
    """
    merged = {
        "schemas": dict(base.get("schemas", {})),
        "semantic_rules": list(base.get("semantic_rules", [])),
        "quadrant_colors": dict(base.get("quadrant_colors", {})),
        "icon_assets": dict(base.get("icon_assets", {})),
    }
    if not isinstance(override, dict):
        return merged
    schemas = override.get("schemas")
    if isinstance(schemas, dict):
        merged["schemas"].update(schemas)
    rules = override.get("semantic_rules")
    if isinstance(rules, list) and rules:
        merged["semantic_rules"] = rules
    quadrant_colors = override.get("quadrant_colors")
    if isinstance(quadrant_colors, dict) and quadrant_colors:
        merged["quadrant_colors"].update(quadrant_colors)
    icon_assets = override.get("icon_assets")
    if isinstance(icon_assets, dict) and icon_assets:
        merged["icon_assets"].update(icon_assets)
    return merged


def _load_layout_config() -> dict[str, Any]:
    """加载外置版式配置文件。

    :return: 配置字典。
    """
    base = _default_layout_config()
    config_path = Path(__file__).resolve().parent.parent / "assets" / "layout_schema.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return base
    except json.JSONDecodeError:
        return base
    return _merge_layout_config(base, data)


def _get_layout_config() -> dict[str, Any]:
    """获取版式配置（含缓存）。

    :return: 配置字典。
    """
    global _LAYOUT_CONFIG_CACHE
    if _LAYOUT_CONFIG_CACHE is None:
        _LAYOUT_CONFIG_CACHE = _load_layout_config()
    return _LAYOUT_CONFIG_CACHE


def _get_layout_schemas() -> dict[str, dict[str, int]]:
    """获取版式 schema 配置。

    :return: schema 字典。
    """
    config = _get_layout_config()
    schemas = config.get("schemas")
    if isinstance(schemas, dict):
        return schemas
    return _default_layout_config()["schemas"]


def _get_semantic_rules() -> list[dict[str, Any]]:
    """获取语义版式规则配置。

    :return: 规则列表。
    """
    config = _get_layout_config()
    rules = config.get("semantic_rules")
    if isinstance(rules, list):
        return rules
    return _default_layout_config()["semantic_rules"]


def _parse_color(value: Any, fallback: RGBColor) -> RGBColor:
    """解析颜色配置。

    :param value: 颜色配置值。
    :param fallback: 默认颜色。
    :return: 解析后的颜色。
    """
    if isinstance(value, RGBColor):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("#") and len(text) == 7:
            try:
                r = int(text[1:3], 16)
                g = int(text[3:5], 16)
                b = int(text[5:7], 16)
                return RGBColor(r, g, b)
            except ValueError:
                return fallback
        if "," in text:
            parts = [part.strip() for part in text.split(",")]
            if len(parts) == 3:
                try:
                    r, g, b = (int(part) for part in parts)
                    return RGBColor(r, g, b)
                except ValueError:
                    return fallback
    if isinstance(value, (list, tuple)) and len(value) == 3:
        try:
            r, g, b = (int(part) for part in value)
            return RGBColor(r, g, b)
        except ValueError:
            return fallback
    return fallback


def _get_quadrant_color_config() -> dict[str, Any]:
    """获取象限配色配置。

    :return: 配色配置。
    """
    config = _get_layout_config()
    colors = config.get("quadrant_colors")
    if isinstance(colors, dict):
        return colors
    return {}


def _get_icon_assets_config() -> dict[str, str]:
    """获取图标资源配置。

    :return: 图标路径配置。
    """
    config = _get_layout_config()
    icons = config.get("icon_assets")
    if isinstance(icons, dict):
        return {str(key): str(value) for key, value in icons.items()}
    return {}


def _resolve_quadrant_color(
    layout_key: str,
    item_key: str | None,
    index: int | None,
    fallback: RGBColor,
) -> RGBColor:
    """解析象限颜色。

    :param layout_key: 版式键。
    :param item_key: 配色项键。
    :param index: 象限序号。
    :param fallback: 默认颜色。
    :return: 象限颜色。
    """
    colors = _get_quadrant_color_config().get(layout_key)
    if isinstance(colors, dict):
        if item_key and item_key in colors:
            return _parse_color(colors[item_key], fallback)
        if index is not None and str(index) in colors:
            return _parse_color(colors[str(index)], fallback)
    if isinstance(colors, list) and index is not None and index < len(colors):
        return _parse_color(colors[index], fallback)
    return fallback


def _resolve_icon_path(icon_key: str) -> Path | None:
    """解析图标资源路径。

    :param icon_key: 图标关键字。
    :return: 图标路径。
    """
    icon_assets = _get_icon_assets_config()
    if icon_key not in icon_assets:
        return None
    raw_path = Path(icon_assets[icon_key])
    if not raw_path.is_absolute():
        raw_path = Path(__file__).resolve().parent.parent / "assets" / raw_path
    if not raw_path.exists():
        return None
    if raw_path.suffix.lower() == ".svg":
        return _ensure_svg_png(raw_path)
    return raw_path


def _ensure_svg_png(svg_path: Path) -> Path | None:
    """将 SVG 转换为 PNG，并返回 PNG 路径。

    :param svg_path: SVG 路径。
    :return: PNG 路径。
    """
    cache_dir = svg_path.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    png_path = cache_dir / f"{svg_path.stem}.png"
    if png_path.exists():
        return png_path
    try:
        import cairosvg
    except ImportError:
        print("提示: 未安装 cairosvg，无法转换 SVG。请先安装: pip install cairosvg")
        return None
    try:
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=96, output_height=96)
    except Exception:
        print(f"提示: SVG 转换失败: {svg_path}")
        return None
    return png_path
    return None

def _set_slide_background(slide, color: RGBColor) -> None:
    """设置幻灯片背景色。

    :param slide: 幻灯片对象
    :param color: 背景色
    :return: None
    """
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_accent_bar(slide, color: RGBColor, y_inch: float, height_inch: float) -> None:
    """添加强调色条。

    :param slide: 幻灯片对象
    :param color: 色条颜色
    :param y_inch: 顶部位置（英寸）
    :param height_inch: 高度（英寸）
    :return: None
    """
    left = Inches(0)
    top = Inches(y_inch)
    width = Inches(13.33)
    height = Inches(height_inch)
    shape = slide.shapes.add_shape(1, left, top, width, height)
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color
    shape.line.fill.background()


def _title_font_size(title: str) -> int:
    """根据标题长度估算字号。

    :param title: 标题文本
    :return: 字号
    """
    length = len(title)
    if length <= 10:
        return 40
    if length <= 18:
        return 34
    if length <= 28:
        return 30
    return 26


def _body_font_size(bullet_count: int) -> int:
    """根据要点数量估算字号。

    :param bullet_count: 要点数量
    :return: 字号
    """
    if bullet_count <= 3:
        return 22
    if bullet_count <= 5:
        return 20
    return 18


def _split_long_bullet(text: str, limit: int = 80) -> list[str]:
    """拆分过长要点。

    :param text: 要点文本
    :param limit: 单条长度上限
    :return: 拆分后的要点列表
    """
    if len(text) <= limit:
        return [text]
    parts = []
    buffer = ""
    for ch in text:
        buffer += ch
        if len(buffer) >= limit and ch in "，。；;,.、 ":
            parts.append(buffer.strip())
            buffer = ""
    if buffer.strip():
        parts.append(buffer.strip())
    return parts


def _normalize_bullets(content: list[str], max_bullets: int = 6) -> list[str]:
    """规范化要点列表。

    :param content: 原始要点列表
    :param max_bullets: 最大要点数量
    :return: 规范化后的要点列表
    """
    normalized: list[str] = []
    for item in content:
        normalized.extend(_split_long_bullet(str(item)))
    return normalized[:max_bullets]


def _split_long_paragraph(text: str, max_chars: int = 220) -> list[dict[str, str]]:
    """拆分超长段落并尽量保留语义与小标题。

    :param text: 段落文本
    :param max_chars: 单页最大字符数
    :return: 拆分后的段落列表
    """
    if len(text) <= max_chars:
        return [{"heading": "", "text": text}]

    heading_tokens = [
        "背景",
        "问题",
        "结论",
        "对策",
        "建议",
        "目标",
        "风险",
        "机会",
        "现状",
        "价值",
        "挑战",
        "方法",
        "结果",
        "下一步",
        "里程碑",
        "计划",
        "复盘",
        "产出",
        "指标",
        "假设",
        "策略",
    ]

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n") if line.strip()]

    sections: list[dict[str, str]] = []
    current_heading = ""
    current_body: list[str] = []
    for line in lines:
        raw = line.strip()
        token = raw.replace("：", ":").split(":", 1)[0].strip()
        if token in heading_tokens:
            if current_body:
                sections.append({"heading": current_heading, "text": " ".join(current_body)})
                current_body = []
            current_heading = token
            remainder = raw.split("：", 1)[-1].split(":", 1)[-1].strip()
            if remainder and remainder != token:
                current_body.append(remainder)
        else:
            current_body.append(raw)
    if current_body:
        sections.append({"heading": current_heading, "text": " ".join(current_body)})

    if not sections:
        sections = [{"heading": "", "text": text}]

    results: list[dict[str, str]] = []
    for section in sections:
        content = section["text"]
        heading = section["heading"]
        if len(content) <= max_chars:
            results.append({"heading": heading, "text": content})
            continue

        sentences = []
        buffer = ""
        for ch in content:
            buffer += ch
            if ch in "。！？!?":
                sentences.append(buffer.strip())
                buffer = ""
        if buffer.strip():
            sentences.append(buffer.strip())

        if len(sentences) <= 1:
            midpoint = max(1, len(content) // 2)
            results.append({"heading": heading, "text": content[:midpoint].strip()})
            results.append({"heading": heading, "text": content[midpoint:].strip()})
            continue

        page_buffer = ""
        for sentence in sentences:
            if not page_buffer:
                page_buffer = sentence
                continue
            if len(page_buffer) + len(sentence) <= max_chars:
                page_buffer += sentence
            else:
                results.append({"heading": heading, "text": page_buffer.strip()})
                page_buffer = sentence
        if page_buffer.strip():
            results.append({"heading": heading, "text": page_buffer.strip()})

    return results


def _chunk_bullets(content: list[str], max_bullets: int) -> list[list[str]]:
    """将要点分块用于自动拆页。

    :param content: 规范化后的要点列表
    :param max_bullets: 每页最大要点数量
    :return: 分块后的要点列表
    """
    if max_bullets <= 0:
        return [content]
    return [content[i : i + max_bullets] for i in range(0, len(content), max_bullets)]


def _resolve_font(style: dict[str, Any], key: str, fallback: str = "微软雅黑") -> str:
    """解析字体配置。

    :param style: 样式配置
    :param key: 字体键名
    :param fallback: 默认字体
    :return: 字体名称
    """
    font_value = style.get(key)
    if not font_value and key != "font":
        font_value = style.get("font")
    return str(font_value) if font_value else fallback


def _apply_title_style(shape, color: RGBColor, size_pt: int, font_name: str) -> None:
    """应用标题样式。

    :param shape: 标题形状
    :param color: 颜色
    :param size_pt: 字号
    :param font_name: 字体名称
    :return: None
    """
    if not shape:
        return
    if not shape.text_frame:
        return
    for paragraph in shape.text_frame.paragraphs:
        paragraph.font.name = font_name
        paragraph.font.size = Pt(size_pt)
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.color.rgb = color
            run.font.size = Pt(size_pt)
            _set_east_asia_font(run, font_name)


def _apply_body_style(text_frame, color: RGBColor, size_pt: int, font_name: str) -> None:
    """应用正文样式。

    :param text_frame: 文本框
    :param color: 颜色
    :param size_pt: 字号
    :param font_name: 字体名称
    :return: None
    """
    for paragraph in text_frame.paragraphs:
        paragraph.font.name = font_name
        paragraph.font.size = Pt(size_pt)
        paragraph.space_after = Pt(8)
        paragraph.line_spacing = 1.2
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.color.rgb = color
            run.font.size = Pt(size_pt)
            _set_east_asia_font(run, font_name)


def _set_east_asia_font(run, font_name: str) -> None:
    """为中文设置 East Asia 字体，避免乱码。

    :param run: 文本 run
    :return: None
    """
    r_pr = run._r.get_or_add_rPr()
    get_latin = getattr(r_pr, "get_or_add_latin", None)
    get_ea = getattr(r_pr, "get_or_add_ea", None)
    get_cs = getattr(r_pr, "get_or_add_cs", None)
    if get_latin:
        get_latin().set("typeface", font_name)
    if get_ea:
        get_ea().set("typeface", font_name)
    if get_cs:
        get_cs().set("typeface", font_name)


def _tune_text_frame(text_frame) -> None:
    """优化文本框排版。

    :param text_frame: 文本框
    :return: None
    """
    text_frame.word_wrap = True
    text_frame.margin_left = Pt(8)
    text_frame.margin_right = Pt(8)
    text_frame.margin_top = Pt(6)
    text_frame.margin_bottom = Pt(6)


def _clear_slides(prs: Presentation) -> None:
    """清空模板内置的示例页。

    :param prs: 演示文稿对象
    :return: None
    """
    slide_ids = list(prs.slides._sldIdLst)  # type: ignore[attr-defined]
    for slide_id in slide_ids:
        r_id = slide_id.rId
        prs.part.drop_rel(r_id)
        prs.slides._sldIdLst.remove(slide_id)  # type: ignore[attr-defined]


def _resolve_template_path(template_name: str) -> Path:
    """解析模板路径。

    :param template_name: 模板名称
    :return: 模板路径
    """
    templates_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    external_dir = templates_dir / "external"
    if template_name.endswith(".pptx"):
        direct = templates_dir / template_name
        if direct.exists():
            return direct
        ext_direct = external_dir / template_name
        if ext_direct.exists():
            return ext_direct
        return Path(template_name)
    direct = templates_dir / f"{template_name}.pptx"
    if direct.exists():
        return direct
    ext_direct = external_dir / f"{template_name}.pptx"
    if ext_direct.exists():
        return ext_direct
    return direct


def _choose_template_by_text(text: str) -> str:
    """根据主题关键词选择模板。

    :param text: 主题或标题文本
    :return: 模板名称
    """
    lower_text = text.lower()
    if any(key in lower_text for key in ["ai", "科技", "技术", "tech", "数据", "算法", "产品"]):
        return "tech-neon"
    if any(key in lower_text for key in ["周报", "周度", "周总结", "工作周报", "工作总结"]):
        return "minimal-business"
    if any(key in lower_text for key in ["高端", "旗舰", "premium", "luxe", "年度"]):
        return "tech-premium"
    if any(key in lower_text for key in ["董事会", "高管", "executive", "board", "graphite"]):
        return "executive-graphite"
    if any(key in lower_text for key in ["极简", "简报", "管理层", "slate"]):
        return "slate-minimal"
    if any(key in lower_text for key in ["医疗", "医药", "健康", "医院", "护理", "临床"]):
        return "fresh-green"
    if any(key in lower_text for key in ["教育", "培训", "课程", "教学", "学习", "教育学"]):
        return "minimal-business"
    if any(
        key in lower_text
        for key in ["金融", "投资", "经营", "战略", "公司", "商业", "business", "银行", "证券", "保险", "资管"]
    ):
        return "bold-corporate"
    if any(key in lower_text for key in ["政务", "政府", "公共", "公共服务", "治理", "民生", "政企"]):
        return "minimal-business"
    if any(
        key in lower_text
        for key in [
            "制造",
            "工业",
            "供应链",
            "工厂",
            "生产",
            "质检",
            "设备",
            "仓储",
            "物流",
            "产线",
            "良率",
        ]
    ):
        return "bold-corporate"
    if any(
        key in lower_text
        for key in ["消费", "零售", "电商", "用户", "品牌", "渠道", "快消", "门店", "会员", "营销", "增长"]
    ):
        return "warm-light"
    if any(key in lower_text for key in ["设计", "品牌", "文化", "艺术", "审美", "创意"]):
        return "elegant-serif"
    if any(key in lower_text for key in ["环保", "自然", "生活", "公益", "绿色"]):
        return "fresh-green"
    return "warm-light"


def _resolve_template_name(slides_data: list[dict[str, Any]], theme_hint: str | None) -> str:
    """根据提示或内容选择模板。

    :param slides_data: 幻灯片数据。
    :param theme_hint: 主题提示。
    :return: 模板名称。
    """
    if theme_hint:
        return _choose_template_by_text(theme_hint)
    if slides_data:
        title = str(slides_data[0].get("title", ""))
        if title:
            return _choose_template_by_text(title)
    return "minimal-business"

def _infer_layout_type(
    slide_info: dict[str, Any],
    slide_index: int,
    total_slides: int,
    prefer_image: bool = True,
) -> str:
    """根据标题与内容推断版式类型。
    :param slide_info: 幻灯片数据。
    :param slide_index: 幻灯片序号（从 0 开始）。
    :param total_slides: 幻灯片总数。
    :param prefer_image: 是否优先图片版式。
    :return: 推断的版式类型。
    """
    explicit = str(slide_info.get("layout_type", "")).strip().lower()
    if explicit:
        return explicit
    if slide_index == 0 or slide_index == total_slides - 1:
        return ""
    title = str(slide_info.get("title", ""))
    content = slide_info.get("content", "")
    if isinstance(content, list):
        content_text = " ".join(str(item) for item in content)
    else:
        content_text = str(content)
    text = f"{title} {content_text}".lower()

    best_layout = ""
    best_priority = -1
    for rule in _get_semantic_rules():
        layout_type = str(rule.get("layout_type", "")).strip().lower()
        if not layout_type:
            continue
        if layout_type == "image" and not prefer_image:
            continue
        keywords = rule.get("keywords", [])
        if not isinstance(keywords, list) or not keywords:
            continue
        matched = False
        for keyword in keywords:
            if not isinstance(keyword, str):
                continue
            if keyword.lower() in text:
                matched = True
                break
        if not matched:
            continue
        priority = int(rule.get("priority", 0) or 0)
        if priority > best_priority:
            best_priority = priority
            best_layout = layout_type

    if best_layout == "image":
        return "image-left" if slide_index % 2 == 0 else "image-right"
    return best_layout

def _resolve_layout_schema(
    layout_type: str,
    max_bullets_per_slide: int,
    max_paragraph_chars: int,
) -> dict[str, int]:
    """根据版式返回约束配置。
    :param layout_type: 版式类型。
    :param max_bullets_per_slide: 默认单页要点上限。
    :param max_paragraph_chars: 默认段落拆分阈值。
    :return: 约束配置。
    """
    schemas = _get_layout_schemas()
    normalized = layout_type if layout_type else "content"
    schema = schemas.get(normalized, {})
    return {
        "max_bullets": int(schema.get("max_bullets", max_bullets_per_slide)),
        "max_paragraph_chars": int(schema.get("max_paragraph_chars", max_paragraph_chars)),
    }

def _split_heading_body(text: str) -> tuple[str, str]:
    """拆分标题与正文。

    :param text: 原始文本。
    :return: 标题与正文。
    """
    separators = ["：", ":", "—", "-", "|", "｜"]
    for sep in separators:
        if sep in text:
            left, right = text.split(sep, 1)
            left = left.strip()
            right = right.strip()
            if left and right:
                return left, right
    return text.strip(), ""


def _split_comparison_pair(text: str) -> tuple[str, str] | None:
    """拆分对比成对文本。

    :param text: 原始文本。
    :return: 左右文本对。
    """
    separators = ["｜", "|", " vs ", " VS ", " vs. ", " VS. ", " / ", " 对 "]
    lower_text = text.lower()
    for sep in separators:
        if sep.lower() in lower_text:
            idx = lower_text.find(sep.lower())
            left = text[:idx].strip()
            right = text[idx + len(sep):].strip()
            if left and right:
                return left, right
    return None


def _strip_label(text: str, labels: list[str]) -> str:
    """去除前缀标签。

    :param text: 原始文本。
    :param labels: 标签列表。
    :return: 去除标签后的文本。
    """
    for label in labels:
        if text.startswith(label):
            trimmed = text[len(label):].lstrip("：:-— ")
            return trimmed or text
    return text


def _resolve_comparison_columns(
    slide_info: dict[str, Any],
    bullets: list[str],
) -> tuple[str, list[str], str, list[str]]:
    """解析对比版式列数据。

    :param slide_info: 幻灯片数据。
    :param bullets: 要点列表。
    :return: 左标题、左内容、右标题、右内容。
    """
    default_left = "对比项A"
    default_right = "对比项B"
    columns = slide_info.get("columns")
    if isinstance(columns, list) and len(columns) >= 2:
        left_col = columns[0] or {}
        right_col = columns[1] or {}
        left_title = str(left_col.get("title", default_left))
        right_title = str(right_col.get("title", default_right))
        left_items = left_col.get("items")
        right_items = right_col.get("items")
        if isinstance(left_items, list) and isinstance(right_items, list):
            return left_title, [str(item) for item in left_items], right_title, [str(item) for item in right_items]
    column_titles = slide_info.get("column_titles")
    if isinstance(column_titles, list) and len(column_titles) >= 2:
        left_title = str(column_titles[0])
        right_title = str(column_titles[1])
    else:
        left_title, right_title = default_left, default_right

    left_items: list[str] = []
    right_items: list[str] = []
    leftovers: list[str] = []
    for item in bullets:
        pair = _split_comparison_pair(str(item))
        if pair:
            left_items.append(pair[0])
            right_items.append(pair[1])
        else:
            leftovers.append(str(item))
    if not left_items and not right_items:
        mid = max(1, len(bullets) // 2)
        left_items = [str(item) for item in bullets[:mid]]
        right_items = [str(item) for item in bullets[mid:]]
    else:
        for item in leftovers:
            if len(left_items) <= len(right_items):
                left_items.append(item)
            else:
                right_items.append(item)
    return left_title, left_items, right_title, right_items


def _resolve_pros_cons(slide_info: dict[str, Any], bullets: list[str]) -> tuple[list[str], list[str]]:
    """解析优劣势列数据。

    :param slide_info: 幻灯片数据。
    :param bullets: 要点列表。
    :return: 优势列表、劣势列表。
    """
    pros = slide_info.get("pros")
    cons = slide_info.get("cons")
    if isinstance(pros, list) and isinstance(cons, list):
        return [str(item) for item in pros], [str(item) for item in cons]

    pros_labels = ["优势", "优点", "利好", "正面", "收益", "机会"]
    cons_labels = ["劣势", "缺点", "风险", "问题", "挑战", "负面", "成本"]

    pros_items: list[str] = []
    cons_items: list[str] = []
    unknown: list[str] = []

    for item in bullets:
        text = str(item)
        if any(text.startswith(label) for label in pros_labels):
            pros_items.append(_strip_label(text, pros_labels))
        elif any(text.startswith(label) for label in cons_labels):
            cons_items.append(_strip_label(text, cons_labels))
        else:
            unknown.append(text)

    if not pros_items or not cons_items:
        mid = max(1, len(bullets) // 2)
        return [str(item) for item in bullets[:mid]], [str(item) for item in bullets[mid:]]

    for item in unknown:
        if len(pros_items) <= len(cons_items):
            pros_items.append(item)
        else:
            cons_items.append(item)
    return pros_items, cons_items


def _format_bullet(text: str) -> str:
    """补充项目符号前缀。

    :param text: 原始文本。
    :return: 处理后的文本。
    """
    stripped = text.strip()
    if not stripped:
        return ""
    if stripped.startswith(("•", "-", "·")):
        return stripped
    return f"• {stripped}"


def _apply_paragraph_style(
    paragraph,
    color: RGBColor,
    size_pt: int,
    bold: bool,
    font_name: str,
) -> None:
    """应用段落样式。

    :param paragraph: 段落对象。
    :param color: 字体颜色。
    :param size_pt: 字号。
    :param bold: 是否加粗。
    :param font_name: 字体名称。
    :return: None
    """
    paragraph.font.name = font_name
    paragraph.font.size = Pt(size_pt)
    paragraph.font.bold = bold
    paragraph.space_after = Pt(6)
    for run in paragraph.runs:
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.font.bold = bold
        run.font.color.rgb = color
        _set_east_asia_font(run, font_name)


def _fill_column(text_frame, heading: str, items: list[str], style: dict[str, RGBColor]) -> None:
    """填充对比列内容。

    :param text_frame: 文本框。
    :param heading: 列标题。
    :param items: 项目列表。
    :param style: 颜色样式。
    :return: None
    """
    _tune_text_frame(text_frame)
    text_frame.text = heading
    heading_font = _resolve_font(style, "font_title", DEFAULT_FONT_NAME)
    body_font = _resolve_font(style, "font", DEFAULT_FONT_NAME)
    if text_frame.paragraphs:
        _apply_paragraph_style(text_frame.paragraphs[0], style["accent"], 20, True, heading_font)
    for item in items:
        if not str(item).strip():
            continue
        paragraph = text_frame.add_paragraph()
        paragraph.text = _format_bullet(str(item))
        _apply_paragraph_style(paragraph, style["body"], 18, False, body_font)


def _render_comparison_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    left_title: str,
    left_items: list[str],
    right_title: str,
    right_items: list[str],
    style: dict[str, RGBColor],
) -> None:
    """渲染对比版式。

    :param prs: 演示文稿对象。
    :param slide_layout: 幻灯片布局。
    :param title: 标题。
    :param left_title: 左列标题。
    :param left_items: 左列要点。
    :param right_title: 右列标题。
    :param right_items: 右列要点。
    :param style: 样式配置。
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    font_title = _resolve_font(style, "font_title", DEFAULT_FONT_NAME)
    font_body = _resolve_font(style, "font", DEFAULT_FONT_NAME)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            font_title,
        )

    left_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(6.0), Inches(4.6))
    right_box = slide.shapes.add_textbox(Inches(6.8), Inches(1.6), Inches(6.0), Inches(4.6))
    _fill_column(left_box.text_frame, left_title, left_items, style)
    _fill_column(right_box.text_frame, right_title, right_items, style)


def _render_matrix_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    bullets: list[str],
    style: dict[str, RGBColor],
) -> None:
    """渲染矩阵版式。

    :param prs: 演示文稿对象。
    :param slide_layout: 幻灯片布局。
    :param title: 标题。
    :param bullets: 要点列表。
    :param style: 样式配置。
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
        )

    items = [str(item) for item in bullets[:4]]
    while len(items) < 4:
        items.append("")

    positions = [
        (Inches(0.7), Inches(1.6)),
        (Inches(6.8), Inches(1.6)),
        (Inches(0.7), Inches(4.1)),
        (Inches(6.8), Inches(4.1)),
    ]
    width = Inches(6.0)
    height = Inches(2.3)

    for index, item in enumerate(items):
        left, top = positions[index]
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = style["bg"]
        box.line.color.rgb = style["accent"]
        box.line.width = Pt(1)

        text_frame = box.text_frame
        _tune_text_frame(text_frame)
        heading, body = _split_heading_body(item)
        text_frame.text = heading
        if text_frame.paragraphs:
            if body:
                _apply_paragraph_style(text_frame.paragraphs[0], style["accent"], 18, True, font_title)
            else:
                _apply_paragraph_style(text_frame.paragraphs[0], style["body"], 16, False, font_body)
        if body:
            paragraph = text_frame.add_paragraph()
            paragraph.text = body
            _apply_paragraph_style(paragraph, style["body"], 16, False, font_body)


def _tint_color(color: RGBColor, ratio: float) -> RGBColor:
    """生成浅色渐变色。

    :param color: 基础颜色。
    :param ratio: 变亮比例。
    :return: 新颜色。
    """
    ratio = max(0.0, min(1.0, ratio))
    r, g, b = color[0], color[1], color[2]
    r = int(r + (255 - r) * ratio)
    g = int(g + (255 - g) * ratio)
    b = int(b + (255 - b) * ratio)
    return RGBColor(r, g, b)


def _add_gradient_panel(
    slide,
    left_inch: float,
    top_inch: float,
    width_inch: float,
    height_inch: float,
    base_color: RGBColor,
) -> None:
    """绘制简易渐变底板。

    :param slide: 幻灯片对象。
    :param left_inch: 左侧位置（英寸）。
    :param top_inch: 顶部位置（英寸）。
    :param width_inch: 宽度（英寸）。
    :param height_inch: 高度（英寸）。
    :param base_color: 基础颜色。
    :return: None
    """
    top_color = _tint_color(base_color, 0.25)
    bottom_color = _tint_color(base_color, 0.45)
    half_height = height_inch / 2

    top_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left_inch),
        Inches(top_inch),
        Inches(width_inch),
        Inches(half_height),
    )
    top_shape.fill.solid()
    top_shape.fill.fore_color.rgb = top_color
    top_shape.line.color.rgb = base_color
    top_shape.line.width = Pt(1)

    bottom_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left_inch),
        Inches(top_inch + half_height),
        Inches(width_inch),
        Inches(half_height),
    )
    bottom_shape.fill.solid()
    bottom_shape.fill.fore_color.rgb = bottom_color
    bottom_shape.line.color.rgb = base_color
    bottom_shape.line.width = Pt(1)


def _add_label_tag(
    slide,
    text: str,
    left_inch: float,
    top_inch: float,
    width_inch: float,
    height_inch: float,
    color: RGBColor,
    font_name: str,
) -> None:
    """添加象限标签条。

    :param slide: 幻灯片对象。
    :param text: 标签文本。
    :param left_inch: 左侧位置（英寸）。
    :param top_inch: 顶部位置（英寸）。
    :param width_inch: 宽度（英寸）。
    :param height_inch: 高度（英寸）。
    :param color: 标签颜色。
    :param font_name: 字体名称。
    :return: None
    """
    if not text.strip():
        return
    tag = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left_inch),
        Inches(top_inch),
        Inches(width_inch),
        Inches(height_inch),
    )
    tag.fill.solid()
    tag.fill.fore_color.rgb = color
    tag.line.fill.background()
    text_frame = tag.text_frame
    _tune_text_frame(text_frame)
    text_frame.text = text
    if text_frame.paragraphs:
        _apply_paragraph_style(text_frame.paragraphs[0], RGBColor(255, 255, 255), 12, True, font_name)


def _add_corner_ribbon(
    slide,
    left_inch: float,
    top_inch: float,
    width_inch: float,
    height_inch: float,
    color: RGBColor,
) -> None:
    """添加象限角标。

    :param slide: 幻灯片对象。
    :param left_inch: 左侧位置（英寸）。
    :param top_inch: 顶部位置（英寸）。
    :param width_inch: 宽度（英寸）。
    :param height_inch: 高度（英寸）。
    :param color: 角标颜色。
    :return: None
    """
    size = min(width_inch, height_inch) * 0.28
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_TRIANGLE,
        Inches(left_inch + width_inch - size),
        Inches(top_inch),
        Inches(size),
        Inches(size),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _tint_color(color, 0.08)
    shape.line.fill.background()
    shape.rotation = 90

    ribbon = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left_inch + width_inch - size * 1.05),
        Inches(top_inch + size * 0.15),
        Inches(size * 0.9),
        Inches(size * 0.28),
    )
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = _tint_color(color, 0.15)
    ribbon.line.fill.background()


def _add_corner_ribbon_text(
    slide,
    text: str,
    left_inch: float,
    top_inch: float,
    width_inch: float,
    height_inch: float,
    color: RGBColor,
    font_name: str,
) -> None:
    """添加角标文字。

    :param slide: 幻灯片对象。
    :param text: 角标文字。
    :param left_inch: 左侧位置（英寸）。
    :param top_inch: 顶部位置（英寸）。
    :param width_inch: 宽度（英寸）。
    :param height_inch: 高度（英寸）。
    :param color: 角标颜色。
    :param font_name: 字体名称。
    :return: None
    """
    if not text.strip():
        return
    size = min(width_inch, height_inch) * 0.28
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(left_inch + width_inch - size * 0.92),
        Inches(top_inch + size * 0.08),
        Inches(size * 0.18),
        Inches(size * 0.18),
    )
    dot.fill.solid()
    dot.fill.fore_color.rgb = _tint_color(color, 0.65)
    dot.line.fill.background()

    box = slide.shapes.add_textbox(
        Inches(left_inch + width_inch - size * 0.92),
        Inches(top_inch + size * 0.28),
        Inches(size * 0.82),
        Inches(size * 0.6),
    )
    text_frame = box.text_frame
    _tune_text_frame(text_frame)
    text_frame.text = text
    if text_frame.paragraphs:
        _apply_paragraph_style(text_frame.paragraphs[0], _tint_color(color, 0.75), 12, True, font_name)


def _add_texture_dots(
    slide,
    left_inch: float,
    top_inch: float,
    width_inch: float,
    height_inch: float,
    color: RGBColor,
    density: int = 3,
) -> None:
    """添加局部背景纹理点。

    :param slide: 幻灯片对象。
    :param left_inch: 左侧位置（英寸）。
    :param top_inch: 顶部位置（英寸）。
    :param width_inch: 宽度（英寸）。
    :param height_inch: 高度（英寸）。
    :param color: 点的颜色。
    :param density: 点数量。
    :return: None
    """
    if density <= 0:
        return
    dot_color = _tint_color(color, 0.65)
    offsets = [
        (0.25, 0.2),
        (0.7, 0.35),
        (0.45, 0.65),
        (0.8, 0.8),
        (0.15, 0.75),
    ]
    for idx in range(min(density, len(offsets))):
        ox, oy = offsets[idx]
        size = 0.12
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(left_inch + width_inch * ox),
            Inches(top_inch + height_inch * oy),
            Inches(size),
            Inches(size),
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = dot_color
        dot.line.fill.background()


ICON_SHAPES = {
    "strength": MSO_SHAPE.OVAL,
    "weakness": MSO_SHAPE.ISOSCELES_TRIANGLE,
    "opportunity": MSO_SHAPE.HEXAGON,
    "threat": MSO_SHAPE.DIAMOND,
    "risk": MSO_SHAPE.ROUNDED_RECTANGLE,
}


def _add_icon(
    slide,
    icon_key: str,
    left_inch: float,
    top_inch: float,
    size_inch: float,
    color: RGBColor,
) -> None:
    """添加简易图标形状。

    :param slide: 幻灯片对象。
    :param icon_key: 图标关键字。
    :param left_inch: 左侧位置（英寸）。
    :param top_inch: 顶部位置（英寸）。
    :param size_inch: 图标尺寸（英寸）。
    :param color: 图标颜色。
    :return: None
    """
    icon_path = _resolve_icon_path(icon_key)
    if icon_path:
        slide.shapes.add_picture(
            str(icon_path),
            Inches(left_inch),
            Inches(top_inch),
            width=Inches(size_inch),
            height=Inches(size_inch),
        )
        return
    shape_type = ICON_SHAPES.get(icon_key)
    if shape_type is None:
        return
    shape = slide.shapes.add_shape(
        shape_type,
        Inches(left_inch),
        Inches(top_inch),
        Inches(size_inch),
        Inches(size_inch),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def _resolve_generic_quadrants(
    slide_info: dict[str, Any],
    bullets: list[str],
    layout_key: str,
) -> list[dict[str, Any]]:
    """解析通用四象限数据。

    :param slide_info: 幻灯片数据。
    :param bullets: 要点列表。
    :param layout_key: 版式键。
    :return: 四象限数据。
    """
    quadrants = slide_info.get("quadrants")
    if isinstance(quadrants, list) and len(quadrants) >= 4:
        result = []
        for index, quadrant in enumerate(quadrants[:4]):
            if not isinstance(quadrant, dict):
                continue
            result.append(
                {
                    "title": str(quadrant.get("title", "")),
                    "items": [str(item) for item in quadrant.get("items", []) if str(item).strip()],
                    "icon": quadrant.get("icon"),
                    "badge": quadrant.get("badge"),
                    "color": _parse_color(
                        quadrant.get("color"),
                        _resolve_quadrant_color(layout_key, None, index, RGBColor(230, 230, 230)),
                    ),
                }
            )
        if len(result) == 4:
            return result
    titles = slide_info.get("quadrant_titles")
    if not isinstance(titles, list) or len(titles) < 4:
        titles = ["象限一", "象限二", "象限三", "象限四"]
    chunk_size = max(1, len(bullets) // 4)
    data = []
    cursor = 0
    for index in range(4):
        items = [str(item) for item in bullets[cursor : cursor + chunk_size] if str(item).strip()]
        cursor += chunk_size
        if index == 3:
            items = [str(item) for item in bullets[cursor - chunk_size :] if str(item).strip()]
        data.append(
            {
                "title": str(titles[index]),
                "badge": f"Q{index + 1}",
                "items": items,
                "color": _resolve_quadrant_color(layout_key, None, index, RGBColor(230, 230, 230)),
            }
        )
    return data


def _resolve_swot_quadrants(
    slide_info: dict[str, Any],
    bullets: list[str],
) -> list[dict[str, Any]]:
    """解析 SWOT 四象限数据。

    :param slide_info: 幻灯片数据。
    :param bullets: 要点列表。
    :return: SWOT 四象限数据。
    """
    swot = slide_info.get("swot")
    if isinstance(swot, dict):
        strengths = swot.get("strengths", [])
        weaknesses = swot.get("weaknesses", [])
        opportunities = swot.get("opportunities", [])
        threats = swot.get("threats", [])
    else:
        strengths = slide_info.get("strengths", [])
        weaknesses = slide_info.get("weaknesses", [])
        opportunities = slide_info.get("opportunities", [])
        threats = slide_info.get("threats", [])

    if not isinstance(strengths, list):
        strengths = []
    if not isinstance(weaknesses, list):
        weaknesses = []
    if not isinstance(opportunities, list):
        opportunities = []
    if not isinstance(threats, list):
        threats = []

    if not (strengths or weaknesses or opportunities or threats):
        s_labels = ["S", "优势", "强项", "strength"]
        w_labels = ["W", "劣势", "短板", "weakness"]
        o_labels = ["O", "机会", "机遇", "opportunity"]
        t_labels = ["T", "威胁", "风险", "threat"]
        unknown = []
        for item in bullets:
            text = str(item).strip()
            if any(text.startswith(label) for label in s_labels):
                strengths.append(_strip_label(text, s_labels))
            elif any(text.startswith(label) for label in w_labels):
                weaknesses.append(_strip_label(text, w_labels))
            elif any(text.startswith(label) for label in o_labels):
                opportunities.append(_strip_label(text, o_labels))
            elif any(text.startswith(label) for label in t_labels):
                threats.append(_strip_label(text, t_labels))
            else:
                unknown.append(text)
        for item in unknown:
            bucket = min(
                [
                    (len(strengths), strengths),
                    (len(weaknesses), weaknesses),
                    (len(opportunities), opportunities),
                    (len(threats), threats),
                ],
                key=lambda pair: pair[0],
            )[1]
            bucket.append(item)

    return [
        {
            "title": "优势",
            "items": [str(item) for item in strengths],
            "icon": "strength",
            "badge": "S",
            "color": _resolve_quadrant_color(
                "swot",
                "strength",
                0,
                RGBColor(76, 175, 80),
            ),
        },
        {
            "title": "劣势",
            "items": [str(item) for item in weaknesses],
            "icon": "weakness",
            "badge": "W",
            "color": _resolve_quadrant_color(
                "swot",
                "weakness",
                1,
                RGBColor(244, 67, 54),
            ),
        },
        {
            "title": "机会",
            "items": [str(item) for item in opportunities],
            "icon": "opportunity",
            "badge": "O",
            "color": _resolve_quadrant_color(
                "swot",
                "opportunity",
                2,
                RGBColor(33, 150, 243),
            ),
        },
        {
            "title": "威胁",
            "items": [str(item) for item in threats],
            "icon": "threat",
            "badge": "T",
            "color": _resolve_quadrant_color(
                "swot",
                "threat",
                3,
                RGBColor(255, 152, 0),
            ),
        },
    ]


def _resolve_risk_matrix_quadrants(
    slide_info: dict[str, Any],
    bullets: list[str],
) -> list[dict[str, Any]]:
    """解析风险矩阵四象限数据。

    :param slide_info: 幻灯片数据。
    :param bullets: 要点列表。
    :return: 风险矩阵四象限数据。
    """
    high_high: list[str] = []
    high_low: list[str] = []
    low_high: list[str] = []
    low_low: list[str] = []

    risks = slide_info.get("risks")
    if isinstance(risks, list):
        for item in risks:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label", "")).strip() or str(item.get("name", "")).strip()
            if not label:
                continue
            impact = int(item.get("impact", 0) or 0)
            probability = int(item.get("probability", 0) or 0)
            impact_high = impact >= 3
            probability_high = probability >= 3
            if impact_high and probability_high:
                high_high.append(label)
            elif impact_high and not probability_high:
                low_high.append(label)
            elif not impact_high and probability_high:
                high_low.append(label)
            else:
                low_low.append(label)
    else:
        items = [str(item) for item in bullets if str(item).strip()]
        if items:
            split = max(1, len(items) // 4)
            high_high = items[:split]
            high_low = items[split : split * 2]
            low_high = items[split * 2 : split * 3]
            low_low = items[split * 3 :]

    return [
        {
            "title": "高概率 / 低影响",
            "items": high_low,
            "icon": "risk",
            "badge": "HL",
            "color": _resolve_quadrant_color(
                "risk-matrix",
                "high_low",
                0,
                RGBColor(255, 167, 38),
            ),
        },
        {
            "title": "高概率 / 高影响",
            "items": high_high,
            "icon": "risk",
            "badge": "HH",
            "color": _resolve_quadrant_color(
                "risk-matrix",
                "high_high",
                1,
                RGBColor(229, 57, 53),
            ),
        },
        {
            "title": "低概率 / 低影响",
            "items": low_low,
            "icon": "risk",
            "badge": "LL",
            "color": _resolve_quadrant_color(
                "risk-matrix",
                "low_low",
                2,
                RGBColor(102, 187, 106),
            ),
        },
        {
            "title": "低概率 / 高影响",
            "items": low_high,
            "icon": "risk",
            "badge": "LH",
            "color": _resolve_quadrant_color(
                "risk-matrix",
                "low_high",
                3,
                RGBColor(66, 165, 245),
            ),
        },
    ]


def _render_quadrant_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    quadrants: list[dict[str, Any]],
    style: dict[str, RGBColor],
    axis_labels: tuple[str, str] | None = None,
) -> None:
    """渲染四象限版式。

    :param prs: 演示文稿对象。
    :param slide_layout: 幻灯片布局。
    :param title: 标题。
    :param quadrants: 四象限数据。
    :param style: 样式配置。
    :param axis_labels: 轴标签。
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    font_title = _resolve_font(style, "font_title", DEFAULT_FONT_NAME)
    font_body = _resolve_font(style, "font", DEFAULT_FONT_NAME)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            font_title,
        )

    positions = [
        (0.7, 1.6),
        (6.8, 1.6),
        (0.7, 4.1),
        (6.8, 4.1),
    ]
    width = 6.0
    height = 2.3
    tint_levels = [0.15, 0.28, 0.35, 0.22]

    for index in range(4):
        quadrant = quadrants[index] if index < len(quadrants) else {"title": "", "items": []}
        left, top = positions[index]
        base_color = _parse_color(
            quadrant.get("color"),
            _tint_color(style["accent"], tint_levels[index]),
        )
        _add_gradient_panel(slide, left, top, width, height, base_color)
        _add_texture_dots(slide, left, top, width, height, base_color, density=3)
        _add_corner_ribbon(slide, left, top, width, height, base_color)

        icon_key = quadrant.get("icon")
        if icon_key:
            _add_icon(slide, str(icon_key), left + 0.15, top + 0.1, 0.35, base_color)

        heading = str(quadrant.get("title", "")).strip()
        if heading:
            _add_label_tag(
                slide,
                heading,
                left + 0.2,
                top + 0.08,
                2.0,
                0.32,
                base_color,
                font_title,
            )
        badge_text = str(quadrant.get("badge", "")).strip()
        if badge_text:
            _add_corner_ribbon_text(slide, badge_text, left, top, width, height, base_color, font_title)

        text_box = slide.shapes.add_textbox(
            Inches(left + 0.6),
            Inches(top + 0.15),
            Inches(width - 0.8),
            Inches(height - 0.3),
        )
        text_frame = text_box.text_frame
        _tune_text_frame(text_frame)
        text_frame.text = ""
        if text_frame.paragraphs:
            _apply_paragraph_style(text_frame.paragraphs[0], style["body"], 16, False, font_body)
        for item in quadrant.get("items", []):
            text = str(item).strip()
            if not text:
                continue
            paragraph = text_frame.add_paragraph()
            paragraph.text = _format_bullet(text)
            _apply_paragraph_style(paragraph, style["body"], 16, False, font_body)

    if axis_labels:
        x_label, y_label = axis_labels
        x_box = slide.shapes.add_textbox(Inches(5.0), Inches(6.5), Inches(3.0), Inches(0.4))
        x_frame = x_box.text_frame
        x_frame.text = f"{x_label} →"
        if x_frame.paragraphs:
            _apply_paragraph_style(x_frame.paragraphs[0], style["body"], 14, True, font_body)

        y_box = slide.shapes.add_textbox(Inches(0.1), Inches(3.2), Inches(1.2), Inches(0.8))
        y_frame = y_box.text_frame
        y_frame.text = f"{y_label} ↑"
        if y_frame.paragraphs:
            _apply_paragraph_style(y_frame.paragraphs[0], style["body"], 14, True, font_body)


def _render_swot_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    slide_info: dict[str, Any],
    bullets: list[str],
    style: dict[str, RGBColor],
) -> None:
    """渲染 SWOT 版式。

    :param prs: 演示文稿对象。
    :param slide_layout: 幻灯片布局。
    :param title: 标题。
    :param slide_info: 幻灯片数据。
    :param bullets: 要点列表。
    :param style: 样式配置。
    :return: None
    """
    quadrants = _resolve_swot_quadrants(slide_info, bullets)
    _render_quadrant_slide(prs, slide_layout, title, quadrants, style)


def _render_risk_matrix_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    slide_info: dict[str, Any],
    bullets: list[str],
    style: dict[str, RGBColor],
) -> None:
    """渲染风险矩阵版式。

    :param prs: 演示文稿对象。
    :param slide_layout: 幻灯片布局。
    :param title: 标题。
    :param slide_info: 幻灯片数据。
    :param bullets: 要点列表。
    :param style: 样式配置。
    :return: None
    """
    quadrants = _resolve_risk_matrix_quadrants(slide_info, bullets)
    _render_quadrant_slide(prs, slide_layout, title, quadrants, style, axis_labels=("影响", "概率"))


def _render_content_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    bullets: list[str],
    style: dict[str, RGBColor],
    title_suffix: str | None = None,
) -> None:
    """渲染单个内容页。

    :param prs: 演示文稿对象
    :param slide_layout: 幻灯片布局
    :param title: 标题
    :param bullets: 要点列表
    :param style: 样式配置
    :param title_suffix: 标题后缀
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)

    display_title = title if not title_suffix else f"{title}{title_suffix}"
    if slide.shapes.title:
        slide.shapes.title.text = display_title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(display_title),
            _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
        )

    if len(slide.placeholders) > 1:
        body_shape = slide.placeholders[1]
        text_frame = body_shape.text_frame
        _tune_text_frame(text_frame)
        if bullets:
            text_frame.text = bullets[0]
            for item in bullets[1:]:
                paragraph = text_frame.add_paragraph()
                paragraph.text = item
        else:
            text_frame.text = ""
        _apply_body_style(
            text_frame,
            style["body"],
            _body_font_size(len(bullets)),
            _resolve_font(style, "font", DEFAULT_FONT_NAME),
        )


def _render_image_left_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    bullets: list[str],
    style: dict[str, RGBColor],
) -> None:
    """渲染图左文右版式。

    :param prs: 演示文稿对象
    :param slide_layout: 幻灯片布局
    :param title: 标题
    :param bullets: 要点列表
    :param style: 样式配置
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
        )

    image_box = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.6), Inches(5.2), Inches(4.5)
    )
    image_box.fill.solid()
    image_box.fill.fore_color.rgb = style["accent"]
    image_box.line.fill.background()

    text_box = slide.shapes.add_textbox(Inches(6.2), Inches(1.6), Inches(6.5), Inches(4.5))
    text_frame = text_box.text_frame
    _tune_text_frame(text_frame)
    if bullets:
        text_frame.text = bullets[0]
        for item in bullets[1:]:
            paragraph = text_frame.add_paragraph()
            paragraph.text = item
    _apply_body_style(
        text_frame,
        style["body"],
        _body_font_size(len(bullets)),
        _resolve_font(style, "font", DEFAULT_FONT_NAME),
    )


def _render_image_right_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    bullets: list[str],
    style: dict[str, RGBColor],
) -> None:
    """渲染图右文左版式。

    :param prs: 演示文稿对象
    :param slide_layout: 幻灯片布局
    :param title: 标题
    :param bullets: 要点列表
    :param style: 样式配置
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
        )

    text_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(6.2), Inches(4.5))
    text_frame = text_box.text_frame
    _tune_text_frame(text_frame)
    if bullets:
        text_frame.text = bullets[0]
        for item in bullets[1:]:
            paragraph = text_frame.add_paragraph()
            paragraph.text = item
    _apply_body_style(
        text_frame,
        style["body"],
        _body_font_size(len(bullets)),
        _resolve_font(style, "font", DEFAULT_FONT_NAME),
    )

    image_box = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(7.1), Inches(1.6), Inches(5.2), Inches(4.5)
    )
    image_box.fill.solid()
    image_box.fill.fore_color.rgb = style["accent"]
    image_box.line.fill.background()


def _render_chart_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    bullets: list[str],
    style: dict[str, RGBColor],
    chart_data: dict[str, list[float]] | None = None,
    chart_type: str | None = None,
    chart_categories: list[str] | None = None,
) -> None:
    """渲染图表页版式。

    :param prs: 演示文稿对象
    :param slide_layout: 幻灯片布局
    :param title: 标题
    :param bullets: 要点列表
    :param style: 样式配置
    :param chart_data: 图表数据
    :param chart_type: 图表类型
    :param chart_categories: 图表类别
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
        )

    data = CategoryChartData()
    data.categories = chart_categories or ["Q1", "Q2", "Q3", "Q4"]
    series_data = chart_data or {
        "营收": [18, 24, 28, 35],
        "成本": [12, 14, 16, 18],
    }
    for name, values in series_data.items():
        data.add_series(name, values)

    chart_type_map = {
        "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
        "line": XL_CHART_TYPE.LINE,
        "stacked": XL_CHART_TYPE.COLUMN_STACKED,
        "stacked-100": XL_CHART_TYPE.COLUMN_STACKED_100,
        "area": XL_CHART_TYPE.AREA,
    }
    resolved_type = chart_type_map.get((chart_type or "column").lower(), XL_CHART_TYPE.COLUMN_CLUSTERED)

    chart_box = slide.shapes.add_chart(
        resolved_type,
        Inches(0.8),
        Inches(1.7),
        Inches(7.0),
        Inches(4.2),
        data,
    ).chart
    chart_box.has_legend = True
    chart_box.legend.include_in_layout = False
    if (chart_type or "").lower() == "multi-axis":
        for index, series in enumerate(chart_box.series):
            if index > 0:
                series.plot_on_secondary_axis = True

    text_box = slide.shapes.add_textbox(Inches(8.2), Inches(1.7), Inches(4.5), Inches(4.2))
    text_frame = text_box.text_frame
    _tune_text_frame(text_frame)
    if bullets:
        text_frame.text = bullets[0]
        for item in bullets[1:]:
            paragraph = text_frame.add_paragraph()
            paragraph.text = item
    _apply_body_style(
        text_frame,
        style["body"],
        _body_font_size(len(bullets)),
        _resolve_font(style, "font", DEFAULT_FONT_NAME),
    )


def _render_table_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    bullets: list[str],
    style: dict[str, RGBColor],
    table: dict[str, Any] | None = None,
) -> None:
    """渲染表格页版式。

    :param prs: 演示文稿对象
    :param slide_layout: 幻灯片布局
    :param title: 标题
    :param bullets: 要点列表
    :param style: 样式配置
    :param table: 表格数据
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    font_title = _resolve_font(style, "font_title", DEFAULT_FONT_NAME)
    font_body = _resolve_font(style, "font", DEFAULT_FONT_NAME)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            font_title,
        )

    headers = []
    rows: list[list[str]] = []
    table_style = None
    if isinstance(table, dict):
        headers = [str(item) for item in table.get("headers", []) if str(item).strip()]
        raw_rows = table.get("rows", [])
        if isinstance(raw_rows, list):
            for row in raw_rows:
                if isinstance(row, list):
                    rows.append([str(item) for item in row])
        table_style = str(table.get("style", "")).strip().lower() or None
    if not rows:
        rows = [["--", "--", "--"], ["--", "--", "--"]]
    col_count = max(len(headers), max(len(row) for row in rows))
    if col_count <= 0:
        col_count = 3
    row_count = len(rows) + (1 if headers else 0)

    table_shape = slide.shapes.add_table(
        row_count,
        col_count,
        Inches(0.7),
        Inches(1.6),
        Inches(7.2),
        Inches(4.6),
    )
    table_obj = table_shape.table

    body_text = style["body"]
    font_body = _resolve_font(style, "font", DEFAULT_FONT_NAME)
    font_title = _resolve_font(style, "font_title", DEFAULT_FONT_NAME)

    resolved_style = table_style or str(style.get("table_style", "")).strip().lower() or "striped"
    is_dark = _is_dark(style["bg"])
    base_bg = RGBColor(20, 26, 40) if is_dark else RGBColor(255, 255, 255)
    accent = style["accent"]
    if resolved_style == "contrast":
        header_bg = accent
        row_even = _mix_color(base_bg, accent, 0.22 if is_dark else 0.12)
        row_odd = base_bg
    elif resolved_style == "soft":
        header_bg = _mix_color(base_bg, accent, 0.18 if is_dark else 0.12)
        row_even = _mix_color(base_bg, accent, 0.10 if is_dark else 0.06)
        row_odd = base_bg
    else:
        header_bg = accent if not is_dark else _mix_color(base_bg, accent, 0.45)
        row_even = base_bg
        row_odd = _mix_color(base_bg, accent, 0.08 if not is_dark else 0.18)

    header_text = RGBColor(255, 255, 255) if _is_dark(header_bg) else style["title"]

    def _set_cell(cell, text: str, bold: bool, color: RGBColor, font_name: str) -> None:
        cell.text = text
        tf = cell.text_frame
        _tune_text_frame(tf)
        for paragraph in tf.paragraphs:
            paragraph.font.name = font_name
            paragraph.font.size = Pt(12)
            paragraph.font.bold = bold
            for run in paragraph.runs:
                run.font.name = font_name
                run.font.size = Pt(12)
                run.font.bold = bold
                run.font.color.rgb = color
                _set_east_asia_font(run, font_name)

    if headers:
        for col in range(col_count):
            cell = table_obj.cell(0, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_bg
            text = headers[col] if col < len(headers) else ""
            _set_cell(cell, text, True, header_text, font_title)

    for row_idx, row in enumerate(rows):
        target_row = row_idx + (1 if headers else 0)
        for col in range(col_count):
            cell = table_obj.cell(target_row, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = row_odd if (row_idx % 2 == 1) else row_even
            text = row[col] if col < len(row) else ""
            _set_cell(cell, text, False, body_text, font_body)

    if bullets:
        text_box = slide.shapes.add_textbox(Inches(8.2), Inches(1.7), Inches(4.5), Inches(4.2))
        text_frame = text_box.text_frame
        _tune_text_frame(text_frame)
        text_frame.text = bullets[0]
        for item in bullets[1:]:
            paragraph = text_frame.add_paragraph()
            paragraph.text = item
        _apply_body_style(
            text_frame,
            style["body"],
            _body_font_size(len(bullets)),
            _resolve_font(style, "font", DEFAULT_FONT_NAME),
        )


def _render_icon_grid_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    icons: list[dict[str, Any]],
    style: dict[str, RGBColor],
) -> None:
    """渲染图标卡片网格。

    :param prs: 演示文稿对象
    :param slide_layout: 幻灯片布局
    :param title: 标题
    :param icons: 图标数据
    :param style: 样式配置
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    font_title = _resolve_font(style, "font_title", DEFAULT_FONT_NAME)
    font_body = _resolve_font(style, "font", DEFAULT_FONT_NAME)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            font_title,
        )

    items = icons[:6] if icons else []
    if not items:
        items = [
            {"label": "指标 A", "value": "—", "badge": "A"},
            {"label": "指标 B", "value": "—", "badge": "B"},
            {"label": "指标 C", "value": "—", "badge": "C"},
            {"label": "指标 D", "value": "—", "badge": "D"},
        ]

    columns = 2 if len(items) <= 4 else 3
    rows = (len(items) + columns - 1) // columns
    left = Inches(0.8)
    top = Inches(1.7)
    available_w = Inches(12.0)
    available_h = Inches(4.6)
    gap = Inches(0.3)
    card_w = (available_w - gap * (columns - 1)) / columns
    card_h = (available_h - gap * (rows - 1)) / rows

    card_fill = RGBColor(255, 255, 255) if not _is_dark(style["bg"]) else RGBColor(20, 26, 40)

    for idx, item in enumerate(items):
        row = idx // columns
        col = idx % columns
        x = left + col * (card_w + gap)
        y = top + row * (card_h + gap)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = card_fill
        card.line.color.rgb = style["accent"]
        card.line.width = Pt(1)

        badge = str(item.get("badge") or "")[:2] or (str(item.get("label") or "")[:1] or "")
        icon = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.25), y + Inches(0.25), Inches(0.45), Inches(0.45))
        icon.fill.solid()
        icon.fill.fore_color.rgb = style["accent"]
        icon.line.fill.background()

        icon_text = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.25), Inches(0.45), Inches(0.45))
        tf = icon_text.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = badge.upper()
        _apply_paragraph_style(p, RGBColor(255, 255, 255), 10, True, font_title)
        p.alignment = PP_ALIGN.CENTER

        label = slide.shapes.add_textbox(x + Inches(0.85), y + Inches(0.22), card_w - Inches(1.1), Inches(0.4))
        tf_label = label.text_frame
        tf_label.clear()
        p_label = tf_label.paragraphs[0]
        p_label.text = str(item.get("label", ""))
        _apply_paragraph_style(p_label, style["body"], 12, False, font_body)

        value = slide.shapes.add_textbox(x + Inches(0.85), y + Inches(0.62), card_w - Inches(1.1), Inches(0.6))
        tf_value = value.text_frame
        tf_value.clear()
        p_value = tf_value.paragraphs[0]
        p_value.text = str(item.get("value", ""))
        _apply_paragraph_style(p_value, style["title"], 20, True, font_title)


def _render_timeline_slide(
    prs: Presentation,
    slide_layout,
    title: str,
    bullets: list[str],
    style: dict[str, RGBColor],
) -> None:
    """渲染时间线页版式。

    :param prs: 演示文稿对象
    :param slide_layout: 幻灯片布局
    :param title: 标题
    :param bullets: 要点列表
    :param style: 样式配置
    :return: None
    """
    slide = prs.slides.add_slide(slide_layout)
    _set_slide_background(slide, style["bg"])
    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
    if slide.shapes.title:
        slide.shapes.title.text = title
        _apply_title_style(
            slide.shapes.title,
            style["title"],
            _title_font_size(title),
            _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
        )

    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(3.2), Inches(11.6), Inches(0.1)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = style["accent"]
    line.line.fill.background()

    step_count = max(2, min(5, len(bullets)))
    for index in range(step_count):
        left = Inches(1.2 + index * 2.4)
        node = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, Inches(2.9), Inches(0.6), Inches(0.6))
        node.fill.solid()
        node.fill.fore_color.rgb = style["accent"]
        node.line.fill.background()

    text_box = slide.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(11.6), Inches(2.0))
    text_frame = text_box.text_frame
    _tune_text_frame(text_frame)
    for item in bullets[:5]:
        paragraph = text_frame.add_paragraph()
        paragraph.text = item
    _apply_body_style(
        text_frame,
        style["body"],
        _body_font_size(len(bullets)),
        _resolve_font(style, "font", DEFAULT_FONT_NAME),
    )

def build_presentation(
    slides_data: list[dict[str, Any]],
    output_path: str | None = None,
    template_name: str | None = None,
    theme_hint: str | None = None,
    auto_layout: bool = True,
    prefer_image_layout: bool = True,
    max_bullets_per_slide: int = 5,
    max_paragraph_chars: int = 220,
) -> None:
    """根据模板生成 PPTX。

    :param slides_data: 幻灯片数据列表
    :param output_path: 输出文件路径（为空则自动按标题命名）
    :param template_name: 模板名称（可为空，自动选择）
    :param theme_hint: 主题提示文本
    :param auto_layout: 是否自动推断版式。
    :param prefer_image_layout: 是否优先使用图片版式。
    :param max_bullets_per_slide: 每页最大要点数量
    :param max_paragraph_chars: 长段落拆分阈值
    :return: None
    """
    resolved_template = template_name or _resolve_template_name(slides_data, theme_hint)
    template_path = _resolve_template_path(resolved_template)
    prs = Presentation(template_path)
    _clear_slides(prs)

    style = TEMPLATE_STYLES.get(resolved_template, TEMPLATE_STYLES["minimal-business"])
    resolved_output = _resolve_output_path(output_path, slides_data)

    total_slides = len(slides_data)

    for index, slide_info in enumerate(slides_data):
        layout_index = int(slide_info.get("layout", 1))
        slide_layout = prs.slide_layouts[layout_index]
        title = str(slide_info.get("title", ""))
        content = slide_info.get("content", "")
        layout_type = str(slide_info.get("layout_type", "")).lower().strip()
        if auto_layout and not layout_type:
            layout_type = _infer_layout_type(
                slide_info,
                slide_index=index,
                total_slides=total_slides,
                prefer_image=prefer_image_layout,
            )
        chart_data = slide_info.get("chart_data")
        chart_type = slide_info.get("chart_type")
        chart_categories = slide_info.get("chart_categories")
        table_data = slide_info.get("table")
        icons = slide_info.get("icons")
        schema = _resolve_layout_schema(layout_type, max_bullets_per_slide, max_paragraph_chars)

        if layout_index == 1 and isinstance(content, list):
            bullets = _normalize_bullets(content, max_bullets=schema["max_bullets"] * 3)
            if layout_type == "table":
                _render_table_slide(prs, slide_layout, title, bullets, style, table_data)
                continue
            if layout_type == "icon-grid":
                icon_items = icons if isinstance(icons, list) else []
                _render_icon_grid_slide(prs, slide_layout, title, icon_items, style)
                continue
            chunks = _chunk_bullets(bullets, schema["max_bullets"])
            for index, chunk in enumerate(chunks):
                suffix = f"(continued {index + 1})" if index > 0 else None
                display_title = title if not suffix else f"{title}{suffix}"
                if layout_type == "image-left":
                    _render_image_left_slide(prs, slide_layout, display_title, chunk, style)
                elif layout_type == "image-right":
                    _render_image_right_slide(prs, slide_layout, display_title, chunk, style)
                elif layout_type == "comparison":
                    left_title, left_items, right_title, right_items = _resolve_comparison_columns(slide_info, chunk)
                    _render_comparison_slide(
                        prs, slide_layout, display_title, left_title, left_items, right_title, right_items, style
                    )
                elif layout_type == "pros-cons":
                    pros_items, cons_items = _resolve_pros_cons(slide_info, chunk)
                    _render_comparison_slide(
                        prs, slide_layout, display_title, "优势", pros_items, "劣势", cons_items, style
                    )
                elif layout_type == "swot":
                    _render_swot_slide(prs, slide_layout, display_title, slide_info, chunk, style)
                elif layout_type == "risk-matrix":
                    _render_risk_matrix_slide(prs, slide_layout, display_title, slide_info, chunk, style)
                elif layout_type in ("matrix-2x2", "four-quadrant"):
                    quadrants = _resolve_generic_quadrants(slide_info, chunk, layout_type)
                    _render_quadrant_slide(prs, slide_layout, display_title, quadrants, style)
                elif layout_type == "chart":
                    _render_chart_slide(
                        prs,
                        slide_layout,
                        display_title,
                        chunk,
                        style,
                        chart_data,
                        chart_type,
                        chart_categories,
                    )
                elif layout_type == "timeline":
                    _render_timeline_slide(prs, slide_layout, display_title, chunk, style)
                else:
                    _render_content_slide(prs, slide_layout, title, chunk, style, suffix)
            continue

        if not isinstance(content, list):
            paragraphs = _split_long_paragraph(str(content), max_chars=schema["max_paragraph_chars"])
            if len(paragraphs) > 1:
                for index, part in enumerate(paragraphs):
                    heading = part.get("heading", "")
                    suffix = f"(continued {index + 1})" if index > 0 else None
                    slide = prs.slides.add_slide(slide_layout)
                    _set_slide_background(slide, style["bg"])
                    _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
                    if slide.shapes.title:
                        display_title = title if not suffix else f"{title}{suffix}"
                        if heading:
                            display_title = f"{display_title} · {heading}"
                        slide.shapes.title.text = display_title
                        _apply_title_style(
                            slide.shapes.title,
                            style["title"],
                            _title_font_size(display_title),
                            _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
                        )
                    if len(slide.placeholders) > 1:
                        text_frame = slide.placeholders[1].text_frame
                        _tune_text_frame(text_frame)
                        text_frame.text = part.get("text", "")
                        _apply_body_style(
                            text_frame,
                            style["body"],
                            _body_font_size(3),
                            _resolve_font(style, "font", DEFAULT_FONT_NAME),
                        )
                continue

        slide = prs.slides.add_slide(slide_layout)
        _set_slide_background(slide, style["bg"])
        _add_accent_bar(slide, style["accent"], y_inch=0.0, height_inch=0.12)
        if slide.shapes.title:
            slide.shapes.title.text = title
            _apply_title_style(
                slide.shapes.title,
                style["title"],
                _title_font_size(title),
                _resolve_font(style, "font_title", DEFAULT_FONT_NAME),
            )

        if len(slide.placeholders) > 1:
            body_shape = slide.placeholders[1]
            if isinstance(content, list):
                bullets = _normalize_bullets(content)
                text_frame = body_shape.text_frame
                _tune_text_frame(text_frame)
                if bullets:
                    text_frame.text = bullets[0]
                    for item in bullets[1:]:
                        paragraph = text_frame.add_paragraph()
                        paragraph.text = item
                else:
                    text_frame.text = ""
                _apply_body_style(
                    text_frame,
                    style["body"],
                    _body_font_size(len(bullets)),
                    _resolve_font(style, "font", DEFAULT_FONT_NAME),
                )
            else:
                text_frame = body_shape.text_frame
                _tune_text_frame(text_frame)
                text_frame.text = str(content)
                _apply_body_style(
                    text_frame,
                    style["body"],
                    _body_font_size(3),
                    _resolve_font(style, "font", DEFAULT_FONT_NAME),
                )

    try:
        prs.save(resolved_output)
        print(f"成功生成演示文稿: {resolved_output}")
    except PermissionError:
        print(f"错误: 无法保存文件。请确保 {resolved_output} 未被其他程序打开。")


def _resolve_output_path(output_path: str | None, slides_data: list[dict[str, Any]]) -> str:
    """根据标题生成输出文件名。

    :param output_path: 输出路径
    :param slides_data: 幻灯片数据列表
    :return: 输出文件路径
    """
    if output_path:
        return output_path
    title = "presentation"
    if slides_data:
        title = str(slides_data[0].get("title", "")).strip() or title
    safe = _sanitize_filename(title)
    return f"{safe}.pptx"


def _sanitize_filename(text: str) -> str:
    """清理文件名中的非法字符。

    :param text: 原始文本
    :return: 安全文本
    """
    invalid = '<>:"/\\\\|?*'
    cleaned = "".join("_" if ch in invalid else ch for ch in text)
    cleaned = cleaned.strip().strip(".")
    return cleaned or "presentation"


def build_demo_slides_data() -> list[dict[str, Any]]:
    """生成示例幻灯片数据用于演示结构。

    :return: 幻灯片数据列表
    """
    # 幻灯片大纲：
    # 1. AI 产品落地路线图（封面）
    # 2. 目标与边界
    # 3. 关键里程碑
    # 4. 资源与风险
    # 5. 总结与行动（结束页）
    return [
        {
            "layout": 0,
            "title": "AI 产品落地路线图",
            "content": "从试点到规模化的执行框架\n汇报人：AI Assistant",
        },
        {
            "layout": 1,
            "layout_type": "image-left",
            "title": "场景画像",
            "content": [
                "聚焦高频、可量化的业务痛点。",
                "明确数据源与责任人。",
                "先做最小可行范围验证价值。",
            ],
        },
        {
            "layout": 1,
            "title": "目标与边界",
            "content": [
                "明确业务价值与可衡量指标。",
                "锁定首批高频场景作为切入口。",
                "定义可控范围，避免范围蔓延。",
                "建立数据与安全合规底线。",
            ],
        },
        {
            "layout": 1,
            "title": "关键里程碑",
            "content": [
                "第 1 个月：需求梳理与 PoC 验证。",
                "第 2-3 个月：核心流程试点上线。",
                "第 4-6 个月：规模化复用与运营优化。",
            ],
        },
        {
            "layout": 1,
            "layout_type": "chart",
            "title": "指标趋势",
            "content": [
                "效率提升：平均处理时长降低 30%。",
                "质量提升：错误率下降 20%。",
                "成本优化：人工投入减少 15%。",
            ],
            "chart_type": "line",
            "chart_data": {
                "营收": [18, 24, 28, 35],
                "成本": [12, 14, 16, 18],
            },
        },
        {
            "layout": 1,
            "title": "资源与风险",
            "content": [
                "资源：产品、数据、工程、运营协同。",
                "风险：数据质量、模型偏差、变更成本。",
                "对策：建立监控与快速回滚机制。",
            ],
        },
        {
            "layout": 1,
            "layout_type": "timeline",
            "title": "阶段推进",
            "content": [
                "探索与定位",
                "验证与试点",
                "规模化落地",
                "持续优化",
            ],
        },
        {
            "layout": 0,
            "title": "总结与行动",
            "content": "先小步验证，再快速复制，持续沉淀标准化能力。",
        },
    ]


def main() -> None:
    """生成示例演示文稿文件。

    :return: None
    """
    slides_data = build_demo_slides_data()
    build_presentation(slides_data, theme_hint="AI 产品", max_bullets_per_slide=5)


if __name__ == "__main__":
    main()
DEFAULT_FONT_NAME = "微软雅黑"
