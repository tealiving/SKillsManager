"""
根据 JSON 结构生成 PPTX。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pptx_template_renderer import build_presentation


def _load_json(path: Path) -> dict[str, Any]:
    """读取 JSON 文件。

    :param path: JSON 文件路径。
    :return: 解析后的字典。
    """
    if not path.exists():
        raise FileNotFoundError(f"未找到输入文件: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_list(value: Any) -> list[str]:
    """规范化列表字段。

    :param value: 原始输入。
    :return: 字符串列表。
    """
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _join_lines(lines: list[str]) -> str:
    """拼接多行文本。

    :param lines: 文本列表。
    :return: 拼接后的字符串。
    """
    cleaned = [line.strip() for line in lines if line and str(line).strip()]
    return "\n".join(cleaned)


def _slide_type(slide: dict[str, Any]) -> str:
    """解析幻灯片类型。

    :param slide: 幻灯片字典。
    :return: 归一化的类型文本。
    """
    return str(slide.get("type", "content")).lower().strip()


def _has_slide_type(slides: list[dict[str, Any]], types: set[str]) -> bool:
    """判断是否包含指定类型。

    :param slides: 幻灯片列表。
    :param types: 类型集合。
    :return: True 表示已存在。
    """
    for slide in slides:
        if _slide_type(slide) in types:
            return True
    return False


def _read_section(slide: dict[str, Any]) -> str:
    """读取幻灯片所属章节。

    :param slide: 幻灯片字典。
    :return: 章节标题（可为空）。
    """
    raw = slide.get("section") or slide.get("section_title") or slide.get("chapter")
    return str(raw).strip() if raw is not None else ""


def _collect_section_items(slides: list[dict[str, Any]]) -> list[str]:
    """收集目录/章节项标题。

    :param slides: 幻灯片列表。
    :return: 目录项标题列表。
    """
    items: list[str] = []
    for slide in slides:
        slide_type = _slide_type(slide)
        if slide_type in ("section", "divider"):
            title = str(slide.get("title", "")).strip()
            if title and (not items or items[-1] != title):
                items.append(title)
            continue
        section = _read_section(slide)
        if section and (not items or items[-1] != section):
            items.append(section)
    return items


def _auto_insert_sections(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """根据 section 字段自动插入章节页。

    :param slides: 幻灯片列表。
    :return: 处理后的幻灯片列表。
    """
    if _has_slide_type(slides, {"section", "divider"}):
        return slides
    result: list[dict[str, Any]] = []
    current_section = ""
    for slide in slides:
        slide_type = _slide_type(slide)
        if slide_type in ("title", "cover"):
            result.append(slide)
            continue
        section = _read_section(slide)
        if section and section != current_section:
            subtitle = str(slide.get("section_subtitle", "")).strip()
            section_slide = {"type": "section", "title": section, "subtitle": subtitle}
            result.append(section_slide)
            current_section = section
        result.append(slide)
    return result


def _auto_insert_agenda(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """自动插入目录页。

    :param slides: 幻灯片列表。
    :return: 处理后的幻灯片列表。
    """
    if _has_slide_type(slides, {"agenda", "toc", "directory"}):
        return slides
    items = _collect_section_items(slides)
    if not items:
        titles: list[str] = []
        for slide in slides:
            slide_type = _slide_type(slide)
            if slide_type in ("title", "cover", "section", "divider", "closing", "end", "thanks"):
                continue
            title = str(slide.get("title", "")).strip()
            if title and title not in titles:
                titles.append(title)
            if len(titles) >= 7:
                break
        items = titles
    if not items:
        return slides
    agenda_slide = {"type": "agenda", "title": "目录", "items": items}
    insert_at = 0
    for index, slide in enumerate(slides):
        if _slide_type(slide) in ("title", "cover"):
            insert_at = index + 1
            break
    return slides[:insert_at] + [agenda_slide] + slides[insert_at:]


def _prepare_slides(slides: list[Any], meta: dict[str, Any]) -> list[dict[str, Any]]:
    """预处理自动生成逻辑。

    :param slides: 原始 slides 列表。
    :param meta: meta 字典。
    :return: 处理后的 slides 列表。
    """
    normalized = [slide for slide in slides if isinstance(slide, dict)]
    auto_sections = meta.get("auto_sections", True)
    auto_agenda = meta.get("auto_agenda", True)
    if auto_sections:
        normalized = _auto_insert_sections(normalized)
    if auto_agenda:
        normalized = _auto_insert_agenda(normalized)
    return normalized


def _resolve_chart(chart: dict[str, Any]) -> tuple[str | None, dict[str, list[float]] | None, list[str] | None]:
    """解析图表数据。

    :param chart: 图表字段。
    :return: (chart_type, chart_data, chart_categories)
    """
    chart_type = str(chart.get("type", "")).strip() or None
    categories = chart.get("categories")
    chart_categories = [str(item) for item in categories] if isinstance(categories, list) else None

    series = chart.get("series")
    chart_data: dict[str, list[float]] = {}
    if isinstance(series, list):
        for item in series:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            values = item.get("values")
            if not name or not isinstance(values, list):
                continue
            chart_data[name] = [float(v) for v in values]
    elif isinstance(series, dict):
        for key, values in series.items():
            if isinstance(values, list):
                chart_data[str(key)] = [float(v) for v in values]

    if not chart_data:
        return chart_type, None, chart_categories
    return chart_type, chart_data, chart_categories


def _build_slides_data(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """将 JSON 数据转换为 slides_data。

    :param payload: JSON 字典。
    :return: slides_data 列表。
    """
    meta = payload.get("meta", {}) if isinstance(payload.get("meta"), dict) else {}
    raw_slides = payload.get("slides", [])
    if not isinstance(raw_slides, list):
        raise ValueError("slides 必须为列表。")

    slides = _prepare_slides(raw_slides, meta)
    slides_data: list[dict[str, Any]] = []

    for slide in slides:
        if not isinstance(slide, dict):
            continue
        slide_type = str(slide.get("type", "content")).lower().strip()
        title = str(slide.get("title") or meta.get("title", "")).strip()
        layout_type = str(slide.get("layout_type", "")).strip()

        if slide_type in ("title", "cover"):
            subtitle = str(slide.get("subtitle") or meta.get("subtitle", "")).strip()
            tagline = str(slide.get("tagline", "")).strip()
            meta_line = str(slide.get("meta") or meta.get("author", "")).strip()
            content = _join_lines([subtitle, tagline, meta_line])
            slides_data.append({"layout": 0, "title": title, "content": content})
            continue

        if slide_type in ("section", "divider"):
            subtitle = str(slide.get("subtitle", "")).strip()
            slides_data.append({"layout": 0, "title": title, "content": subtitle})
            continue

        if slide_type in ("agenda", "toc", "directory"):
            items = _normalize_list(slide.get("items") or slide.get("bullets"))
            slides_data.append({"layout": 1, "title": title or "目录", "content": items})
            continue

        if slide_type in ("timeline", "roadmap"):
            items = _normalize_list(slide.get("items") or slide.get("bullets"))
            slides_data.append(
                {
                    "layout": 1,
                    "title": title or "里程碑",
                    "content": items,
                    "layout_type": "timeline",
                }
            )
            continue

        if slide_type in ("chart", "data"):
            chart = slide.get("chart") if isinstance(slide.get("chart"), dict) else {}
            chart_type, chart_data, chart_categories = _resolve_chart(chart)
            bullets = _normalize_list(slide.get("bullets") or slide.get("items"))
            slide_info: dict[str, Any] = {
                "layout": 1,
                "title": title,
                "content": bullets,
                "layout_type": "chart",
                "chart_type": chart_type,
                "chart_data": chart_data,
            }
            if chart_categories:
                slide_info["chart_categories"] = chart_categories
            slides_data.append(slide_info)
            continue

        if slide_type == "table":
            bullets = _normalize_list(slide.get("bullets") or slide.get("items"))
            table = slide.get("table") if isinstance(slide.get("table"), dict) else {}
            slides_data.append(
                {
                    "layout": 1,
                    "title": title,
                    "content": bullets,
                    "layout_type": "table",
                    "table": table,
                }
            )
            continue

        if slide_type == "icon-grid":
            icons = slide.get("icons") if isinstance(slide.get("icons"), list) else []
            slides_data.append(
                {
                    "layout": 1,
                    "title": title,
                    "content": [],
                    "layout_type": "icon-grid",
                    "icons": icons,
                }
            )
            continue

        content = _normalize_list(slide.get("bullets") or slide.get("items") or slide.get("content"))
        if slide_type in (
            "comparison",
            "pros-cons",
            "swot",
            "risk-matrix",
            "matrix-2x2",
            "four-quadrant",
            "table",
            "icon-grid",
            "image-left",
            "image-right",
        ):
            layout_type = slide_type
        slide_info = {"layout": 1, "title": title, "content": content}
        if layout_type:
            slide_info["layout_type"] = layout_type

        passthrough_keys = [
            "columns",
            "column_titles",
            "pros",
            "cons",
            "swot",
            "risks",
            "quadrants",
            "axis_labels",
        ]
        for key in passthrough_keys:
            if key in slide:
                slide_info[key] = slide[key]
        slides_data.append(slide_info)

    return slides_data


def main() -> None:
    """脚本入口。

    :return: None
    """
    parser = argparse.ArgumentParser(description="JSON -> PPTX (template renderer)")
    parser.add_argument("--input", "-i", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", default="", help="输出 PPTX 文件路径")
    parser.add_argument("--theme", default="", help="主题提示词或模板名")
    parser.add_argument("--template", default="", help="模板文件名或路径")
    parser.add_argument("--max-bullets", type=int, default=5, help="每页最大要点数")
    parser.add_argument("--max-paragraph-chars", type=int, default=220, help="长段落拆分阈值")
    args = parser.parse_args()

    payload = _load_json(Path(args.input))
    meta = payload.get("meta", {}) if isinstance(payload.get("meta"), dict) else {}
    slides_data = _build_slides_data(payload)
    if not slides_data:
        raise ValueError("slides 为空，无法生成 PPTX。")

    output = args.output or str(meta.get("output", "")) or None
    theme_hint = args.theme or str(meta.get("theme", "")).strip() or None
    template_name = args.template or str(meta.get("template", "")).strip() or None

    build_presentation(
        slides_data,
        output_path=output,
        template_name=template_name if template_name else None,
        theme_hint=theme_hint,
        max_bullets_per_slide=args.max_bullets,
        max_paragraph_chars=args.max_paragraph_chars,
    )


if __name__ == "__main__":
    main()
