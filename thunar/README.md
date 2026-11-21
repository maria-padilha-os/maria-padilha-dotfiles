# Thunar and GTK integration

This directory owns Thunar's behaviour and its GTK desktop integration. The
colour CSS is generated elsewhere and must not be copied here.

| checkout | destination |
| --- | --- |
| `thunar/thunarrc` | `~/.config/Thunar/thunarrc` (linked) |
| `thunar/uca.xml` | `~/.config/Thunar/uca.xml` (linked) |
| `gtk-3.0/settings.ini` | `~/.config/gtk-3.0/settings.ini` (linked) |
| `gtk-4.0/settings.ini` | `~/.config/gtk-4.0/settings.ini` (linked) |
| `flatpak/overrides/global` | `${XDG_DATA_HOME:-~/.local/share}/flatpak/overrides/global` (linked, user-scoped) |

`padilha-dots thunar` installs the two Thunar files and both GTK settings.
`padilha-dots gtk` installs only the GTK settings, and `padilha-dots flatpak`
installs the user-scoped Flatpak theme override. All three are part of the
default `padilha-dots` run. See [`../flatpak/README.md`](../flatpak/README.md)
for the Flatpak coverage and removal commands.

## Thunar behaviour

`thunarrc` starts Thunar in the detailed list view, sorts by name with folders
first, shows hidden files, and keeps the status bar and location entry visible.
The confirmation options ask before moving files to the trash and before
closing a window with multiple tabs; the permanent-delete menu action is hidden.
`MiscRecursivePermissions` is `ASK` (interactive only, never unconditional) and
recursive search is off.

Thunar 4.20 and newer keep their live preferences in Xfconf and read
`thunarrc` when a profile has no Thunar settings yet (the migration path). On an
existing profile, Xfconf keeps its already-migrated values. This checkout does
not replace the mutable
`~/.config/xfce4/xfconf/xfce-perchannel-xml/thunar.xml`, so a user can change
those values without making the repository dirty.

## Custom actions

`uca.xml` contains two deliberately small actions:

- **Open Terminal Here** - opens the selected directory in WezTerm;
- **Edit in Neovim** - opens the selected item in Neovim inside WezTerm.

Every command uses the single-target `%f` placeholder. There is no
privilege-escalation action, no multi-selection expansion, no shell pipeline
and no recursive command. `tests/thunar_config.py` rejects those patterns.

## Generated files: do not edit

`padilha-theme` in the separate `maria-padilha-de` checkout writes these files
from the current wallpaper/scheme:

- `~/.config/gtk-3.0/gtk.css`
- `~/.config/gtk-3.0/thunar.css`
- `~/.config/gtk-4.0/gtk.css`
- `~/.config/gtk-4.0/thunar.css`
- `~/.local/state/caelestia/scheme.json`

`gtk.css` imports `thunar.css`. Both belong to the theme engine and are
overwritten on every `padilha-theme apply`; edits there are lost. They stay
local and are not tracked in this repository. The tracked
`gtk-3.0/settings.ini` only selects the base GTK theme, Papirus-Dark icons, the
Noto Sans UI font and the dark preference, so Thunar picks up the generated CSS
without this repository ever owning `gtk.css`.

To regenerate the colours:

```sh
padilha-theme apply --wallpaper "$(cat ~/.local/state/caelestia/wallpaper/path.txt)"
```

## Tests

```sh
python3 tests/thunar_config.py
tests/ci.sh
```

The checks parse the INI and XML files, enforce the custom-action safety rules,
verify the generated CSS is absent from the checkout, and exercise the linker
against a scratch `HOME` (including a sentinel `gtk.css` that must survive).
