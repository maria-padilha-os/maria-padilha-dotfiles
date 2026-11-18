#!/usr/bin/env bash
# Copy selected MC files to the Wayland clipboard as text/uri-list, and paste
# file-URI lists back into the current panel directory.
set -euo pipefail

mode=${1:-}
shift || true

copy_uris() {
    [ "$#" -gt 0 ] || exit 0
    python3 - "$@" <<'PY' | wl-copy --type text/uri-list
import pathlib
import sys

for raw in sys.argv[1:]:
    path = pathlib.Path(raw).expanduser()
    if path.exists():
        print(path.resolve().as_uri())
PY
}

copy_text() {
    [ "$#" -gt 0 ] || exit 0
    printf '%s\n' "$@" | wl-copy --type text/plain
}

paste_uris() {
    local dest=${1:-$PWD}
    local tmp
    tmp=$(mktemp)
    trap 'rm -f "${tmp:-}"' EXIT

    if ! wl-paste --type text/uri-list >"$tmp" 2>/dev/null || [ ! -s "$tmp" ]; then
        wl-paste --no-newline >"$tmp" 2>/dev/null || {
            printf 'MC clipboard: the clipboard has no file URIs or paths\n' >&2
            exit 1
        }
    fi

    python3 - "$tmp" "$dest" <<'PY'
import pathlib
import shutil
import sys
import urllib.parse

source_file = pathlib.Path(sys.argv[1])
dest = pathlib.Path(sys.argv[2]).expanduser()

for line in source_file.read_text(errors="replace").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("file://"):
        parsed = urllib.parse.urlparse(line)
        if parsed.scheme != "file":
            continue
        path = pathlib.Path(urllib.parse.unquote(parsed.path))
    else:
        path = pathlib.Path(line).expanduser()

    if not path.exists():
        print(f"MC clipboard: missing source: {path}", file=sys.stderr)
        continue

    target = dest / path.name
    if target.exists():
        print(f"MC clipboard: keeping existing: {target}", file=sys.stderr)
        continue

    if path.is_dir():
        shutil.copytree(path, target)
    else:
        shutil.copy2(path, target)
    print(target)
PY
}

case "$mode" in
    copy)
        copy_uris "$@"
        ;;
    copy-text)
        copy_text "$@"
        ;;
    paste)
        paste_uris "$@"
        ;;
    *)
        printf 'usage: %s copy|copy-text|paste [paths...]\n' "$0" >&2
        exit 2
        ;;
esac
