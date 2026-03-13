"""run_report 命令入口测试。"""

from datetime import datetime
from pathlib import Path

from scripts.run_report import (
    build_management_sections,
    discover_local_repositories,
    load_template_text,
    parse_args,
    parse_git_log_output,
    write_daily_table_csv,
)
from scripts.report_core import CommitRecord


def test_discover_local_repositories_finds_nested_git_dirs(tmpdir) -> None:
    """验证可递归发现多层级本地仓库。

    :param tmpdir: pytest 临时目录对象。
    :return: None
    """
    tmp_path = Path(str(tmpdir))
    repo_a = tmp_path / "repo-a"
    repo_a_git = repo_a / ".git"
    repo_a_git.mkdir(parents=True)

    repo_b = tmp_path / "group" / "repo-b"
    repo_b_git = repo_b / ".git"
    repo_b_git.mkdir(parents=True)

    found = discover_local_repositories(tmp_path, max_depth=3)
    assert len(found) == 2
    assert set(found) == {repo_a, repo_b}


def test_parse_git_log_output_parses_commit_rows() -> None:
    """验证 git log 输出可被正确解析。

    :return: None
    """
    output = (
        "abc123\x1ftealiving\x1ftealiving@example.com\x1f2026-03-06T10:00:00+08:00\x1f"
        "fix login token refresh\x1fparent1 parent2\n"
        "def456\x1ftealiving\x1ftealiving@example.com\x1f2026-03-06T11:00:00+08:00\x1f"
        "add export api\x1fparent3\n"
    )
    commits = parse_git_log_output("repo-a", output)
    assert len(commits) == 2
    assert commits[0].is_merge is True
    assert commits[1].is_merge is False
    assert commits[0].committed_at == datetime.fromisoformat("2026-03-06T10:00:00+08:00")


def test_parse_args_accept_style_management() -> None:
    """验证命令行参数支持样式选项。

    :return: None
    """
    args = parse_args(["--style", "management"])
    assert args.style == "management"


def test_load_template_text_support_style_template() -> None:
    """验证内置样式模板可被加载。

    :return: None
    """
    template = load_template_text(period="weekly", style="management", template_path=None)
    assert template is not None
    assert "风险与问题" in template


def test_parse_args_accept_repo_daily_and_csv_output() -> None:
    """验证命令行参数支持仓库按天风格和 CSV 导出。

    :return: None
    """
    args = parse_args(
        [
            "--style",
            "repo-daily",
            "--table-output-csv",
            "weekly_table.csv",
        ]
    )
    assert args.style == "repo-daily"
    assert str(args.table_output_csv).endswith("weekly_table.csv")


def test_load_template_text_support_repo_daily_template() -> None:
    """验证仓库按天风格模板可被加载。

    :return: None
    """
    template = load_template_text(period="weekly", style="repo-daily", template_path=None)
    assert template is not None
    assert "仓库每日明细" in template


def test_build_management_sections_extracts_risk_and_progress() -> None:
    """验证可从提交中提取管理分区条目。

    :return: None
    """
    commits = [
        CommitRecord(
            repo="repo-a",
            commit_id="a1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime.fromisoformat("2026-03-06T10:00:00+08:00"),
            message="正在重构任务调度模块",
            is_merge=False,
        ),
        CommitRecord(
            repo="repo-b",
            commit_id="b1",
            author_name="tealiving",
            author_email="tealiving@example.com",
            committed_at=datetime.fromisoformat("2026-03-06T11:00:00+08:00"),
            message="联调存在阻塞，待确认接口权限",
            is_merge=False,
        ),
    ]
    in_progress_items, risk_items, next_plan_items = build_management_sections(commits)
    assert any("repo-a" in item for item in in_progress_items)
    assert any("repo-b" in item for item in risk_items)
    assert len(next_plan_items) >= 1


def test_write_daily_table_csv_writes_expected_rows(tmpdir) -> None:
    """验证 CSV 导出包含头与数据行。

    :param tmpdir: pytest 临时目录对象。
    :return: None
    """
    output_path = Path(str(tmpdir)) / "table.csv"
    write_daily_table_csv(
        {
            "repo-a": {"2026-03-05": ["fix login token refresh", "add audit log"]},
            "repo-b": {"2026-03-06": ["refactor workflow"]},
        },
        output_path=output_path,
    )
    content = output_path.read_text(encoding="utf-8")
    assert "date,repo,items" in content
    assert "2026-03-05,repo-a" in content
    assert "2026-03-06,repo-b" in content
