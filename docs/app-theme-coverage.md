# Application theme coverage

This audit covers the applications Maria Padilha can theme from the tracked
dotfiles and from the generated palette in `maria-padilha-de`. It was checked
against the running host on 2026-11-21: `command -v`, the tracked/live configs,
and `flatpak list --app` (no Flatpak applications are installed here).

Status vocabulary:

- **Themed** — the normal application UI follows the current Material You
  palette.
- **Partially themed** — only some surfaces follow it, or a manual step is
  required, or the app only follows the palette after `padilha-theme apply`.
- **Impossible** — the application has no supported theme interface, or a
  sandbox/permission boundary prevents a dotfiles-only fix.

## Coverage table

| Application | Status | Source of the theme | Exact gap |
| --- | --- | --- | --- |
| Firefox | Themed (scoped) | `firefox/user.js`, `firefox/chrome/userChrome.css`, `firefox/chrome/userContent.css`; `maria-padilha-de/share/templates/firefox.css` → `<profile>/chrome/lilith.css` | Chrome, tabs, menus, sidebar, find bar and the scoped internal pages are themed. Web pages, `about:preferences`, `about:addons`, `about:config`, devtools and the PDF viewer intentionally keep Firefox's native styling. A full restart is required after a palette change. |
| Thunar | Themed (GTK 3) | `thunar/thunarrc`, `thunar/uca.xml`, `gtk-3.0/settings.ini`, `gtk-4.0/settings.ini`; generated `gtk-3.0/thunar.css` and `gtk-4.0/thunar.css` | An existing Thunar profile lives in Xfconf, which wins over `thunarrc`; the tracked file is the migration/default path. `settings.ini` pins the `adw-gtk3-dark` base theme, so a light palette relies on the engine's `--dconf` switch (or the generated CSS) for the base theme. Template/theme generation is owned by `maria-padilha-de`. |
| GTK / Flatpak | Partially themed | Generated `gtk-3.0/gtk.css`, `gtk-3.0/thunar.css`, `gtk-4.0/gtk.css`, `gtk-4.0/thunar.css`; tracked `gtk-3.0/settings.ini` and `gtk-4.0/settings.ini` | Native GTK 3, GTK 4 and libadwaita apps see the host stylesheets. A Flatpak app has its own `~/.var/app/<id>/config` and often its own runtime theme; it does not see the host `~/.config/gtk-*` files. Fixing that needs a per-app `flatpak override` (or the XDG settings portal), which writes outside this checkout and is therefore not committed. No Flatpak app is installed on this host. |
| btop | Themed | `btop/btop.conf` selects `caelestia`; new tracked fallback `btop/themes/caelestia.theme`; generated `~/.config/btop/themes/caelestia.theme` from `share/templates/btop.theme` | Before this change a fresh clone pointed at a theme file that only existed after `padilha-theme apply`, so btop silently used its default palette. The fallback is now copied only when the generated theme is absent; btop needs a restart or `SIGUSR2` to reload. |
| cava | Themed after apply | `maria-padilha-de/share/templates/cava.conf` → `~/.config/cava/config`; new tracked fallback `cava/config` | Cava has no include mechanism for a colour-only fragment, so the engine writes the whole config and the dotfiles cannot symlink it. The new fallback is seeded once, only when no config exists, and is never overwritten after that. Reload with `SIGUSR2` or restart cava. |
| fuzzel | Themed after apply | `maria-padilha-de/share/templates/fuzzel.ini` → `~/.config/fuzzel/fuzzel.ini`; new tracked fallback `fuzzel/fuzzel.ini` | Same whole-file constraint as cava. The fallback is seeded once and fuzzel reads it on the next launch; an already-generated file is left untouched. |
| micro | Themed | `micro/settings.json`, `micro/bindings.json`, static `micro/colorschemes/padilha.micro`; generated `~/.config/micro/colorschemes/padilha.micro` from `share/templates/micro.micro` | The tracked fallback follows `hypr/scheme/current.lua`, so a fresh clone without an apply still matches the tracked palette; the installer seeds it only when no generated colourscheme exists. |
| Midnight Commander | Themed after apply | `mc/ini` (`skin=caelestia`), `mc/mc.keymap`, `mc/mc.ext.ini`, `mc/menu`; generated `~/.local/share/mc/skins/caelestia.ini` from `share/templates/mc-skin.ini` | The skin is generated in `maria-padilha-de` by design and is not tracked here. Before the first apply MC falls back to its stock skin; upstream MC does not reload a skin after a palette change (the Maria Padilha fork reloads on `SIGUSR1`). No dotfiles file can replace the generated skin without breaking the generator's ownership. |
| Spotify / Spicetify | Partially themed | `maria-padilha-de/share/templates/spicetify-{dark,light}.ini` → `~/.config/spicetify/Themes/caelestia/color.ini`; new tracked `spicetify/config-xpui.ini` and fallback `spicetify/Themes/caelestia/color.ini` | Only the palette file is generated; Spotify's own UI is unthemed without Spicetify, and the user must run `spicetify apply` after every palette change. The new config and fallback are seeded only for a missing Spicetify setup and are never linked, because Spicetify rewrites its config. Album art, canvas and lyrics keep their own colours. |
| Discord | Partially themed / impossible by official means | Opt-in static `discord/theme.css`; optional `maria-padilha-de/share/templates/discord.scss` → `<client-mod>/themes/caelestia.theme.css` when `enableDiscord = true` | Discord has no supported arbitrary-CSS API. A third-party client mod (Vencord/BetterDiscord) is required and is against Discord's Terms of Service; this repository never installs, links or patches it. On this host the client-mod themes are stale legacy “Midnight (Caelestia)” files with a remote `@import`, not output from the current self-contained template. Generated palette updates still need a manual client restart. |
| Thunderbird | Themed | `thunderbird/user.js`, `thunderbird/chrome/*.css`; generated `<profile>/chrome/padilha.css` from `share/templates/thunderbird.css` | The generated palette needs a Thunderbird restart; mail content and remote images are not restyled. |
| WezTerm | Themed | `wezterm/wezterm.lua` reads `~/.local/state/caelestia/scheme.json` and falls back to tracked `hypr/scheme/current.lua` | A palette change needs a config reload; `padilha-theme` touches the config so WezTerm's automatic reload picks it up. |
| Neovim | Themed (opt-in) | `nvim/colors/caelestia.lua` and `nvim/lua/themes/caelestia.lua`, selected by `vim.g.caelestia_colorscheme`; the default NvChad/base46 theme is independent | Caelestia is opt-in. Base46 is not tied to the generated scheme. Transparency stays off by design. |
| lazygit | Themed | `lazygit/config.yml` uses the terminal ANSI palette | It follows the terminal's 16-colour palette rather than reading the generated scheme directly; a palette change needs the terminal/WezTerm reload first. |
| dsh-tui | Themed when installed | `dsh-tui/themes/*.json` and `dsh-tui/plugin`; `padilha-dots dsh-tui` installs them | It is not part of the default `padilha-dots` run; without the theme plugin it keeps the runtime default. |
| Other GTK apps (GIMP, LibreOffice, Audacious, viewnior, galculator, Evince, etc.) | Partially themed | Generated GTK 3/4 CSS plus `settings.ini` | Apps that ship their own theme or hard-coded colours (GIMP's `theme.css`, some LibreOffice surfaces) only partially follow the palette. Flatpak copies are subject to the sandbox gap above. |
| Other Qt apps (VLC, Qt tools) | Partially themed | Generated `~/.config/qtengine/caelestia.colors` and `config.json` from `share/templates/qt*.colors` | The host has `qt5ct` configured with Kvantum's `Matcha` style, which can override the generated qtengine colours. Each app must select `QT_QPA_PLATFORMTHEME=qtengine`; Qt Flatpaks may bundle their own platform theme. |
| Electron / Chromium apps (Obsidian, Todoist, YouTube Music, Bitwarden, Chromium, Steam) | Partially themed / impossible for web surfaces | Each app's own light/dark setting; Chromium may follow the GTK frame | There is no supported global palette injection. Forcing CSS would require patching app resources, a client mod, or a browser policy; those are outside this checkout and not added here. Zed's local `~/.config/zed/themes/caelestia.json` is a stale static theme, not generated by the current palette. |

## Dotfiles-side fixes in this change

- `cava/config`, `fuzzel/fuzzel.ini`, `btop/themes/caelestia.theme`,
  `spicetify/config-xpui.ini` and
  `spicetify/Themes/caelestia/color.ini` are tracked fallbacks for files the
  theme engine owns after the first apply. `bin/padilha-dots` copies them only
  when the destination is missing, so a later `padilha-theme apply` never
  writes into this checkout.
- `gtk-4.0/settings.ini` is now tracked and linked alongside the GTK 3
  settings. Only `settings.ini` is linked; the generated `gtk.css` and
  `thunar.css` files remain local.
- `micro/colorschemes/padilha.micro` is refreshed to match the tracked
  palette.
- `btop/themes/caelestia.theme` gives btop a palette before the first apply.
- The coverage tests in `tests/app_theme_config.py` and the scratch-home checks
  in `tests/ci.sh` pin the new paths and the seed-only behaviour.

## Verification

Run the static and scratch-home checks:

```sh
python3 tests/app_theme_config.py
tests/ci.sh
```

Then use the visual checklist in
[`app-theme-visual-checklist.md`](app-theme-visual-checklist.md).
