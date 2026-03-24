param(
    [Parameter(Mandatory = $true)]
    [string]$Name,

    [switch]$Force,

    [string]$CodexHome,

    [string]$RepoRoot
)

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$resolvedRepoRoot = if ($RepoRoot) {
    (Resolve-Path $RepoRoot).Path
} else {
    (Resolve-Path (Join-Path $scriptDirectory '..')).Path
}

$arguments = @(
    (Join-Path $resolvedRepoRoot 'bin/codex-skills.mjs'),
    'install',
    $Name,
    '--repo-root',
    $resolvedRepoRoot
)

if ($CodexHome) {
    $arguments += @('--codex-home', $CodexHome)
}

if ($Force) {
    $arguments += '--force'
}

& node @arguments
exit $LASTEXITCODE
