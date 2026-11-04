# Padilha dotfiles

These are the configs Padilha owns, in their own repository. They are linked
into `~/.config`:

| checkout | link |
| --- | --- |
| `hypr` | `~/.config/hypr` |
| `nvim` | `~/.config/nvim` |
| `wezterm` | `~/.config/wezterm` |

`bin/padilha-dots` creates the links. It refuses to replace a real directory,
so on a fresh machine move the existing config aside once and run it.

## Screenshots

| Day | Night |
| --- | --- |
| ![Padilha desktop at day](assets/screenshots/desktop-day.webp) | ![Padilha desktop at night](assets/screenshots/desktop-night.webp) |
| ![Launcher over the wallpaper](assets/screenshots/launcher.webp) | ![Dashboard over a Neovim buffer](assets/screenshots/dashboard.webp) |

![Day and night palette transition](assets/screenshots/palette.gif)

The screenshots are from the Padilha shell and Hyprland configuration in this
repository; the night view is the night palette preview, and the GIF is
generated from the day/night stills.

Local-only files are ignored rather than committed:

- `hypr/hyprland/env.local.lua` — machine secrets (API keys);
- `*.bak` — timestamped backups from config edits;
- `nvim/Session.vim` and `nvim/nvim.log` — Neovim runtime artifacts.

The Hyprland config calls `padilha-session` from the separate `padilha-de`
checkout (installed in `/usr/bin`, or a sibling `../padilha-de/bin`).

