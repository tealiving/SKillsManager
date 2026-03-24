import { installSkill } from '../install.mjs';

/**
 * 运行 install 命令并返回文本结果。
 * :param skillName: 目标 skill 名称。
 * :param options: install 命令选项。
 * :return: Promise<string>
 */
export async function runInstallCommand(skillName, options = {}) {
  const result = await installSkill(skillName, options);
  return `Installed ${result.name} to ${result.targetDir}\nRestart Codex to pick up new skills.`;
}
