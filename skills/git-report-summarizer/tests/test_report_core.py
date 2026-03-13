"""report_core 核心逻辑测试。"""

from datetime import datetime

import pytest

from scripts.report_core import (
    CommitRecord,
    aggregate_commits,
    aggregate_repo_daily_commits,
    aggregate_repo_daily_summary_commits,
    aggregate_summarized_commits,
    filter_and_normalize_commits,
    format_daily_table,
    format_period_overview,
    format_repo_daily_details,
    render_report,
    resolve_time_window,
    summarize_commit_message,
)


def test_resolve_time_window_daily() -> None:
    """验证日报窗口按自然日计算。

    :return: None
    """
    start, end = resolve_time_window("daily", base_date=datetime(2026, 3, 6))
    assert start == datetime(2026, 3, 6, 0, 0, 0)
    assert end == datetime(2026, 3, 7, 0, 0, 0)


def test_resolve_time_window_weekly() -> None:
    """验证周报窗口按周一到下周一计算。

    :return: None
    """
    start, end = resolve_time_window("weekly", base_date=datetime(2026, 3, 6))
    assert start == datetime(2026, 3, 2, 0, 0, 0)
    assert end == datetime(2026, 3, 9, 0, 0, 0)


def test_resolve_time_window_custom_missing_bounds() -> None:
    """验证自定义窗口缺失边界时抛出异常。

    :return: None
    """
    with pytest.raises(ValueError):
        resolve_time_window("custom", since=datetime(2026, 3, 1))


def test_filter_and_normalize_commits_filters_noise() -> None:
    """验证噪声与合并提交可被过滤。

    :return: None
    """
    commits = [
        CommitRecord(
            repo="repo-a",
            commit_id="a1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 6, 10, 0, 0),
            message="fix login token refresh",
            is_merge=False,
        ),
        CommitRecord(
            repo="repo-a",
            commit_id="a2",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 6, 11, 0, 0),
            message="merge branch feature/x",
            is_merge=True,
        ),
        CommitRecord(
            repo="repo-a",
            commit_id="a3",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 6, 12, 0, 0),
            message="wip",
            is_merge=False,
        ),
    ]

    kept, filtered = filter_and_normalize_commits(commits)
    assert len(kept) == 1
    assert kept[0].commit_id == "a1"
    assert filtered == 2


def test_aggregate_commits_groups_by_repo() -> None:
    """验证提交可按仓库聚合为工作项。

    :return: None
    """
    commits = [
        CommitRecord(
            repo="repo-a",
            commit_id="a1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 6, 10, 0, 0),
            message="fix login token refresh",
            is_merge=False,
        ),
        CommitRecord(
            repo="repo-b",
            commit_id="b1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 6, 13, 0, 0),
            message="add export report api",
            is_merge=False,
        ),
    ]
    grouped = aggregate_commits(commits)
    assert list(grouped.keys()) == ["repo-a", "repo-b"]
    assert grouped["repo-a"] == ["fix login token refresh"]


def test_render_report_default_template() -> None:
    """验证默认模板渲染包含基础结构。

    :return: None
    """
    report = render_report(
        period="daily",
        time_range_text="2026-03-06 ~ 2026-03-07",
        grouped_items={"repo-a": ["fix login token refresh"]},
        filtered_count=1,
        failed_repos=["repo-c"],
        style="concise",
    )
    assert "日报" in report
    assert "repo-a" in report
    assert "repo-c" in report
    assert "过滤提交数：1" in report


def test_render_report_custom_template() -> None:
    """验证自定义模板占位符替换生效。

    :return: None
    """
    report = render_report(
        period="weekly",
        time_range_text="2026-03-02 ~ 2026-03-09",
        grouped_items={"repo-a": ["fix login token refresh"]},
        filtered_count=0,
        failed_repos=[],
        style="management",
        in_progress_items=["[repo-a] 正在重构任务调度"],
        risk_items=["联调资源待确认"],
        next_plan_items=["完成回归测试"],
        template_text=(
            "标题={{period_title}}\n范围={{time_range}}\n内容={{completed_items}}\n"
            "进行中={{in_progress_items}}\n风险={{risk_items}}\n计划={{next_plan_items}}"
        ),
    )
    assert "标题=本周周报" in report
    assert "- [repo-a] fix login token refresh" in report
    assert "- [repo-a] 正在重构任务调度" in report
    assert "联调资源待确认" in report
    assert "完成回归测试" in report


def test_render_report_management_default_template() -> None:
    """验证管理版默认模板包含管理分区。

    :return: None
    """
    report = render_report(
        period="weekly",
        time_range_text="2026-03-02 ~ 2026-03-09",
        grouped_items={"repo-a": ["fix login token refresh"]},
        filtered_count=0,
        failed_repos=[],
        style="management",
        in_progress_items=["[repo-a] 正在重构任务调度"],
        risk_items=["联调资源待确认"],
        next_plan_items=["完成回归测试"],
    )
    assert "进行中" in report
    assert "风险与问题" in report
    assert "下阶段计划" in report


