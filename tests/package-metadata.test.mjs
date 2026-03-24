import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { readFile } from 'node:fs/promises';

const PACKAGE_JSON_PATH = path.resolve(process.cwd(), 'package.json');

/**
 * 读取仓库根目录中的 package 元数据。
 * :return: Promise<object>
 */
async function loadPackageMetadata() {
  const content = await readFile(PACKAGE_JSON_PATH, 'utf8');
  return JSON.parse(content);
}

/**
 * 验证发布脚本已声明，便于统一执行本地验收。
 * :return: Promise<void>
 */
async function testReleaseScripts() {
  const packageMetadata = await loadPackageMetadata();
  assert.equal(packageMetadata.scripts['pack:dry-run'], 'npm pack --dry-run');
  assert.equal(packageMetadata.scripts['verify:release'], 'npm test && npm run pack:dry-run');
}

/**
 * 验证 files 白名单仅保留发布所需内容。
 * :return: Promise<void>
 */
async function testPublishedFilesWhitelist() {
  const packageMetadata = await loadPackageMetadata();
  const publishedFiles = new Set(packageMetadata.files);

  assert.ok(publishedFiles.has('README.md'));
  assert.ok(publishedFiles.has('bin'));
  assert.ok(publishedFiles.has('catalog'));
  assert.ok(publishedFiles.has('docs/release-checklist.md'));
  assert.ok(publishedFiles.has('docs/usage'));
  assert.ok(publishedFiles.has('lib'));
  assert.ok(publishedFiles.has('scripts'));
  assert.ok(publishedFiles.has('skills'));
  assert.equal(publishedFiles.has('tests'), false);
  assert.equal(publishedFiles.has('docs/plans'), false);
}

test('package metadata defines release scripts', testReleaseScripts);
test('package metadata whitelists publishable content', testPublishedFilesWhitelist);
