#!/usr/bin/env python
"""下载并校验第三方 Qt 样式资源。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_BLOCKED_LICENSE_KEYWORDS: tuple[str, ...] = ("GPL", "AGPL", "LGPL")


@dataclass(frozen=True)
class ThemeSource:
    """样式源元数据。

    :param name: 样式源唯一标识。
    :param display_name: 样式源显示名。
    :param style_family: 样式风格族。
    :param frameworks: 适配框架列表。
    :param license_name: 许可证标识。
    :param url: 资源下载地址。
    :param version: 版本或提交号标识。
    :param archive_type: 压缩包类型。
    :param sha256: 压缩包 SHA256 校验值。
    :param enabled: 是否启用。
    :param notes: 备注信息。
    :return: None
    """

    name: str
    display_name: str
    style_family: str
    frameworks: tuple[str, ...]
    license_name: str
    url: str
    version: str
    archive_type: str
    sha256: str
    enabled: bool
    notes: str

    @classmethod
    def from_dict(cls, payload: dict) -> "ThemeSource":
        """从配置字典创建样式源对象。

        :param payload: 配置字典。
        :return: ThemeSource 对象。
        """

        required_keys = ("name", "url", "version", "license")
        missing = [key for key in required_keys if key not in payload or not payload[key]]
        if missing:
            raise ValueError(f"样式源缺少必填字段: {', '.join(missing)}")

        frameworks = payload.get("frameworks") or []
        if not isinstance(frameworks, list):
            raise ValueError(f"样式源 {payload['name']} 的 frameworks 必须是列表")

        return cls(
            name=str(payload["name"]),
            display_name=str(payload.get("display_name", payload["name"])),
            style_family=str(payload.get("style_family", "unknown")),
            frameworks=tuple(str(item) for item in frameworks),
            license_name=str(payload["license"]),
            url=str(payload["url"]),
            version=str(payload["version"]),
            archive_type=str(payload.get("archive_type", "zip")),
            sha256=str(payload.get("sha256", "")).lower(),
            enabled=bool(payload.get("enabled", True)),
            notes=str(payload.get("notes", "")),
        )


def parse_args() -> argparse.Namespace:
    """解析命令行参数。

    :return: 解析后的参数对象。
    """

    parser = argparse.ArgumentParser(description="按配置下载并校验 Qt 样式资源")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="样式源配置文件路径，默认 references/theme_sources.json",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="下载目录，默认 assets/theme-cache",
    )
    parser.add_argument(
        "--provider",
        action="append",
        default=[],
        help="指定要下载的样式源名称，可重复传参",
    )
    parser.add_argument("--all", action="store_true", help="下载所有启用的样式源")
    parser.add_argument("--list", action="store_true", help="仅列出可用样式源")
    parser.add_argument("--force", action="store_true", help="即使已存在也重新下载")
    parser.add_argument("--dry-run", action="store_true", help="只打印将执行的操作")
    parser.add_argument(
        "--allow-copyleft",
        action="store_true",
        help="允许下载 GPL/AGPL/LGPL 等传染性许可证资源",
    )
    parser.add_argument(
        "--allow-license",
        action="append",
        default=[],
        help="额外允许的许可证（精确匹配，例：GPL-3.0）",
    )
    parser.add_argument(
        "--block-license",
        action="append",
        default=[],
        help="额外屏蔽的许可证（精确匹配，例：MIT）",
    )
    parser.add_argument(
        "--skip-checksum",
        action="store_true",
        help="跳过 SHA256 校验（仅建议临时排障使用）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="下载超时时间（秒），默认 120",
    )
    return parser.parse_args()


def resolve_skill_root() -> Path:
    """解析 skill 根目录。

    :return: skill 根目录路径。
    """

    return Path(__file__).resolve().parents[1]


def load_sources(config_path: Path) -> list[ThemeSource]:
    """加载样式源配置。

    :param config_path: 配置文件路径。
    :return: 样式源列表。
    """

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    items = payload.get("sources")
    if not isinstance(items, list):
        raise ValueError("配置文件字段 sources 必须是数组")

    sources = [ThemeSource.from_dict(item) for item in items]
    return [source for source in sources if source.enabled]


def sanitize_fragment(raw_text: str) -> str:
    """清洗文件名片段，避免非法字符。

    :param raw_text: 原始文本。
    :return: 清洗后的文本。
    """

    compact = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw_text.strip())
    return compact.strip("-") or "unknown"


def build_archive_name(source: ThemeSource) -> str:
    """为样式源构建归档文件名。

    :param source: 样式源对象。
    :return: 归档文件名。
    """

    version = sanitize_fragment(source.version)
    return f"{sanitize_fragment(source.name)}--{version}.{source.archive_type}"


def compute_sha256(file_path: Path) -> str:
    """计算文件 SHA256。

    :param file_path: 文件路径。
    :return: 文件 SHA256（小写十六进制）。
    """

    digest = hashlib.sha256()
    with file_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().lower()


def download_file(url: str, output_path: Path, timeout: int) -> None:
    """下载远程文件到指定路径。

    :param url: 下载地址。
    :param output_path: 输出路径。
    :param timeout: 超时时间（秒）。
    :return: None
    """

    request = urllib.request.Request(url=url, headers={"User-Agent": "codex-theme-fetch/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response, output_path.open("wb") as target:
        shutil.copyfileobj(response, target)


def ensure_checksum(file_path: Path, expected_sha256: str, skip_checksum: bool) -> None:
    """校验文件哈希。

    :param file_path: 文件路径。
    :param expected_sha256: 期望哈希。
    :param skip_checksum: 是否跳过校验。
    :return: None
    """

    if skip_checksum:
        return

    if not expected_sha256:
        raise ValueError(f"缺少 SHA256: {file_path.name}")

    actual_sha256 = compute_sha256(file_path)
    if actual_sha256 != expected_sha256.lower():
        raise ValueError(
            f"SHA256 不匹配: {file_path.name} expected={expected_sha256.lower()} actual={actual_sha256}"
        )


def select_sources(all_sources: Sequence[ThemeSource], provider_names: Sequence[str], pick_all: bool) -> list[ThemeSource]:
    """根据参数筛选待下载样式源。

    :param all_sources: 全部可用样式源。
    :param provider_names: 指定下载的样式源名列表。
    :param pick_all: 是否下载全部。
    :return: 待下载样式源列表。
    """

    if pick_all:
        return list(all_sources)

    if not provider_names:
        return []

    selected: list[ThemeSource] = []
    index = {source.name: source for source in all_sources}
    for name in provider_names:
        if name not in index:
            known = ", ".join(sorted(index))
            raise ValueError(f"未知 provider: {name}，可用值: {known}")
        selected.append(index[name])
    return selected


def normalize_license_name(license_name: str) -> str:
    """规范化许可证名称，便于比较。

    :param license_name: 原始许可证名称。
    :return: 规范化后的许可证名称（大写）。
    """

    return license_name.strip().upper()


def is_default_blocked_license(license_name: str) -> bool:
    """判断许可证是否命中默认屏蔽规则。

    :param license_name: 许可证名称。
    :return: 命中默认屏蔽返回 True，否则返回 False。
    """

    normalized = normalize_license_name(license_name)
    return any(keyword in normalized for keyword in DEFAULT_BLOCKED_LICENSE_KEYWORDS)


def apply_license_policy(
    selected_sources: Sequence[ThemeSource],
    allow_copyleft: bool,
    allowed_licenses: Sequence[str],
    blocked_licenses: Sequence[str],
) -> tuple[list[ThemeSource], list[str]]:
    """按许可证策略过滤样式源。

    :param selected_sources: 待处理样式源列表。
    :param allow_copyleft: 是否允许默认屏蔽的 copyleft 许可证。
    :param allowed_licenses: 额外允许的许可证列表（精确匹配）。
    :param blocked_licenses: 额外屏蔽的许可证列表（精确匹配）。
    :return: 二元组（通过过滤的样式源列表、被屏蔽提示信息列表）。
    """

    allow_set = {normalize_license_name(item) for item in allowed_licenses if item and item.strip()}
    block_set = {normalize_license_name(item) for item in blocked_licenses if item and item.strip()}
    accepted: list[ThemeSource] = []
    blocked_messages: list[str] = []

    for source in selected_sources:
        license_name = normalize_license_name(source.license_name)
        blocked_by_default = (not allow_copyleft) and is_default_blocked_license(license_name)
        blocked_by_custom = license_name in block_set
        allowed_by_custom = license_name in allow_set

        if blocked_by_custom and not allowed_by_custom:
            blocked_messages.append(
                f"BLOCK {source.name} license={source.license_name} reason=命中 --block-license"
            )
            continue

        if blocked_by_default and not allowed_by_custom:
            blocked_messages.append(
                f"BLOCK {source.name} license={source.license_name} "
                "reason=默认屏蔽 copyleft（可用 --allow-copyleft 或 --allow-license 放行）"
            )
            continue

        accepted.append(source)

    return accepted, blocked_messages


def print_source_table(sources: Iterable[ThemeSource]) -> None:
    """打印样式源列表。

    :param sources: 样式源可迭代对象。
    :return: None
    """

    rows = list(sources)
    if not rows:
        print("没有可用样式源")
        return

    print("name	license	frameworks	version")
    for source in rows:
        framework_text = ",".join(source.frameworks)
        print(f"{source.name}	{source.license_name}	{framework_text}	{source.version}")


def fetch_source(
    source: ThemeSource,
    destination_dir: Path,
    force: bool,
    dry_run: bool,
    skip_checksum: bool,
    timeout: int,
) -> str:
    """下载单个样式源。

    :param source: 样式源对象。
    :param destination_dir: 下载目录。
    :param force: 是否强制覆盖。
    :param dry_run: 是否仅演练。
    :param skip_checksum: 是否跳过哈希校验。
    :param timeout: 下载超时时间（秒）。
    :return: 执行结果描述。
    """

    archive_path = destination_dir / build_archive_name(source)

    if archive_path.exists() and not force:
        try:
            ensure_checksum(archive_path, source.sha256, skip_checksum)
            return f"SKIP  {source.name} (已存在且校验通过): {archive_path.name}"
        except Exception as exc:
            return f"WARN  {source.name} (已存在但校验失败，使用 --force 重新下载): {exc}"

    if dry_run:
        return f"PLAN  {source.name} -> {archive_path}"

    with tempfile.TemporaryDirectory(prefix="theme_fetch_") as temp_dir:
        temp_path = Path(temp_dir) / archive_path.name
        download_file(source.url, temp_path, timeout=timeout)
        ensure_checksum(temp_path, source.sha256, skip_checksum)
        destination_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(temp_path), str(archive_path))

    return f"DONE  {source.name} -> {archive_path}"


def main() -> int:
    """脚本主入口。

    :return: 进程退出码，0 表示成功。
    """

    args = parse_args()
    skill_root = resolve_skill_root()

    config_path = args.config or (skill_root / "references" / "theme_sources.json")
    destination_dir = args.dest or (skill_root / "assets" / "theme-cache")

    try:
        sources = load_sources(config_path)
        if args.list:
            print_source_table(sources)
            print("默认策略：屏蔽 GPL/AGPL/LGPL；可用 --allow-copyleft 或 --allow-license 放行。")
            return 0

        selected_sources = select_sources(sources, args.provider, args.all)
        selected_sources, blocked_messages = apply_license_policy(
            selected_sources=selected_sources,
            allow_copyleft=args.allow_copyleft,
            allowed_licenses=args.allow_license,
            blocked_licenses=args.block_license,
        )
        for message in blocked_messages:
            print(message)
        if not selected_sources:
            print("无可下载 provider。可使用 --list 查看，或调整许可证策略后重试。")
            return 2

        for source in selected_sources:
            result = fetch_source(
                source=source,
                destination_dir=destination_dir,
                force=args.force,
                dry_run=args.dry_run,
                skip_checksum=args.skip_checksum,
                timeout=args.timeout,
            )
            print(result)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
