import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';

/**
 * 返回执行 npm 所需的命令与参数前缀。
 * :return: object
 */
function getNpmInvocation() {
  if (process.env.npm_execpath) {
    return {
      command: process.execPath,
      prefixArgs: [process.env.npm_execpath]
    };
  }

  return {
    command: process.platform === 'win32' ? 'npm.cmd' : 'npm',
    prefixArgs: []
  };
}

/**
 * 执行 npm pack 干跑并返回 JSON 结果。
 * :return: object
 */
function runPackDryRunJson() {
  const npmInvocation = getNpmInvocation();
  const result = spawnSync(
    npmInvocation.command,
    [...npmInvocation.prefixArgs, 'pack', '--dry-run', '--json'],
    {
      cwd: process.cwd(),
      encoding: 'utf8'
    }
  );

  assert.equal(result.status, 0, result.stderr || result.stdout);
  return JSON.parse(result.stdout)[0];
}

/**
 * 验证发布包不会包含缓存目录与开发测试目录。
 * :return: void
 */
function testPackedFilesExcludeCachesAndTests() {
  const packResult = runPackDryRunJson();
  const packedPaths = packResult.files.map((file) => file.path);

  assert.equal(
    packedPaths.some((filePath) => filePath.includes('.pytest_cache')),
    false
  );
  assert.equal(
    packedPaths.some((filePath) => filePath.includes('__pycache__')),
    false
  );
  assert.equal(
    packedPaths.some((filePath) => filePath.endsWith('.pyc')),
    false
  );
  assert.equal(
    packedPaths.some((filePath) => filePath.startsWith('tests/')),
    false
  );
  assert.equal(
    packedPaths.some((filePath) => filePath.startsWith('docs/plans/')),
    false
  );
  assert.equal(
    packedPaths.some((filePath) => filePath.includes('/tests/')),
    false
  );
}

test('pack dry-run excludes caches and test-only content', testPackedFilesExcludeCachesAndTests);
