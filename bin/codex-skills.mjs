#!/usr/bin/env node

import { runInstallCommand } from '../lib/commands/install.mjs';
import { runListCommand } from '../lib/commands/list.mjs';
import { runValidateCommand } from '../lib/commands/validate.mjs';

/**
 * 解析命令行参数。
 * :param argv: 原始参数列表。
 * :return: 解析后的命令、位置参数与选项。
 */
function parseCliArguments(argv) {
  const positional = [];
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const current = argv[index];
    if (current === '--repo-root') {
      options.repoRoot = argv[index + 1];
      index += 1;
      continue;
    }
    if (current === '--catalog-path') {
      options.catalogPath = argv[index + 1];
      index += 1;
      continue;
    }
    if (current === '--codex-home') {
      options.codexHome = argv[index + 1];
      index += 1;
      continue;
    }
    if (current === '--force') {
      options.force = true;
      continue;
    }
    positional.push(current);
  }
  return {
    command: positional[0],
    skillName: positional[1],
    options
  };
}

/**
 * 运行 CLI 主流程。
 * :param argv: 命令行参数列表。
 * :return: Promise<number>
 */
export async function main(argv = process.argv.slice(2)) {
  const parsed = parseCliArguments(argv);
  try {
    if (parsed.command === 'list') {
      console.log(await runListCommand(parsed.options));
      return 0;
    }
    if (parsed.command === 'install') {
      if (!parsed.skillName) {
        throw new Error('Skill name is required for install.');
      }
      console.log(await runInstallCommand(parsed.skillName, parsed.options));
      return 0;
    }
    if (parsed.command === 'validate') {
      if (!parsed.skillName) {
        throw new Error('Skill name is required for validate.');
      }
      console.log(await runValidateCommand(parsed.skillName, parsed.options));
      return 0;
    }
    throw new Error('Unknown command. Supported commands: list, install, validate.');
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    return 1;
  }
}

const exitCode = await main();
process.exit(exitCode);
