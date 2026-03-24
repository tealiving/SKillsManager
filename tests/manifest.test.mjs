import test from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';

import { readCatalog } from '../lib/manifest.mjs';

/**
 * 创建临时仓库根目录和 catalog 文件。
 * :param {object} catalogData 要写入的 catalog 对象。
 * :return: Promise<object>
 */
async function createCatalogFixture(catalogData) {
  const repoRoot = await mkdtemp(path.join(os.tmpdir(), 'skills-manager-manifest-'));
  const catalogDir = path.join(repoRoot, 'catalog');
  const catalogPath = path.join(catalogDir, 'skills.json');
  await mkdir(catalogDir, { recursive: true });
  await writeFile(catalogPath, JSON.stringify(catalogData, null, 2), 'utf8');
  return { repoRoot, catalogPath };
}

/**
 * 验证缺失 skills 字段时会抛出错误。
 * :return: Promise<void>
 */
async function testRejectsCatalogWithoutSkills() {
  const fixture = await createCatalogFixture({ schemaVersion: 1 });
  await assert.rejects(
    readCatalog({ repoRoot: fixture.repoRoot, catalogPath: fixture.catalogPath }),
    /skills/
  );
}

/**
 * 验证缺失必要字段的 skill 条目会抛出错误。
 * :return: Promise<void>
 */
async function testRejectsSkillWithoutRequiredFields() {
  const fixture = await createCatalogFixture({
    schemaVersion: 1,
    skills: [{ name: 'demo-skill', installable: true }]
  });
  await assert.rejects(
    readCatalog({ repoRoot: fixture.repoRoot, catalogPath: fixture.catalogPath }),
    /path/
  );
}

/**
 * 验证越界路径会被拒绝。
 * :return: Promise<void>
 */
async function testRejectsSkillPathTraversal() {
  const fixture = await createCatalogFixture({
    schemaVersion: 1,
    skills: [
      {
        name: 'demo-skill',
        path: '../outside',
        installable: true
      }
    ]
  });
  await assert.rejects(
    readCatalog({ repoRoot: fixture.repoRoot, catalogPath: fixture.catalogPath }),
    /outside repo root/
  );
}

test('readCatalog rejects catalog without skills field', testRejectsCatalogWithoutSkills);
test('readCatalog rejects skill entries without required fields', testRejectsSkillWithoutRequiredFields);
test('readCatalog rejects skill path traversal', testRejectsSkillPathTraversal);
