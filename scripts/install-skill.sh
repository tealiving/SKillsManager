#!/usr/bin/env bash

set -euo pipefail

name=""
force="false"
codex_home=""
repo_root=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      force="true"
      shift
      ;;
    --codex-home)
      codex_home="$2"
      shift 2
      ;;
    --repo-root)
      repo_root="$2"
      shift 2
      ;;
    *)
      if [[ -z "$name" ]]; then
        name="$1"
        shift
      else
        echo "Unexpected argument: $1" >&2
        exit 1
      fi
      ;;
  esac
done

if [[ -z "$name" ]]; then
  echo "Skill name is required." >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "$repo_root" ]]; then
  resolved_repo_root="$(cd "$repo_root" && pwd)"
else
  resolved_repo_root="$(cd "$script_dir/.." && pwd)"
fi

if command -v node >/dev/null 2>&1; then
  node_command="node"
elif command -v node.exe >/dev/null 2>&1; then
  node_command="node.exe"
else
  echo "Node.js runtime is required." >&2
  exit 127
fi

node_repo_root="$resolved_repo_root"
node_codex_home="$codex_home"
entry_script="$resolved_repo_root/bin/codex-skills.mjs"

if [[ "$node_command" == "node.exe" ]]; then
  if [[ "$node_repo_root" =~ ^/mnt/([a-zA-Z])/(.*)$ ]]; then
    drive="${BASH_REMATCH[1]}"
    tail="${BASH_REMATCH[2]//\//\\}"
    node_repo_root="${drive^}:\\$tail"
  fi
  if [[ -n "$node_codex_home" && "$node_codex_home" =~ ^/mnt/([a-zA-Z])/(.*)$ ]]; then
    drive="${BASH_REMATCH[1]}"
    tail="${BASH_REMATCH[2]//\//\\}"
    node_codex_home="${drive^}:\\$tail"
  fi
  entry_script="${node_repo_root}\\bin\\codex-skills.mjs"
fi

arguments=(
  "$entry_script"
  install
  "$name"
  --repo-root
  "$node_repo_root"
)

if [[ -n "$node_codex_home" ]]; then
  arguments+=(--codex-home "$node_codex_home")
fi

if [[ "$force" == "true" ]]; then
  arguments+=(--force)
fi

"$node_command" "${arguments[@]}"
