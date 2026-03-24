import test from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import { mkdtemp } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';

const REPO_ROOT = process.cwd();

/**
 * 执行 PowerShell 安装脚本。
 * :param {string} codexHome 临时 Codex Home 目录。
 * :return: object
 */
function runPowerShellInstallScript(codexHome) {
  return spawnSync(
    'powershell',
    [
      '-ExecutionPolicy',
      'Bypass',
      '-File',
      path.join(REPO_ROOT, 'scripts', 'install-skill.ps1'),
      '-Name',
      'git-report-summarizer',
      '-CodexHome',
      codexHome
    ],
    {
      cwd: REPO_ROOT,
      encoding: 'utf8'
    }
  );
}

/**
 * 执行 Bash 安装脚本。
 * :param {string} codexHome 临时 Codex Home 目录。
 * :return: object
 */
function runBashInstallScript(codexHome) {
  return spawnSync(
    'bash',
    [
      './scripts/install-skill.sh',
      'git-report-summarizer',
      '--codex-home',
      codexHome
    ],
    {
      cwd: REPO_ROOT,
      encoding: 'utf8'
    }
  );
}

/**
 * 验证 PowerShell 兜底脚本可完成安装。
 * :return: Promise<void>
 */
async function testPowerShellInstallScript() {
  const codexHome = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-script-ps-'));
  const result = runPowerShellInstallScript(codexHome);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /Installed git-report-summarizer/);
}

/**
 * 验证 Bash 兜底脚本可完成安装。
 * :return: Promise<void>
 */
async function testBashInstallScript() {
  const codexHome = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-script-bash-'));
  const result = runBashInstallScript(codexHome);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /Installed git-report-summarizer/);
}

test('powershell install script installs the target skill', testPowerShellInstallScript);
test('bash install script installs the target skill', testBashInstallScript);