def test_aggregate_repo_daily_commits_groups_by_repo_and_day() -> None:
    """验证提交可按仓库与日期分组。

    :return: None
    """
    commits = [
        CommitRecord(
            repo="repo-a",
            commit_id="a1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 5, 10, 0, 0),
            message="fix login token refresh",
            is_merge=False,
        ),
        CommitRecord(
            repo="repo-a",
            commit_id="a2",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 5, 11, 0, 0),
            message="add audit log",
            is_merge=False,
        ),
        CommitRecord(
            repo="repo-b",
            commit_id="b1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 6, 9, 0, 0),
            message="refactor workflow",
            is_merge=False,
        ),
    ]
    grouped = aggregate_repo_daily_commits(commits)
    assert grouped["repo-a"]["2026-03-05"] == [
        "fix login token refresh",
        "add audit log",
    ]
    assert grouped["repo-b"]["2026-03-06"] == ["refactor workflow"]


def test_format_repo_daily_details_contains_repo_and_date() -> None:
    """验证仓库按天明细可读性结构。

    :return: None
    """
    details = format_repo_daily_details(
        {
            "repo-a": {"2026-03-05": ["fix login token refresh"]},
            "repo-b": {"2026-03-06": ["refactor workflow"]},
        }
    )
    assert "### repo-a" in details
    assert "2026-03-05" in details
    assert "fix login token refresh" in details


def test_format_daily_table_renders_markdown_rows() -> None:
    """验证按天表格可渲染为 Markdown。

    :return: None
    """
    table_text = format_daily_table(
        {
            "repo-a": {"2026-03-05": ["fix login token refresh", "add audit log"]},
        }
    )
    assert "| 日期 | 仓库 | 工作内容 |" in table_text
    assert "| 2026-03-05 | repo-a | fix login token refresh" in table_text


def test_render_report_repo_daily_default_template() -> None:
    """验证仓库按天风格默认模板包含明细与表格。

    :return: None
    """
    report = render_report(
        period="weekly",
        time_range_text="2026-03-02 ~ 2026-03-09",
        grouped_items={"repo-a": ["fix login token refresh"]},
        filtered_count=0,
        failed_repos=[],
        style="repo-daily",
        period_overview="- [repo-a] 完成登录链路优化",
        repo_daily_details="### repo-a\n- 2026-03-05\n  - fix login token refresh",
        daily_table="| 日期 | 仓库 | 工作内容 |\n|---|---|---|\n| 2026-03-05 | repo-a | fix login token refresh |",
    )
    assert "本周总结" in report
    assert "仓库每日明细" in report
    assert "按天表格视图" in report


def test_summarize_commit_message_extracts_multiline_items() -> None:
    """验证可从 git -m 拼接文本中提取摘要条目。

    :return: None
    """
    message = (
        'git commit -m "feat(v1.0): 完成企业版多格式文本脱敏与OCR能力" \\ '
        '-m "1. 新增 pdf/txt/docx 批量识别与文本删除" \\ '
        '-m "2. 完善 GUI 进度和取消能力"'
    )
    items = summarize_commit_message(message)
    assert items[0] == "完成企业版多格式文本脱敏与OCR能力"
    assert any("批量识别与文本删除" in item for item in items)
    assert any("GUI" in item and "进度和取消能力" in item for item in items)


def test_aggregate_summarized_commits_uses_compact_items() -> None:
    """验证摘要聚合输出为精简工作项。

    :return: None
    """
    commits = [
        CommitRecord(
            repo="repo-a",
            commit_id="a1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 5, 10, 0, 0),
            message="feat: 完成登录态刷新与过期处理链路",
            is_merge=False,
        )
    ]
    grouped = aggregate_summarized_commits(commits)
    assert grouped["repo-a"] == ["完成登录态刷新与过期处理链路"]


def test_aggregate_repo_daily_summary_commits_groups_compact_items() -> None:
    """验证按天摘要聚合输出精简条目。

    :return: None
    """
    commits = [
        CommitRecord(
            repo="repo-a",
            commit_id="a1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime(2026, 3, 5, 10, 0, 0),
            message="fix: 修复登录态刷新失败",
            is_merge=False,
        )
    ]
    grouped = aggregate_repo_daily_summary_commits(commits)
    assert grouped["repo-a"]["2026-03-05"] == ["修复登录态刷新失败"]


def test_format_period_overview_compacts_by_repo() -> None:
    """验证周期总结按仓库输出重点工作。

    :return: None
    """
    overview = format_period_overview(
        {
            "repo-a": {
                "2026-03-05": ["完成登录态刷新", "完善权限校验"],
                "2026-03-06": ["修复导出异常"],
            }
        }
    )
    assert "[repo-a] 重点完成：" in overview
    assert "完成登录态刷新" in overview
