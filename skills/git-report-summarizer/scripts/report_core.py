"""提交汇总核心逻辑。"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from typing import Dict, Iterable, List, Tuple


NOISE_KEYWORDS = ("wip", "merge", "format", "typo", "test", "chore")
CONVENTIONAL_PREFIX_PATTERN = re.compile(
    r"^(feat|fix|chore|refactor|docs|test|build|ci|style|perf)(\([^)]+\))?:\s*",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class CommitRecord:
    """提交记录模型。"""

    repo: str
    commit_id: str
    author_name: str
    author_email: str
    committed_at: datetime
    message: str
    is_merge: bool


def resolve_time_window(
    period: str,
    base_date: datetime | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> Tuple[datetime, datetime]:
    """解析汇报时间窗口。

    :param period: 周期类型，支持 daily、weekly、monthly、custom。
    :param base_date: 基准时间，不传则使用当前时间。
    :param since: 自定义开始时间，仅 custom 周期使用。
    :param until: 自定义结束时间，仅 custom 周期使用。
    :return: 开始时间与结束时间元组，结束时间为开区间。
    """
    now = base_date or datetime.now()
    day_start = datetime(now.year, now.month, now.day)
    if period == "daily":
        return day_start, day_start + timedelta(days=1)
    if period == "weekly":
        week_start = day_start - timedelta(days=day_start.weekday())
        return week_start, week_start + timedelta(days=7)
    if period == "monthly":
        month_start = datetime(day_start.year, day_start.month, 1)
        if day_start.month == 12:
            next_month = datetime(day_start.year + 1, 1, 1)
        else:
            next_month = datetime(day_start.year, day_start.month + 1, 1)
        return month_start, next_month
    if period == "custom":
        if since is None or until is None:
            raise ValueError("custom 周期必须同时提供 since 与 until。")
        return since, until
    raise ValueError(f"不支持的周期类型: {period}")


def is_noise_commit(message: str, is_merge: bool) -> bool:
    """判定提交是否属于噪声。

    :param message: 提交信息。
    :param is_merge: 是否为合并提交。
    :return: 若为噪声提交返回 True，否则返回 False。
    """
    normalized = message.strip().lower()
    if is_merge:
        return True
    return normalized in NOISE_KEYWORDS or any(
        normalized.startswith(prefix) for prefix in ("merge ", "wip ")
    )


def filter_and_normalize_commits(
    commits: Iterable[CommitRecord],
) -> Tuple[List[CommitRecord], int]:
    """过滤噪声提交并返回保留记录。

    :param commits: 原始提交序列。
    :return: 保留提交列表与被过滤数量。
    """
    kept: List[CommitRecord] = []
    filtered_count = 0
    for item in commits:
        if is_noise_commit(item.message, item.is_merge):
            filtered_count += 1
            continue
        kept.append(item)
    return kept, filtered_count


def aggregate_commits(commits: Iterable[CommitRecord]) -> Dict[str, List[str]]:
    """按仓库聚合提交信息。

    :param commits: 提交序列。
    :return: 以仓库名为键、提交消息列表为值的映射。
    """
    grouped: "OrderedDict[str, List[str]]" = OrderedDict()
    for item in sorted(commits, key=lambda record: (record.repo, record.committed_at)):
        grouped.setdefault(item.repo, []).append(item.message.strip())
    return dict(grouped)


def aggregate_repo_daily_commits(
    commits: Iterable[CommitRecord],
) -> Dict[str, Dict[str, List[str]]]:
    """按仓库与日期聚合提交信息。

    :param commits: 提交序列。
    :return: 二级映射，第一层为仓库，第二层为日期（YYYY-MM-DD）。
    """
    grouped: "OrderedDict[str, OrderedDict[str, List[str]]]" = OrderedDict()
    for item in sorted(commits, key=lambda record: (record.repo, record.committed_at)):
        repo_map = grouped.setdefault(item.repo, OrderedDict())
        day_key = item.committed_at.strftime("%Y-%m-%d")
        repo_map.setdefault(day_key, []).append(item.message.strip())
    return {repo: dict(day_map) for repo, day_map in grouped.items()}


def _clean_fragment_text(fragment: str) -> str:
    """清洗提交片段文本。

    :param fragment: 原始片段文本。
    :return: 清洗后的文本。
    """
    text = fragment.replace("\\", " ").replace("\n", " ").strip()
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r'^(git\s+commit\s+-m\s+)', "", text, flags=re.IGNORECASE)
    text = text.strip('"').strip("'").strip()
    text = CONVENTIONAL_PREFIX_PATTERN.sub("", text)
    text = re.sub(r"^\d+[\.、:：]\s*", "", text)
    text = re.sub(r"\s*([，。；：,:;])\s*", r"\1", text)
    text = re.sub(r"\s*([/\-])\s*", r"\1", text)
    return text.strip()


def _extract_fragments(message: str) -> List[str]:
    """提取提交消息中的候选片段。

    :param message: 原始提交消息。
    :return: 候选片段列表。
    """
    quoted = re.findall(r'-m\s+"([^"]+)"', message)
    if quoted:
        return quoted
    return [message]


def _compress_fragment(text: str, max_length: int = 36) -> str:
    """压缩片段文本长度，提升可读性。

    :param text: 原始文本。
    :param max_length: 允许最大长度。
    :return: 压缩后的文本。
    """
    normalized = text.strip()
    if len(normalized) <= max_length:
        return normalized
    clauses = [item.strip() for item in re.split(r"[，,:：]", normalized) if item.strip()]
    if len(clauses) >= 2:
        candidate = "，".join(clauses[:2])
        if len(candidate) <= max_length + 8:
            return candidate
    return normalized[:max_length].rstrip("，,:： ") + "…"


def summarize_commit_message(message: str, max_items: int = 3) -> List[str]:
    """从提交消息中提炼工作摘要条目。

    :param message: 原始提交消息。
    :param max_items: 最大条目数。
    :return: 摘要条目列表。
    """
    items: List[str] = []
    for fragment in _extract_fragments(message):
        split_items = re.split(r"(?:\s+\d+[\.、]\s+|[；;。])", fragment)
        for raw_item in split_items:
            cleaned = _clean_fragment_text(raw_item)
            if not cleaned:
                continue
            if cleaned.lower() in NOISE_KEYWORDS:
                continue
            compressed = _compress_fragment(cleaned)
            if compressed not in items:
                items.append(compressed)
            if len(items) >= max_items:
                return items
    if not items:
        fallback = _clean_fragment_text(message)
        if fallback:
            items.append(_compress_fragment(fallback))
    return items


def aggregate_summarized_commits(
    commits: Iterable[CommitRecord],
) -> Dict[str, List[str]]:
    """按仓库聚合摘要后的提交条目。

    :param commits: 提交序列。
    :return: 仓库与摘要条目映射。
    """
    grouped: "OrderedDict[str, List[str]]" = OrderedDict()
    for item in sorted(commits, key=lambda record: (record.repo, record.committed_at)):
        summary_items = summarize_commit_message(item.message)
        repo_items = grouped.setdefault(item.repo, [])
        for summary in summary_items:
            if summary not in repo_items:
                repo_items.append(summary)
    return dict(grouped)


def aggregate_repo_daily_summary_commits(
    commits: Iterable[CommitRecord],
) -> Dict[str, Dict[str, List[str]]]:
    """按仓库与日期聚合摘要条目。

    :param commits: 提交序列。
    :return: 二级映射，第一层仓库，第二层日期，值为摘要条目列表。
    """
    grouped: "OrderedDict[str, OrderedDict[str, List[str]]]" = OrderedDict()
    for item in sorted(commits, key=lambda record: (record.repo, record.committed_at)):
        repo_map = grouped.setdefault(item.repo, OrderedDict())
        day_key = item.committed_at.strftime("%Y-%m-%d")
        daily_items = repo_map.setdefault(day_key, [])
        for summary in summarize_commit_message(item.message):
            if summary not in daily_items:
                daily_items.append(summary)
    return {repo: dict(day_map) for repo, day_map in grouped.items()}


def format_repo_daily_details(
    repo_daily_items: Dict[str, Dict[str, List[str]]],
) -> str:
    """格式化仓库按天明细文本。

    :param repo_daily_items: 仓库-日期-事项映射。
    :return: Markdown 明细文本。
    """
    if not repo_daily_items:
        return "- 无"
    sections: List[str] = []
    for repo, day_map in repo_daily_items.items():
        sections.append(f"### {repo}")
        for day_text, items in day_map.items():
            sections.append(f"- {day_text}")
            for item in items:
                sections.append(f"  - {item}")
    return "\n".join(sections)


def format_daily_table(repo_daily_items: Dict[str, Dict[str, List[str]]]) -> str:
    """格式化仓库按天表格文本。

    :param repo_daily_items: 仓库-日期-事项映射。
    :return: Markdown 表格文本。
    """
    header = "| 日期 | 仓库 | 工作内容 |\n|---|---|---|"
    rows: List[str] = []
    for repo, day_map in repo_daily_items.items():
        for day_text, items in day_map.items():
            joined = "<br>".join(items) if items else "无"
            rows.append(f"| {day_text} | {repo} | {joined} |")
    if not rows:
        return f"{header}\n| - | - | 无 |"
    return f"{header}\n" + "\n".join(rows)


def format_period_overview(
    repo_daily_items: Dict[str, Dict[str, List[str]]],
    max_items_per_repo: int = 3,
) -> str:
    """格式化周期总结文本。

    :param repo_daily_items: 仓库-日期-事项映射。
    :param max_items_per_repo: 每个仓库保留的重点条目数。
    :return: Markdown 周期总结文本。
    """
    if not repo_daily_items:
        return "- 无"
    lines: List[str] = []
    for repo, day_map in repo_daily_items.items():
        merged_items: List[str] = []
        for items in day_map.values():
            for item in items:
                if item not in merged_items:
                    merged_items.append(item)
        selected = merged_items[:max_items_per_repo]
        if not selected:
            lines.append(f"- [{repo}] 本周期无有效提交")
            continue
        lines.append(f"- [{repo}] 重点完成：{'；'.join(selected)}")
    return "\n".join(lines)


def _period_title(period: str) -> str:
    """生成周期标题文本。

    :param period: 周期类型。
    :return: 对应的人类可读标题。
    """
    mapping = {
        "daily": "今日日报",
        "weekly": "本周周报",
        "monthly": "本月月报",
        "custom": "自定义汇报",
    }
    return mapping.get(period, "工作汇报")


def _format_completed_items(grouped_items: Dict[str, List[str]]) -> str:
    """格式化已完成事项列表。

    :param grouped_items: 仓库与消息列表映射。
    :return: Markdown 列表文本。
    """
    lines: List[str] = []
    for repo, items in grouped_items.items():
        for text in items:
            lines.append(f"- [{repo}] {text}")
    return "\n".join(lines) if lines else "- 无"


def _format_failed_repos(failed_repos: Iterable[str]) -> str:
    """格式化失败仓库列表。

    :param failed_repos: 失败仓库序列。
    :return: Markdown 列表文本。
    """
    values = list(failed_repos)
    if not values:
        return "- 无"
    return "\n".join(f"- {name}" for name in values)


def _format_optional_items(items: Iterable[str] | None) -> str:
    """格式化可选文本条目。

    :param items: 可选条目序列。
    :return: Markdown 列表文本。
    """
    if items is None:
        return "- 无"
    values = [item.strip() for item in items if item.strip()]
    if not values:
        return "- 无"
    return "\n".join(f"- {value}" for value in values)


def render_report(
    period: str,
    time_range_text: str,
    grouped_items: Dict[str, List[str]],
    filtered_count: int,
    failed_repos: Iterable[str],
    style: str = "concise",
    in_progress_items: Iterable[str] | None = None,
    risk_items: Iterable[str] | None = None,
    next_plan_items: Iterable[str] | None = None,
    period_overview: str = "- 无",
    repo_daily_details: str = "- 无",
    daily_table: str = "| 日期 | 仓库 | 工作内容 |\n|---|---|---|\n| - | - | 无 |",
    template_text: str | None = None,
) -> str:
    """渲染最终汇报文本。

    :param period: 周期类型。
    :param time_range_text: 时间范围文本。
    :param grouped_items: 聚合后的仓库工作项。
    :param filtered_count: 被过滤提交数量。
    :param failed_repos: 采集失败仓库列表。
    :param style: 汇报样式，支持 concise、management、technical、repo-daily。
    :param in_progress_items: 进行中事项列表。
    :param risk_items: 风险事项列表。
    :param next_plan_items: 下阶段计划事项列表。
    :param period_overview: 周期总结文本。
    :param repo_daily_details: 仓库按天明细文本。
    :param daily_table: 仓库按天表格文本。
    :param template_text: 用户自定义模板文本。
    :return: 渲染后的汇报内容。
    """
    values = {
        "period_title": _period_title(period),
        "time_range": time_range_text,
        "completed_items": _format_completed_items(grouped_items),
        "failed_repos": _format_failed_repos(failed_repos),
        "filtered_count": str(filtered_count),
        "in_progress_items": _format_optional_items(in_progress_items),
        "risk_items": _format_optional_items(risk_items),
        "next_plan_items": _format_optional_items(next_plan_items),
        "period_overview": period_overview,
        "repo_daily_details": repo_daily_details,
        "daily_table": daily_table,
    }
    if template_text is None:
        if style == "repo-daily":
            overview_title = "本周总结" if period == "weekly" else "本周期总结"
            return (
                f"# {values['period_title']}\n\n"
                f"## 时间范围\n{values['time_range']}\n\n"
                "## 本周期完成\n"
                f"{values['completed_items']}\n\n"
                f"## {overview_title}\n"
                f"{values['period_overview']}\n\n"
                "## 仓库每日明细\n"
                f"{values['repo_daily_details']}\n\n"
                "## 按天表格视图\n"
                f"{values['daily_table']}\n\n"
                "## 采集异常仓库\n"
                f"{values['failed_repos']}\n\n"
                f"过滤提交数：{values['filtered_count']}\n"
            )
        if style == "management":
            return (
                f"# {values['period_title']}\n\n"
                f"## 时间范围\n{values['time_range']}\n\n"
                "## 本周期完成\n"
                f"{values['completed_items']}\n\n"
                "## 进行中\n"
                f"{values['in_progress_items']}\n\n"
                "## 风险与问题\n"
                f"{values['risk_items']}\n\n"
                "## 下阶段计划\n"
                f"{values['next_plan_items']}\n\n"
                "## 采集异常仓库\n"
                f"{values['failed_repos']}\n\n"
                f"过滤提交数：{values['filtered_count']}\n"
            )
        if style == "technical":
            return (
                f"# {values['period_title']}\n\n"
                f"## 时间范围\n{values['time_range']}\n\n"
                "## 变更明细\n"
                f"{values['completed_items']}\n\n"
                "## 进行中技术项\n"
                f"{values['in_progress_items']}\n\n"
                "## 风险阻塞\n"
                f"{values['risk_items']}\n\n"
                "## 采集异常仓库\n"
                f"{values['failed_repos']}\n\n"
                f"过滤提交数：{values['filtered_count']}\n"
            )
        return (
            f"# {values['period_title']}\n\n"
            f"## 时间范围\n{values['time_range']}\n\n"
            "## 已完成事项\n"
            f"{values['completed_items']}\n\n"
            "## 采集异常仓库\n"
            f"{values['failed_repos']}\n\n"
            f"过滤提交数：{values['filtered_count']}\n"
        )
    output = template_text
    for key, value in values.items():
        output = output.replace(f"{{{{{key}}}}}", value)
    return output
