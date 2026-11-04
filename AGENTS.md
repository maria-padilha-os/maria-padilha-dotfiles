# AGENTS.md — padilha-dotfiles

Read `/home/machine/Códigos/padilha/AGENTS.md` first; this is the repo-specific
summary.

Scope: Hyprland (`hypr/`), Neovim (`nvim/`), WezTerm (`wezterm/`), and the
static Midnight Commander files (`mc/`). These are linked into
`~/.config/{hypr,nvim,wezterm}` and the selected files under `~/.config/mc`.
The generated caelestia MC skin stays in `padilha-de`.

## Safety

- Do not commit `hypr/hyprland/env.local.lua`; it contains the real DeepSeek
  key and is ignored.
- Suspend is broken: do not restore `systemctl suspend`/`hibernate`; the
  `Super+Shift+Escape` binding intentionally shows a notice.
- The shell lock is unstable: automatic idle locking is disabled. Do not add
  `qs ... lock lock` to `hypridle.conf`.
- Live edits affect the running session. Validate Lua before reloading:

  ```sh
  lua -e 'assert(loadfile("hypr/variables.lua"))'
  hyprctl reload
  hyprctl configerrors
  ```

- Generated `hypr/scheme/current.lua` is tracked so a fresh clone has a valid
  palette; commit it when a palette change is part of the change.

## Commands

```sh
lua -e 'assert(loadfile("hypr/hyprland/execs.lua"))'
hyprctl reload && hyprctl configerrors
nvim --headless '+checkhealth' '+qa'   # if diagnosing Neovim
```

## Style

- Hyprland config is Lua (`hl.bind`, `hl.window_rule`, `hl.dsp`), not the old
  keyword format.
- Neovim follows NvChad/base46; caelestia is opt-in via
  `vim.g.caelestia_colorscheme`. Keep `transparency = false` unless deliberately
  changing the terminal layering.
- WezTerm owns `window_background_opacity = 0.85`; Hyprland's WezTerm rule uses
  `1.0 override` so the compositor does not multiply it.
- Screenshots/GIFs: never capture the DSH terminal, Firefox, or private windows.
  Use a dedicated empty workspace, verify it, inspect frames, and prefer stills
  or GIFs generated from those stills over live screen recording.
