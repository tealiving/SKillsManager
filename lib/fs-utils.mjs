import os from 'node:os';
import path from 'node:path';
import { cp, mkdir, mkdtemp, rename, rm } from 'node:fs/promises';

/**
 * 解析本地 Codex Home 目录。
 * :param {string | undefined} explicitCodexHome 显式指定的 Codex Home。
 * :return: string
 */
export function resolveCodexHome(explicitCodexHome) {
  return explicitCodexHome ?? process.env.CODEX_HOME ?? path.join(os.homedir(), '.codex');
}

/**
 * 创建临时工作目录。
 * :param {string} prefix 临时目录前缀。
 * :return: Promise<string>
 */
export async function makeTempDirectory(prefix = 'codex-skill-') {
  return mkdtemp(path.join(os.tmpdir(), prefix));
}

/**
 * 复制目录到目标位置。
 * :param {string} sourceDir 源目录。
 * :param {string} targetDir 目标目录。
 * :return: Promise<void>
 */
export async function copyDirectory(sourceDir, targetDir) {
  await cp(sourceDir, targetDir, { recursive: true });
}

/**
 * 用暂存目录替换目标目录。
 * :param {string} stagedDir 暂存目录。
 * :param {string} targetDir 目标目录。
 * :param {boolean} force 是否允许覆盖。
 * :return: Promise<void>
 */
export async function replaceDirectory(stagedDir, targetDir, force = false) {
  if (force) {
    await rm(targetDir, { recursive: true, force: true });
  }
  await mkdir(path.dirname(targetDir), { recursive: true });
  await rename(stagedDir, targetDir);
}
