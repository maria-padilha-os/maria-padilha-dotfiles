#!/bin/sh
# Install the Lilith micro configuration into ~/.config/micro.
#
#   micro/install.sh                 link settings.json/bindings.json, seed the
#                                    colourscheme and install the lsp plugin
#   micro/install.sh --no-plugins    skip the network plugin install
#   micro/install.sh --copy          copy the files instead of symlinking them
#
# Safe to run repeatedly. Plugin installation is best effort: an offline run
# still leaves micro with its built-in plugins and prints what is missing.
set -eu

self=$(readlink -f -- "$0" 2>/dev/null || printf '%s' "$0")
src=$(CDPATH='' cd -- "$(dirname -- "$self")" && pwd)
config="${XDG_CONFIG_HOME:-$HOME/.config}/micro"
copy=0
plugins=1

usage() {
    cat <<'EOF'
usage: micro/install.sh [--no-plugins] [--copy]

  --no-plugins  do not run `micro -plugin install lsp`
  --copy        copy settings/bindings instead of symlinking them
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
    --no-plugins) plugins=0 ;;
    --copy) copy=1 ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        printf 'install.sh: unknown argument: %s\n' "$1" >&2
        usage >&2
        exit 2
        ;;
    esac
    shift
done

mkdir -p "$config/colorschemes"

install_file() {
    file=$1
    if [ ! -f "$src/$file" ]; then
        printf 'install.sh: missing %s\n' "$src/$file" >&2
        return 0
    fi

    dst="$config/$file"
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
        backup="$dst.pre-lilith-$(date +%Y%m%d-%H%M%S)"
        printf 'backing up %s -> %s\n' "$dst" "$backup" >&2
        mv "$dst" "$backup"
    fi

    if [ "$copy" -eq 1 ]; then
        [ -L "$dst" ] && rm -f "$dst"
        cp -f "$src/$file" "$dst"
        printf '%s (copy)\n' "$dst"
    else
        ln -sfn "$src/$file" "$dst"
        printf '%s -> %s\n' "$dst" "$src/$file"
    fi
}

install_file settings.json
install_file bindings.json

# The colourscheme is generated state: the theme engine owns this path after
# the first run. Seed the static fallback only when it is not there yet, so a
# later wallpaper change is not clobbered by a login-time bootstrap.
colour="$config/colorschemes/lilith.micro"
if [ -e "$colour" ]; then
    printf 'kept existing %s\n' "$colour"
elif [ -f "$src/colorschemes/lilith.micro" ]; then
    cp "$src/colorschemes/lilith.micro" "$colour"
    printf 'seeded %s\n' "$colour"
else
    printf 'install.sh: missing %s\n' "$src/colorschemes/lilith.micro" >&2
fi

if [ "$plugins" -eq 1 ]; then
    if [ -f "$config/plug/lsp/main.lua" ]; then
        printf 'lsp plugin already installed\n'
    elif ! command -v micro >/dev/null 2>&1; then
        printf 'install.sh: micro is not installed; skipping the lsp plugin\n' >&2
    else
        printf 'installing micro lsp plugin (network; failure is not fatal)\n'
        # micro returns 0 even when the channel cannot be reached, so the
        # check below, not the exit status, decides whether it worked.
        if command -v timeout >/dev/null 2>&1; then
            MICRO_CONFIG_HOME="$config" timeout 60 micro -plugin install lsp || true
        else
            MICRO_CONFIG_HOME="$config" micro -plugin install lsp || true
        fi
        if [ -f "$config/plug/lsp/main.lua" ]; then
            printf 'lsp plugin installed\n'
        else
            printf 'install.sh: lsp plugin not installed (offline?); retry with: micro -plugin install lsp\n' >&2
        fi
    fi
fi
