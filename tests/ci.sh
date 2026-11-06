#!/usr/bin/env bash
# Contract tests for the dotfiles checkout. No live session is needed: the
# linker is exercised against a scratch HOME, and the Hyprland config is only
# parsed, not loaded.
set -uo pipefail

root=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
dots="$root/bin/padilha-dots"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

pass=0
fail=0
ok() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
bad() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; [ -n "${2:-}" ] && printf '       %s\n' "$2"; }

echo "syntax"

while IFS= read -r -d '' file; do
    if lua -e "assert(loadfile('$file'))"; then
        ok "lua parse ${file#"$root"/}"
    else
        bad "lua parse ${file#"$root"/}"
    fi
done < <(find "$root/hypr" -name '*.lua' -print0)

for file in "$dots" "$root/micro/install.sh"; do
    if sh -n "$file"; then
        ok "sh -n ${file#"$root"/}"
    else
        bad "sh -n ${file#"$root"/}"
    fi
done

if command -v shellcheck >/dev/null 2>&1; then
    if shellcheck --severity=warning "$dots" "$root/micro/install.sh"; then
        ok "shellcheck"
    else
        bad "shellcheck"
    fi
fi

echo "json"

while IFS= read -r -d '' file; do
    if python3 -m json.tool <"$file" >/dev/null 2>&1; then
        ok "json ${file#"$root"/}"
    else
        bad "json ${file#"$root"/}"
    fi
done < <(find "$root" -path "$root/.git" -prune -o -name '*.json' -print0)

echo "linking"

home="$tmp/home"
mkdir -p "$home/.config"
if HOME="$home" XDG_CONFIG_HOME="$home/.config" "$dots" hypr nvim wezterm mc >/dev/null 2>&1; then
    ok "padilha-dots links a scratch config"
else
    bad "padilha-dots links a scratch config"
fi

for name in hypr nvim wezterm; do
    if [ -L "$home/.config/$name" ]; then
        ok "$name is a symlink"
    else
        bad "$name is a symlink"
    fi
done

mc_ini="$home/.config/mc/ini"
if [ -f "$mc_ini" ] && [ ! -L "$mc_ini" ]; then
    ok "mc ini is copied"
else
    bad "mc ini is copied"
fi
if [ -L "$home/.config/mc/mc.keymap" ]; then
    ok "mc keymap is linked"
else
    bad "mc keymap is linked"
fi

printf '\n[local-test]\nvalue=keep\n' >>"$mc_ini"
HOME="$home" XDG_CONFIG_HOME="$home/.config" "$dots" mc >/dev/null 2>&1
if grep -q '^value=keep$' "$mc_ini"; then
    ok "a local mc change is kept"
else
    bad "a local mc change is kept"
fi

if HOME="$tmp/no-profile" XDG_CONFIG_HOME="$tmp/no-profile/.config" "$dots" firefox >/dev/null 2>&1; then
    ok "firefox without a profile is not an error"
else
    bad "firefox without a profile is not an error"
fi

if HOME="$tmp/micro" XDG_CONFIG_HOME="$tmp/micro/.config" "$root/micro/install.sh" --no-plugins >/dev/null 2>&1; then
    ok "micro installer runs without plugins"
else
    bad "micro installer runs without plugins"
fi
if [ -L "$tmp/micro/.config/micro/settings.json" ]; then
    ok "micro settings are linked"
else
    bad "micro settings are linked"
fi

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
