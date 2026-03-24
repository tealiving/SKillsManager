import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFile } from 'node:fs/promises';

import { validateCatalog } from './validate.mjs';

const MODULE_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_REPO_ROOT = path.resolve(MODULE_DIR, '..');

/**
 * 返回默认仓库根目录。
 * :return: string
 */
export function getDefaultRepoRoot() {
  return DEFAULT_REPO_ROOT;
}

/**
 * 返回默认 catalog 路径。
 * :param {string} repoRoot 仓库根目录。
 * :return: string
 */
export function getDefaultCatalogPath(repoRoot = getDefaultRepoRoot()) {
  return path.join(repoRoot, 'catalog', 'skills.json');
}

/**
 * 读取并校验 skills catalog。
 * :param {object} options 读取选项。
 * :param {string} options.repoRoot 仓库根目录。
 * :param {string} options.catalogPath catalog 文件路径。
 * :return: Promise<object>
 */
export async function readCatalog(options = {}) {
  const repoRoot = options.repoRoot ?? getDefaultRepoRoot();
  const catalogPath = options.catalogPath ?? getDefaultCatalogPath(repoRoot);
  const content = await readFile(catalogPath, 'utf8');
  const parsed = JSON.parse(content);
  return validateCatalog(parsed, repoRoot);
}
