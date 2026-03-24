import test from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import { mkdir, mkdtemp, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';

const BIN_PATH = path.resolve(process.cwd(), 'bin', 'codex-skills.mjs');

/**
 * 创建 CLI 测试使用的临时仓库目录。
 * :param {object} options 夹具选项。
 * :param {string} options.skillName skill 名称。
 * :return: Promise<object>
 */
async function createCliFixture(options = {}) {
  const {
    skillName = 'demo-skill'
  } = options;
  const repoRoot = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-cli-'));
  const skillDir = path.join(repoRoot, 'skills', skillName);
  const catalogDir = path.join(repoRoot, 'catalog');
  await mkdir(skillDir, { recursive: true });
  await mkdir(catalogDir, { recursive: true });
  await writeFile(path.join(skillDir, 'SKILL.md'), '# demo', 'utf8');
  await writeFile(
    path.join(catalogDir, 'skills.json'),
    JSON.stringify(
      {
        schemaVersion: 1,
        skills: [
          {
            name: skillName,
            title: 'Demo Skill',
            path: `skills/${skillName}`,
            installable: true,
            channel: 'stable'
          }
        ]
      },
      null,
      2
    ),
    'utf8'
  );
  return { repoRoot, skillName };
}

/**
 * 执行 CLI 并返回结果。
 * :param {string[]} args 参数列表。
 * :return: object
 */
function runCli(args) {
  return spawnSync(process.execPath, [BIN_PATH, ...args], {
    encoding: 'utf8'
  });
}

/**
 * 验证 list 命令会输出 skill 名称。
 * :return: Promise<void>
 */
async function testListCommand() {
  const fixture = await createCliFixture();
  const result = runCli(['list', '--repo-root', fixture.repoRoot]);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /demo-skill/);
}

/**
 * 验证 install 命令会输出目标目录与重启提示。
 * :return: Promise<void>
 */
async function testInstallCommand() {
  const fixture = await createCliFixture();
  const codexHome = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-cli-codex-home-'));
  const result = runCli([
    'install',
    fixture.skillName,
    '--repo-root',
    fixture.repoRoot,
    '--codex-home',
    codexHome
  ]);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /Installed demo-skill/);
  assert.match(result.stdout, /Restart Codex/i);
}

/**
 * 验证 validate 命令会输出合法提示。
 * :return: Promise<void>
 */
async function testValidateCommand() {
  const fixture = await createCliFixture();
  const result = runCli([
    'validate',
    fixture.skillName,
    '--repo-root',
    fixture.repoRoot
  ]);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /is valid/i);
}

test('cli list prints installable skills', testListCommand);
test('cli install prints destination and restart hint', testInstallCommand);
test('cli validate reports skill is valid', testValidateCommand);
