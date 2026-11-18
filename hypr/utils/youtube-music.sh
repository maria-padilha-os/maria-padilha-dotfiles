#!/usr/bin/env bash
# Open YouTube Music in a dedicated Firefox window and put it on the music
# special workspace. Firefox may reuse an existing process, so matching the
# window after launch is more reliable than passing a workspace to exec_cmd.
set -euo pipefail

url='https://music.youtube.com/'

find_window() {
    hyprctl clients -j 2>/dev/null |
        jq -r '.[] | select(.class == "firefox" and ((.title | test("YouTube Music")) or .workspace.name == "special:music")) | .address' |
        head -n 1
}

move_to_music() {
    local address=$1
    [ -n "$address" ] || return 0
    hyprctl dispatch "hl.dsp.window.move({ window = \"address:$address\", workspace = \"special:music\" })" >/dev/null 2>&1 || true
}

address=$(find_window)
if [ -n "$address" ]; then
    move_to_music "$address"
    exit 0
fi

before=$(hyprctl clients -j 2>/dev/null | jq -r '.[].address' | sort)
firefox --new-window "$url" >/dev/null 2>&1 &

for _ in $(seq 1 40); do
    clients=$(hyprctl clients -j 2>/dev/null)
    address=$(jq -r '.[] | select(.class == "firefox" and (.title | test("YouTube Music"))) | .address' <<<"$clients" | head -n 1)
    if [ -z "$address" ]; then
        address=$(comm -13 <(printf '%s\n' "$before") <(jq -r '.[] | select(.class == "firefox") | .address' <<<"$clients" | sort) | head -n 1)
    fi
    if [ -n "$address" ]; then
        move_to_music "$address"
        exit 0
    fi
    sleep 0.25
done
