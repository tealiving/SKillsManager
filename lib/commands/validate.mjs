import path from 'node:path';
import { access } from 'node:fs/promises';

import { readCatalog } from '../manifest.mjs';

/**
 * 按名称查找目标 skill。
 * :param skillName: 目标 skill 名称。
 * :param catalog: 已读取的 catalog。
 * :return: object
 */
function findSkill(skillName, catalog) {
  const matchedSkill = catalog.skills.find((skill) => skill.name === skillName);
  if (!matchedSkill) {
    throw new Error(`Skill "${skillName}" not found.`);
  }
  return matchedSkill;
}

/**
 * 运行 validate 命令并返回文本结果。
 * :param skillName: 目标 skill 名称。
 * :param options: validate 命令选项。
 * :return: Promise<string>
 */
export async function runValidateCommand(skillName, options = {}) {
  const catalog = await readCatalog(options);
  const skill = findSkill(skillName, catalog);
  const skillFile = path.join(skill.resolvedPath, 'SKILL.md');
  await access(skillFile);
  return `Skill "${skill.name}" is valid at ${skill.resolvedPath}.`;
}
