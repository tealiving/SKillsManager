"""git 提交汇报入口脚本。"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.report_core import (
    CommitRecord,
    aggregate_repo_daily_summary_commits,
    aggregate_repo_daily_commits,
    aggregate_summarized_commits,
    filter_and_normalize_commits,
    format_daily_table,
    format_period_overview,
    format_repo_daily_details,
    render_report,
    resolve_time_window,
)

IN_PROGRESS_KEYWORDS = ("进行中", "重构", "优化中", "refactor", "in progress")
RISK_KEYWORDS = ("风险", "阻塞", "失败", "待确认", "待联调", "blocked")


def parse_iso_date(value: str) -> datetime:
    """解析日期文本为 datetime。

    :param value: 日期文本，支持 YYYY-MM-DD 或 ISO-8601。
    :return: 解析后的 datetime 对象。
    """
    if len(value) == 10:
        return datetime.strptime(value, "%Y-%m-%d")
    return datetime.fromisoformat(value)


def run_command(command: Sequence[str], cwd: Path | None = None) -> str:
    """执行外部命令并返回标准输出。

    :param command: 命令及参数序列。
    :param cwd: 执行目录。
    :return: 标准输出文本（去除首尾空白）。
    """
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _safe_git_config(key: str, cwd: Path) -> str:
    """读取 git 配置项，优先仓库级再回退全局。

    :param key: git 配置键名。
    :param cwd: 当前工作目录。
    :return: 配置值，不存在时返回空字符串。
    """
    try:
        value = run_command(["git", "config", "--get", key], cwd=cwd)
        if value:
            return value
    except subprocess.CalledProcessError:
        pass
    try:
        return run_command(["git", "config", "--global", "--get", key], cwd=None)
    except subprocess.CalledProcessError:
        return ""


def read_identity(cwd: Path) -> Tuple[str, str]:
    """读取当前 git 身份信息。

    :param cwd: 当前工作目录。
    :return: (用户名, 邮箱) 元组。
    """
    return _safe_git_config("user.name", cwd), _safe_git_config("user.email", cwd)


def discover_local_repositories(workspace: Path, max_depth: int = 4) -> List[Path]:
    """在工作目录递归发现本地 git 仓库。

    :param workspace: 工作目录根路径。
    :param max_depth: 最大扫描层级。
    :return: 仓库路径列表。
    """
    found: List[Path] = []
    root_depth = len(workspace.resolve().parts)
    for current_root, dirs, _files in os.walk(workspace):
        root = Path(current_root)
        depth = len(root.resolve().parts) - root_depth
        if depth > max_depth:
            dirs[:] = []
            continue
        if ".git" in dirs:
            found.append(root)
            dirs[:] = []
    return sorted(found)


def parse_git_log_output(repo_name: str, output: str) -> List[CommitRecord]:
    """解析 git log 输出。

    :param repo_name: 仓库显示名。
    :param output: git log 原始输出。
    :return: 解析后的提交记录列表。
    """
    records: List[CommitRecord] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 6:
            continue
        commit_id, author_name, author_email, commit_time, message, parents = parts
        parent_ids = [item for item in parents.split(" ") if item]
        records.append(
            CommitRecord(
                repo=repo_name,
                commit_id=commit_id,
                author_name=author_name,
                author_email=author_email,
                committed_at=datetime.fromisoformat(commit_time),
                message=message,
                is_merge=len(parent_ids) > 1,
            )
        )
    return records


def _match_identity(
    record: CommitRecord,
    author_name: str,
    author_email: str,
) -> bool:
    """判断提交是否匹配当前身份。

    :param record: 提交记录。
    :param author_name: 目标用户名。
    :param author_email: 目标邮箱。
    :return: 匹配返回 True，否则 False。
    """
    name_matched = bool(author_name) and record.author_name.lower() == author_name.lower()
    email_matched = bool(author_email) and record.author_email.lower() == author_email.lower()
    if author_name and author_email:
        return name_matched or email_matched
    if author_name:
        return name_matched
    if author_email:
        return email_matched
    return True


def collect_local_commits(
    repo_path: Path,
    window_start: datetime,
    window_end: datetime,
    author_name: str,
    author_email: str,
) -> List[CommitRecord]:
    """收集单仓库本地提交。

    :param repo_path: 仓库路径。
    :param window_start: 时间窗口开始。
    :param window_end: 时间窗口结束。
    :param author_name: 目标用户名。
    :param author_email: 目标邮箱。
    :return: 过滤身份后的提交记录列表。
    """
    output = run_command(
        [
            "git",
            "-C",
            str(repo_path),
            "log",
            f"--since={window_start.isoformat()}",
            f"--until={window_end.isoformat()}",
            "--pretty=format:%H%x1f%an%x1f%ae%x1f%aI%x1f%s%x1f%P",
        ]
    )
    parsed = parse_git_log_output(repo_path.name, output)
    return [
        item
        for item in parsed
        if _match_identity(item, author_name=author_name, author_email=author_email)
    ]


def collect_local_commits_for_repositories(
    repositories: Sequence[Path],
    window_start: datetime,
    window_end: datetime,
    author_name: str,
    author_email: str,
    max_workers: int,
) -> Tuple[List[CommitRecord], List[str]]:
    """并发采集多个本地仓库提交。

    :param repositories: 仓库路径序列。
    :param window_start: 时间窗口开始。
    :param window_end: 时间窗口结束。
    :param author_name: 目标用户名。
    :param author_email: 目标邮箱。
    :param max_workers: 最大并发数。
    :return: (提交列表, 失败仓库名列表)。
    """
    commits: List[CommitRecord] = []
    failed_repos: List[str] = []
    if not repositories:
        return commits, failed_repos

    worker_count = max(1, min(max_workers, len(repositories)))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: Dict[Future[List[CommitRecord]], Path] = {}
        for repo_path in repositories:
            future = executor.submit(
                collect_local_commits,
                repo_path,
                window_start,
                window_end,
                author_name,
                author_email,
            )
            future_map[future] = repo_path

        for future in as_completed(future_map):
            repo_path = future_map[future]
            try:
                commits.extend(future.result())
            except subprocess.CalledProcessError:
                failed_repos.append(repo_path.name)

    return commits, sorted(failed_repos)


def _http_get_json(url: str, headers: Dict[str, str]) -> List[Dict[str, object]]:
    """发起 HTTP GET 并解析 JSON。

    :param url: 请求 URL。
    :param headers: 请求头字典。
    :return: JSON 数组对象。
    """
    request = Request(url=url, headers=headers, method="GET")
    with urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if isinstance(data, list):
        return data
    return []


def discover_remote_repositories(
    platform: str,
    user_name: str,
    token: str,
    api_base: str,
    max_pages: int = 5,
) -> List[str]:
    """发现远程仓库列表。

    :param platform: 平台名称，支持 github 或 gitee。
    :param user_name: 平台用户名。
    :param token: API 访问令牌。
    :param api_base: API 基础地址。
    :param max_pages: 最大分页页数。
    :return: full_name 形式仓库列表。
    """
    if not user_name:
        return []

    repositories: List[str] = []
    headers: Dict[str, str] = {}
    if platform == "github" and token:
        headers["Authorization"] = f"Bearer {token}"

    for page in range(1, max_pages + 1):
        query = {"per_page": 100, "page": page}
        if platform == "github":
            if token:
                url = f"{api_base.rstrip('/')}/user/repos?{urlencode(query)}"
            else:
                url = (
                    f"{api_base.rstrip('/')}/users/{user_name}/repos?"
                    f"{urlencode(query)}"
                )
        elif platform == "gitee":
            if token:
                query["access_token"] = token
            url = (
                f"{api_base.rstrip('/')}/users/{user_name}/repos?"
                f"{urlencode(query)}"
            )
        else:
            return []

        data = _http_get_json(url=url, headers=headers)
        if not data:
            break
        for repo in data:
            full_name = str(repo.get("full_name", "")).strip()
            if full_name:
                repositories.append(full_name)

    return sorted(set(repositories))


def collect_remote_commits(
    platform: str,
    repository_full_name: str,
    user_name: str,
    token: str,
    api_base: str,
    window_start: datetime,
    window_end: datetime,
    max_pages: int = 5,
) -> List[CommitRecord]:
    """采集单个远程仓库提交。

    :param platform: 平台名称，支持 github 或 gitee。
    :param repository_full_name: full_name 仓库名。
    :param user_name: 平台用户名。
    :param token: API 访问令牌。
    :param api_base: API 基础地址。
    :param window_start: 时间窗口开始。
    :param window_end: 时间窗口结束。
    :param max_pages: 最大分页页数。
    :return: 提交记录列表。
    """
    headers: Dict[str, str] = {}
    if platform == "github" and token:
        headers["Authorization"] = f"Bearer {token}"

    commits: List[CommitRecord] = []
    for page in range(1, max_pages + 1):
        query = {
            "since": window_start.isoformat(),
            "until": window_end.isoformat(),
            "per_page": 100,
            "page": page,
        }
        if user_name:
            query["author"] = user_name

        if platform == "github":
            url = (
                f"{api_base.rstrip('/')}/repos/{repository_full_name}/commits?"
                f"{urlencode(query)}"
            )
        elif platform == "gitee":
            if token:
                query["access_token"] = token
            url = (
                f"{api_base.rstrip('/')}/repos/{repository_full_name}/commits?"
                f"{urlencode(query)}"
            )
        else:
            return []

        rows = _http_get_json(url=url, headers=headers)
        if not rows:
            break
        for row in rows:
            commit = row.get("commit", {})
            author = commit.get("author", {}) if isinstance(commit, dict) else {}
            message = str(commit.get("message", "")).splitlines()[0]
            date_value = str(author.get("date", ""))
            if not date_value:
                continue
            parent_list = row.get("parents", [])
            parents = parent_list if isinstance(parent_list, list) else []
            commits.append(
                CommitRecord(
                    repo=repository_full_name,
                    commit_id=str(row.get("sha", "")),
                    author_name=str(author.get("name", "")),
                    author_email=str(author.get("email", "")),
                    committed_at=datetime.fromisoformat(
                        date_value.replace("Z", "+00:00")
                    ),
                    message=message,
                    is_merge=len(parents) > 1,
                )
            )
    return commits


def format_time_range(window_start: datetime, window_end: datetime) -> str:
    """格式化时间窗口文本。

    :param window_start: 开始时间。
    :param window_end: 结束时间。
    :return: 格式化文本。
    """
    return (
        f"{window_start.strftime('%Y-%m-%d %H:%M:%S')} ~ "
        f"{window_end.strftime('%Y-%m-%d %H:%M:%S')}"
    )


def _append_unique_item(target: List[str], value: str) -> None:
    """向列表追加去重条目。

    :param target: 目标列表。
    :param value: 候选文本。
    :return: None
    """
    if value not in target:
        target.append(value)


def build_management_sections(
    commits: Sequence[CommitRecord],
) -> Tuple[List[str], List[str], List[str]]:
    """基于提交信息构建管理分区条目。

    :param commits: 已过滤提交记录序列。
    :return: (进行中, 风险, 下阶段计划) 三元组。
    """
    in_progress_items: List[str] = []
    risk_items: List[str] = []
    next_plan_items: List[str] = []

    for commit in commits:
        content = commit.message.strip()
        lowered = content.lower()
        item_text = f"[{commit.repo}] {content}"
        if any(keyword in lowered for keyword in RISK_KEYWORDS):
            _append_unique_item(risk_items, item_text)
            _append_unique_item(next_plan_items, f"处理风险项：{item_text}")
            continue
        if any(keyword in lowered for keyword in IN_PROGRESS_KEYWORDS):
            _append_unique_item(in_progress_items, item_text)
            _append_unique_item(next_plan_items, f"推进并完成：{item_text}")

    if not next_plan_items:
        top_commits = sorted(commits, key=lambda row: row.committed_at, reverse=True)[:3]
        for commit in top_commits:
            _append_unique_item(next_plan_items, f"继续推进 [{commit.repo}] {commit.message.strip()}")

    return in_progress_items, risk_items, next_plan_items


def load_template_text(
    period: str,
    style: str,
    template_path: Path | None,
) -> str | None:
    """加载用户模板或内置模板。

    :param period: 周期类型。
    :param style: 汇报样式。
    :param template_path: 用户模板路径。
    :return: 模板文本，不存在时返回 None。
    """
    if template_path is not None:
        return template_path.read_text(encoding="utf-8")

    template_dir = Path(__file__).resolve().parents[1] / "assets" / "templates"
    candidates = [f"{period}.md.j2"]
    if style != "concise":
        candidates.insert(0, f"{period}.{style}.md.j2")
    for filename in candidates:
        builtin = template_dir / filename
        if builtin.exists():
            return builtin.read_text(encoding="utf-8")
    return None


def write_daily_table_csv(
    repo_daily_items: Dict[str, Dict[str, List[str]]],
    output_path: Path,
) -> None:
    """导出仓库按天工作内容 CSV。

    :param repo_daily_items: 仓库-日期-事项映射。
    :param output_path: 输出 CSV 路径。
    :return: None
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "repo", "items"])
        for repo, day_map in repo_daily_items.items():
            for day_text, items in day_map.items():
                writer.writerow([day_text, repo, " | ".join(items)])


