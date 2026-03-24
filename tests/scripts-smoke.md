# Scripts Smoke Test

## Scope

记录仓库兜底安装脚本的本地烟雾验证结果。

## Commands

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skill.ps1 -Name git-report-summarizer -CodexHome <temp-dir>
```

Bash:

```bash
bash ./scripts/install-skill.sh git-report-summarizer --codex-home <temp-dir>
```

## Latest Local Verification

- 日期：`2026-03-24`
- 验证目标：`git-report-summarizer`
- 预期结果：将 skill 安装到 `<temp-dir>/skills/git-report-summarizer`，并输出重启 Codex 提示
- PowerShell：通过
- Bash：通过
- 备注：Bash 在当前 Windows 环境下通过 `node.exe` 回退执行
