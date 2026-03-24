import path from 'node:path';
import { access, rm } from 'node:fs/promises';

import { copyDirectory, makeTempDirectory, replaceDirectory, resolveCodexHome } from './fs-utils.mjs';
import { readCatalog } from './manifest.mjs';

/**
 * 判断文件或目录是否存在。
 * :param {string} targetPath 待检查路径。
 * :return: Promise<boolean>
 */
async function exists(targetPath) {
  try {
    await access(targetPath);
    return true;
  } catch {
    return false;
  }
}

/**
 * 按名称查找可安装 skill 条目。
 * :param {string} skillName skill 名称。
 * :param {object} catalog 已读取的 catalog。
 * :return: object
 */
function findInstallableSkill(skillName, catalog) {
  const matchedSkill = catalog.skills.find(
    (skill) => skill.name === skillName && skill.installable === true
  );
  if (!matchedSkill) {
    throw new Error(`Skill "${skillName}" not found or not installable.`);
  }
  return matchedSkill;
}

/**
 * 安装指定 skill 到本地 Codex skills 目录。
 * :param {string} skillName skill 名称。
 * :param {object} options 安装选项。
 * :param {string} options.repoRoot 仓库根目录。
 * :param {string} options.catalogPath catalog 文件路径。
 * :param {string} options.codexHome 显式指定的 Codex Home。
 * :param {boolean} options.force 是否允许覆盖。
 * :return: Promise<object>
 */
export async function installSkill(skillName, options = {}) {
  const catalog = await readCatalog({
    repoRoot: options.repoRoot,
    catalogPath: options.catalogPath
  });
  const skill = findInstallableSkill(skillName, catalog);
  const sourceDir = skill.resolvedPath;
  const skillFile = path.join(sourceDir, 'SKILL.md');
  if (!(await exists(skillFile))) {
    throw new Error(`SKILL.md not found in source directory: ${sourceDir}`);
  }

  const codexHome = resolveCodexHome(options.codexHome);
  const targetDir = path.join(codexHome, 'skills', skill.name);
  if ((await exists(targetDir)) && options.force !== true) {
    throw new Error(`Destination already exists: ${targetDir}`);
  }

  const tempRoot = await makeTempDirectory();
  const stagedDir = path.join(tempRoot, skill.name);
  try {
    await copyDirectory(sourceDir, stagedDir);
    await replaceDirectory(stagedDir, targetDir, options.force === true);
    return {
      name: skill.name,
      sourceDir,
      targetDir,
      codexHome
    };
  } finally {
    await rm(tempRoot, { recursive: true, force: true });
  }
}
