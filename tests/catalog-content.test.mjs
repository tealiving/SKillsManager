import test from 'node:test';
import assert from 'node:assert/strict';

import { readCatalog } from '../lib/manifest.mjs';

/**
 * 验证 catalog 包含剩余需要归一化导入的技能。
 * :return: Promise<void>
 */
async function testCatalogContainsNormalizedImports() {
  const catalog = await readCatalog();
  const names = new Set(catalog.skills.map((skill) => skill.name));
  assert.ok(names.has('openai-docs'));
  assert.ok(names.has('skill-creator'));
  assert.ok(names.has('skill-installer'));
  assert.ok(names.has('planning-with-files'));
}

test('catalog includes normalized nested skills', testCatalogContainsNormalizedImports);
