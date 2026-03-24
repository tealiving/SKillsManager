import path from 'node:path';

/**
 * 判断目标路径是否位于根目录内。
 * :param {string} rootPath 根目录绝对路径。
 * :param {string} candidatePath 候选绝对路径。
 * :return: boolean
 */
function isPathInsideRoot(rootPath, candidatePath) {
  const relativePath = path.relative(rootPath, candidatePath);
  return relativePath === '' || (!relativePath.startsWith('..') && !path.isAbsolute(relativePath));
}

/**
 * 校验单个 skill 条目并返回标准化结果。
 * :param {object} skill 原始 skill 条目。
 * :param {string} repoRoot 仓库根目录。
 * :return: object
 */
function validateSkillEntry(skill, repoRoot) {
  if (!skill || typeof skill !== 'object') {
    throw new Error('Invalid skill entry: entry must be an object.');
  }
  if (!skill.name || typeof skill.name !== 'string') {
    throw new Error('Invalid skill entry: name is required.');
  }
  if (!skill.path || typeof skill.path !== 'string') {
    throw new Error(`Invalid skill entry for ${skill.name}: path is required.`);
  }
  if (typeof skill.installable !== 'boolean') {
    throw new Error(`Invalid skill entry for ${skill.name}: installable must be boolean.`);
  }
  const resolvedPath = path.resolve(repoRoot, skill.path);
  if (!isPathInsideRoot(repoRoot, resolvedPath)) {
    throw new Error(`Invalid skill entry for ${skill.name}: path resolves outside repo root.`);
  }
  return {
    ...skill,
    resolvedPath
  };
}

/**
 * 校验 catalog 结构并返回标准化结果。
 * :param {object} catalog 原始 catalog 对象。
 * :param {string} repoRoot 仓库根目录。
 * :return: object
 */
export function validateCatalog(catalog, repoRoot) {
  if (!catalog || typeof catalog !== 'object') {
    throw new Error('Invalid catalog: expected an object.');
  }
  if (!Array.isArray(catalog.skills)) {
    throw new Error('Invalid catalog: skills field is required.');
  }
  return {
    schemaVersion: typeof catalog.schemaVersion === 'number' ? catalog.schemaVersion : 1,
    skills: catalog.skills.map((skill) => validateSkillEntry(skill, repoRoot))
  };
}
