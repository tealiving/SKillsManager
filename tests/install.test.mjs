import test from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import {
  access,
  mkdir,
  mkdtemp,
  readFile,
  writeFile
} from 'node:fs/promises';

import { installSkill } from '../lib/install.mjs';

/**
 * 创建用于安装测试的临时仓库。
 * :param {object} options 测试目录选项。
 * :param {string} options.skillName skill 名称。
 * :param {boolean} options.includeSkillFile 是否写入 SKILL.md。
 * :return: Promise<object>
 */
async function createInstallFixture(options = {}) {
  const {
    skillName = 'demo-skill',
    includeSkillFile = true
  } = options;
  const repoRoot = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-install-'));
  const skillDir = path.join(repoRoot, 'skills', skillName);
  const catalogDir = path.join(repoRoot, 'catalog');
  await mkdir(skillDir, { recursive: true });
  await mkdir(catalogDir, { recursive: true });
  if (includeSkillFile) {
    await writeFile(path.join(skillDir, 'SKILL.md'), '# demo', 'utf8');
  }
  await writeFile(
    path.join(catalogDir, 'skills.json'),
    JSON.stringify(
      {
        schemaVersion: 1,
        skills: [
          {
            name: skillName,
            path: `skills/${skillName}`,
            installable: true
          }
        ]
      },
      null,
      2
    ),
    'utf8'
  );
  return { repoRoot, skillDir };
}

/**
 * 验证缺失目标 skill 时会抛出错误。
 * :return: Promise<void>
 */
async function testInstallRejectsMissingSkill() {
  const fixture = await createInstallFixture();
  const codexHome = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-codex-home-'));
  await assert.rejects(
    installSkill('missing-skill', { repoRoot: fixture.repoRoot, codexHome }),
    /not found/
  );
}

/**
 * 验证缺失 SKILL.md 时会抛出错误。
 * :return: Promise<void>
 */
async function testInstallRejectsDirectoryWithoutSkillFile() {
  const fixture = await createInstallFixture({ includeSkillFile: false });
  const codexHome = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-codex-home-'));
  await assert.rejects(
    installSkill('demo-skill', { repoRoot: fixture.repoRoot, codexHome }),
    /SKILL\.md/
  );
}

/**
 * 验证目标目录已存在且未传 force 时会抛出错误。
 * :return: Promise<void>
 */
async function testInstallRejectsExistingDestinationWithoutForce() {
  const fixture = await createInstallFixture();
  const codexHome = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-codex-home-'));
  const targetDir = path.join(codexHome, 'skills', 'demo-skill');
  await mkdir(targetDir, { recursive: true });
  await assert.rejects(
    installSkill('demo-skill', { repoRoot: fixture.repoRoot, codexHome }),
    /already exists/
  );
}

/**
 * 验证可安装到自定义 CODEX_HOME。
 * :return: Promise<void>
 */
async function testInstallUsesExplicitCodexHome() {
  const fixture = await createInstallFixture();
  const codexHome = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-codex-home-'));
  const result = await installSkill('demo-skill', { repoRoot: fixture.repoRoot, codexHome });
  const targetFile = path.join(codexHome, 'skills', 'demo-skill', 'SKILL.md');
  await access(targetFile);
  const content = await readFile(targetFile, 'utf8');
  assert.equal(result.targetDir, path.join(codexHome, 'skills', 'demo-skill'));
  assert.equal(content, '# demo');
}

test('installSkill rejects unknown skills', testInstallRejectsMissingSkill);
test('installSkill rejects directories without SKILL.md', testInstallRejectsDirectoryWithoutSkillFile);
test('installSkill rejects existing destinations without force', testInstallRejectsExistingDestinationWithoutForce);
test('installSkill installs into explicit CODEX_HOME', testInstallUsesExplicitCodexHome);
