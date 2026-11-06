# micro — Maria Padilha's default text editor

Maria Padilha ships [micro](https://micro-editor.github.io/) as the default terminal
editor, with Neovim as the alternative the user can select at install time.
This directory holds the dotfile-side configuration; the palette is rendered
from `maria-padilha-de/share/templates/micro.micro` by the theme engine.

Tested against micro **2.0.15** (Arch `micro` package). The LSP plugin requires
micro >= 2.0.8.

## Install

```sh
# from maria-padilha-dotfiles/
micro/install.sh              # symlink settings/bindings, seed colourscheme,
                              # install the `lsp` plugin (network, best effort)
micro/install.sh --no-plugins # skip the plugin download
micro/install.sh --copy       # copy instead of symlink
```

`padilha-dots micro` calls this helper. The installer (`maria-padilha-de/install.sh`)
runs it during `--full`; the generated colourscheme is not part of the link
because `~/.config/micro` must stay a real directory — the theme engine writes
`~/.config/micro/colorschemes/padilha.micro` there on every palette change.

The helper is idempotent: it backs up an existing real `settings.json` or
`bindings.json` once, replaces symlinks in place, seeds the static fallback only
when no colourscheme exists, and never overwrites a palette generated later.
Plugin installation is skipped when `micro/plug/lsp/main.lua` is already there.
Offline, `micro -plugin install` prints an error but exits 0, so the helper
checks for the plugin directory and warns instead of failing the bootstrap.

## Files

| path | purpose |
| --- | --- |
| `settings.json` | editor defaults and the LSP server map |
| `bindings.json` | LSP shortcuts; overrides micro's `Alt-f` = `WordRight` conflict |
| `colorschemes/padilha.micro` | static fallback colourscheme (current palette) |
| `install.sh` | bootstrap into `~/.config/micro` |

## Settings

The defaults follow the NvChad/nvim setup where micro has an equivalent:

- 4-space indent, tabs expanded to spaces, auto-indent, no autosave
- soft wrap on (word wrap off), cursor line, ruler, scrollbar, line numbers in
  the gutter are not a micro option; the ruler carries line/column
- true colour forced on (`truecolor: "on"`), syntax on, `colorscheme: "padilha"`
- clipboard `external` (Wayland: `wl-copy`), mouse on
- `savecursor`, `saveundo`, `savehistory` and backups on
- search highlight/incremental search, matching-brace highlight, tab-error and
  trailing-whitespace highlight, but **no** automatic `rmtrailingws` (it is
  reported, not silently applied)
- `parsecursor` enabled, so `micro file:12:4` works like a compiler diagnostic

`bindings.json` only fills gaps: micro already binds `F2` save, `F3` find,
`F4` quit, `Ctrl-s`, `Ctrl-q`, `Alt-,`/`Alt-.` for tabs, and
`Ctrl-e` for the command bar. The LSP plugin wants `Alt-k` hover, `Alt-d`
definition, `Alt-f` format, `Alt-r` references and `Ctrl-Space` completion; its
`TryBindKey` refuses to override micro's Emacs `Alt-f` = `WordRight`, so the
binding is set explicitly here. `F5` is bound to `SaveAll`. `Ctrl-Space` is not
listed: its `lspcompletion` command does not exist until the plugin is
installed and micro would print `Unknown command lspcompletion` on startup; the
plugin binds it itself when it loads. The other plugin commands are inert but
harmless while the plugin is missing.

## LSP

micro 2.0.15 has **no built-in LSP client**. LSP comes from the official plugin
channel's `lsp` plugin (`AndCake/micro-plugin-lsp`, installed as version 0.6.2),
which `install.sh` installs into `~/.config/micro/plug/lsp`. It is a
best-effort client: hover, definition, references, formatting, diagnostics and
basic completion, not a full IDE.

The plugin reads these options (all in `settings.json`):

| option | value | meaning |
| --- | --- | --- |
| `lsp.server` | comma list | `<filetype>=<command> [args]` |
| `lsp.formatOnSave` | `false` | format manually with `Alt-f` |
| `lsp.autocompleteDetails` | `false` | suggestions in the status line, not a split |
| `lsp.tabcompletion` | `true` | Tab accepts an LSP completion |

`lsp.server` is keyed by micro's **filetype names**, which are not always the
language name: shell scripts are `shell` (not `bash`), C++ is `c++`, and
`jsonc` is not a separate filetype. The plugin appends its own fallback list,
but the first matching entry wins, so the commands below take precedence.

| micro filetype | server command | Arch package | on this machine |
| --- | --- | --- | --- |
| `c`, `c++`, `objc` | `clangd` | `clang` | **installed** (`/usr/bin/clangd`) |
| `lua` | `lua-language-server` | `lua-language-server` | missing |
| `python` | `pyright-langserver --stdio` | `pyright` | missing |
| `javascript`, `typescript` | `typescript-language-server --stdio` | `typescript-language-server` | missing |
| `go` | `gopls` | `gopls` | missing |
| `rust` | `rust-analyzer` | `rust-analyzer` | missing |
| `shell` | `bash-language-server start` | `bash-language-server` | missing |
| `json` | `vscode-json-language-server --stdio` | npm `vscode-langservers-extracted` | missing |
| `html` | `vscode-html-language-server --stdio` | npm `vscode-langservers-extracted` | missing |
| `css` | `vscode-css-language-server --stdio` | npm `vscode-langservers-extracted` | missing |
| `yaml` | `yaml-language-server --stdio` | `yaml-language-server` | missing |
| `markdown` | `marksman server` | `marksman` | missing |
| `zig` | `zls` | `zls` | missing |
| `php` | `intelephense --stdio` | npm `intelephense` | missing |

On Arch the missing ones that are packaged:

```sh
sudo pacman -S --needed clang lua-language-server pyright \
    typescript-language-server gopls rust-analyzer bash-language-server \
    yaml-language-server marksman zls
```

The HTML/CSS/JSON and PHP servers are not in this machine's sync database; use
npm:

```sh
sudo npm install -g vscode-langservers-extracted intelephense
```

A server only starts when a file of its filetype is opened, so an uninstalled
server costs nothing until then. When it fails, micro logs the spawn error and
the LSP features for that file do nothing; install the package or drop the
entry from `lsp.server`.

The plugin does not implement rename, code actions, workspace symbols or
signature help. `lsp.formatOnSave` stays off because formatters are opinionated;
`Alt-f` formats on demand when the server supports `textDocument/formatting`.

## Colourscheme

`padilha.micro` is a normal micro colourscheme (`color-link` directives with
true-colour hex values). Two copies exist by design:

- `colorschemes/padilha.micro` here is the static fallback, rendered once from
  the current scheme so a fresh clone is never colourless;
- `~/.config/micro/colorschemes/padilha.micro` is generated by
  `padilha-theme apply` from `maria-padilha-de/share/templates/micro.micro` and follows
  every wallpaper/palette change.

The engine entry is already in `maria-padilha-de/lib/apply.lua` (`id = "micro"`,
destination `micro/colorschemes/padilha.micro`, `hash = true`); the template
writes bare `rrggbb` placeholders and the engine adds `#`. After a palette
change, micro picks the colours up on restart (or `Ctrl-e` →
`set colorscheme padilha`).

The syntax colours mirror `nvim/colors/caelestia.lua`: comments use
`onSurfaceVariant`, strings `green`, numbers/constants `peach`, keywords
`primary`, functions `yellow`, types `blue`, operators `red`, preprocessors
`pink`, and special characters `teal`. Chrome uses the Material surface
containers so the editor sits in the same palette as the bar and terminal.

## Switching to Neovim

At install time:

```sh
./install.sh --editor nvim
```

That selects Neovim as `EDITOR`/`VISUAL` and as the `text/plain` handler while
keeping micro installed as the OS default fallback. To switch by hand:

```sh
xdg-mime default nvim.desktop text/plain
printf 'EDITOR=nvim\nVISUAL=nvim\n' > ~/.config/environment.d/90-padilha-editor.conf
```

Switch back with `micro.desktop` and `EDITOR=micro`. `~/.config/nvim` is linked
by `padilha-dots nvim` (or the full installer), independently of which editor is
the default.

## Limitations

- The LSP client is a third-party plugin, not part of micro; the first bootstrap
  needs the network for `micro -plugin install lsp`. An air-gapped image should
  vendor the plugin zip or pre-seed `~/.config/micro/plug/lsp`.
- Plugin 0.6.2 is the latest on the official channel, even though upstream's
  `main.lua` reports 0.6.3; do not hand-install the git version.
- `lsp.formatOnSave` is deliberately off; `Alt-f` is the manual path.
- The colourscheme has no transparency (it sets a background); the WezTerm
  opacity still blends it with the wallpaper.
- No GLSL/Java/Kotlin server is configured because no packaged server is
  available in this snapshot; add a line to `lsp.server` if one is installed.