def serialize_commits(commits: Iterable[CommitRecord]) -> List[Dict[str, str]]:
    """序列化提交记录为 JSON 对象列表。

    :param commits: 提交记录序列。
    :return: 可 JSON 序列化的字典列表。
    """
    serialized: List[Dict[str, str]] = []
    for item in commits:
        serialized.append(
            {
                "repo": item.repo,
                "commit_id": item.commit_id,
                "author_name": item.author_name,
                "author_email": item.author_email,
                "committed_at": item.committed_at.isoformat(),
                "message": item.message,
                "is_merge": str(item.is_merge),
            }
        )
    return serialized


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。

    :param argv: 参数序列，为 None 时读取系统参数。
    :return: 解析后的命名空间对象。
    """
    parser = argparse.ArgumentParser(
        description="根据 git 身份汇总提交并生成日报/周报/月报。"
    )
    parser.add_argument(
        "--period",
        choices=["daily", "weekly", "monthly", "custom"],
        default="daily",
        help="汇报周期。",
    )
    parser.add_argument("--base-date", type=str, help="基准日期，格式 YYYY-MM-DD。")
    parser.add_argument("--since", type=str, help="自定义开始时间，ISO 格式。")
    parser.add_argument("--until", type=str, help="自定义结束时间，ISO 格式。")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="本地仓库扫描根目录。",
    )
    parser.add_argument(
        "--repos",
        nargs="*",
        default=[],
        help="显式指定仓库路径列表（可多个）。",
    )
    parser.add_argument(
        "--platform",
        choices=["local", "github", "gitee", "both"],
        default="local",
        help="数据来源平台。",
    )
    parser.add_argument(
        "--enable-remote-discovery",
        action="store_true",
        help="是否启用远程仓库发现与提交采集。",
    )
    parser.add_argument("--github-user", type=str, default="", help="GitHub 用户名。")
    parser.add_argument("--gitee-user", type=str, default="", help="Gitee 用户名。")
    parser.add_argument(
        "--github-token",
        type=str,
        default=os.getenv("GITHUB_TOKEN", ""),
        help="GitHub Token，默认读取环境变量 GITHUB_TOKEN。",
    )
    parser.add_argument(
        "--gitee-token",
        type=str,
        default=os.getenv("GITEE_TOKEN", ""),
        help="Gitee Token，默认读取环境变量 GITEE_TOKEN。",
    )
    parser.add_argument(
        "--github-api-base",
        type=str,
        default="https://api.github.com",
        help="GitHub API 基础地址。",
    )
    parser.add_argument(
        "--gitee-api-base",
        type=str,
        default="https://gitee.com/api/v5",
        help="Gitee API 基础地址。",
    )
    parser.add_argument("--author-name", type=str, default="", help="覆盖 git 用户名。")
    parser.add_argument("--author-email", type=str, default="", help="覆盖 git 邮箱。")
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="本地仓库并发采集工作线程数。",
    )
    parser.add_argument(
        "--style",
        choices=["concise", "management", "technical", "repo-daily"],
        default="concise",
        help="输出风格。",
    )
    parser.add_argument(
        "--table-output-csv",
        type=Path,
        default=None,
        help="按天表格 CSV 输出路径。",
    )
    parser.add_argument("--template", type=Path, help="自定义模板路径。")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("report.md"),
        help="汇报输出路径。",
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=Path("raw_commits.json"),
        help="原始提交输出路径。",
    )
    return parser.parse_args(argv)


def _resolve_window_from_args(args: argparse.Namespace) -> Tuple[datetime, datetime]:
    """根据参数解析时间窗口。

    :param args: 命令行参数对象。
    :return: (开始时间, 结束时间) 元组。
    """
    base_date = parse_iso_date(args.base_date) if args.base_date else None
    since = parse_iso_date(args.since) if args.since else None
    until = parse_iso_date(args.until) if args.until else None
    return resolve_time_window(
        period=args.period,
        base_date=base_date,
        since=since,
        until=until,
    )


def _build_local_repository_list(args: argparse.Namespace) -> List[Path]:
    """构建本地仓库列表。

    :param args: 命令行参数对象。
    :return: 去重后的本地仓库路径列表。
    """
    repositories: List[Path] = []
    for text_path in args.repos:
        path = Path(text_path).resolve()
        if (path / ".git").exists():
            repositories.append(path)
    if args.platform in {"local", "both"}:
        repositories.extend(discover_local_repositories(args.workspace.resolve()))
    unique: Dict[str, Path] = {}
    for path in repositories:
        unique[str(path)] = path
    return sorted(unique.values())


def _collect_remote_if_enabled(
    args: argparse.Namespace,
    window_start: datetime,
    window_end: datetime,
    author_name: str,
) -> Tuple[List[CommitRecord], List[str]]:
    """按参数采集远程提交。

    :param args: 命令行参数对象。
    :param window_start: 时间窗口开始。
    :param window_end: 时间窗口结束。
    :param author_name: 作者名称。
    :return: (提交记录列表, 失败仓库列表)。
    """
    if not args.enable_remote_discovery or args.platform == "local":
        return [], []

    commits: List[CommitRecord] = []
    failed_repos: List[str] = []
    platform_list = (
        ["github", "gitee"] if args.platform == "both" else [args.platform]
    )
    for platform in platform_list:
        if platform == "github":
            user_name = args.github_user or author_name
            token = args.github_token
            api_base = args.github_api_base
        else:
            user_name = args.gitee_user or author_name
            token = args.gitee_token
            api_base = args.gitee_api_base
        if not user_name:
            continue

        try:
            repos = discover_remote_repositories(
                platform=platform,
                user_name=user_name,
                token=token,
                api_base=api_base,
            )
        except Exception:
            continue

        for repository in repos:
            try:
                commits.extend(
                    collect_remote_commits(
                        platform=platform,
                        repository_full_name=repository,
                        user_name=user_name,
                        token=token,
                        api_base=api_base,
                        window_start=window_start,
                        window_end=window_end,
                    )
                )
            except Exception:
                failed_repos.append(repository)

    return commits, sorted(set(failed_repos))


def main(argv: Sequence[str] | None = None) -> int:
    """执行汇报采集流程。

    :param argv: 命令行参数序列。
    :return: 进程退出码，0 表示成功。
    """
    args = parse_args(argv)
    window_start, window_end = _resolve_window_from_args(args)

    git_name, git_email = read_identity(args.workspace.resolve())
    author_name = args.author_name or git_name
    author_email = args.author_email or git_email

    local_repositories = _build_local_repository_list(args)
    local_commits, local_failed = collect_local_commits_for_repositories(
        repositories=local_repositories,
        window_start=window_start,
        window_end=window_end,
        author_name=author_name,
        author_email=author_email,
        max_workers=args.max_workers,
    )

    remote_commits, remote_failed = _collect_remote_if_enabled(
        args=args,
        window_start=window_start,
        window_end=window_end,
        author_name=author_name,
    )

    all_commits = local_commits + remote_commits
    kept_commits, filtered_count = filter_and_normalize_commits(all_commits)
    grouped = aggregate_summarized_commits(kept_commits)
    repo_daily_items = aggregate_repo_daily_summary_commits(kept_commits)
    raw_repo_daily_items = aggregate_repo_daily_commits(kept_commits)
    in_progress_items, risk_items, next_plan_items = build_management_sections(kept_commits)
    period_overview = format_period_overview(repo_daily_items)
    repo_daily_details = format_repo_daily_details(repo_daily_items)
    daily_table = format_daily_table(repo_daily_items)

    template_text = load_template_text(
        period=args.period,
        style=args.style,
        template_path=args.template,
    )
    report_text = render_report(
        period=args.period,
        time_range_text=format_time_range(window_start, window_end),
        grouped_items=grouped,
        filtered_count=filtered_count,
        failed_repos=sorted(set(local_failed + remote_failed)),
        style=args.style,
        in_progress_items=in_progress_items,
        risk_items=risk_items,
        next_plan_items=next_plan_items,
        period_overview=period_overview,
        repo_daily_details=repo_daily_details,
        daily_table=daily_table,
        template_text=template_text,
    )

    args.output.write_text(report_text, encoding="utf-8")
    raw_payload = {
        "period": args.period,
        "time_range": {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
        },
        "author_name": author_name,
        "author_email": author_email,
        "style": args.style,
        "filtered_count": filtered_count,
        "failed_repositories": sorted(set(local_failed + remote_failed)),
        "commit_count": len(kept_commits),
        "in_progress_items": in_progress_items,
        "risk_items": risk_items,
        "next_plan_items": next_plan_items,
        "period_overview": period_overview,
        "grouped_summary_items": grouped,
        "repo_daily_items": repo_daily_items,
        "raw_repo_daily_items": raw_repo_daily_items,
        "repo_daily_details": repo_daily_details,
        "daily_table": daily_table,
        "commits": serialize_commits(kept_commits),
    }
    if args.table_output_csv is not None:
        write_daily_table_csv(repo_daily_items=repo_daily_items, output_path=args.table_output_csv)
    args.raw_output.write_text(
        json.dumps(raw_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
