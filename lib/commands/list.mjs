import { readCatalog } from '../manifest.mjs';

/**
 * 运行 list 命令并返回文本结果。
 * :param options: list 命令选项。
 * :return: Promise<string>
 */
export async function runListCommand(options = {}) {
  const catalog = await readCatalog(options);
  const installableSkills = catalog.skills.filter((skill) => skill.installable === true);
  if (installableSkills.length === 0) {
    return 'No installable skills found.';
  }
  const lines = installableSkills.map((skill) => {
    const titleSuffix = skill.title ? ` - ${skill.title}` : '';
    const channelSuffix = skill.channel ? ` [${skill.channel}]` : '';
    return `- ${skill.name}${channelSuffix}${titleSuffix}`;
  });
  return lines.join('\n');
}
