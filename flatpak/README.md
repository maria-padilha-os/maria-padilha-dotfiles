# Flatpak theme overrides

`flatpak/overrides/global` wires Flatpak applications to the same GTK theme as
the host desktop. `padilha-dots flatpak` links it to
`${XDG_DATA_HOME:-$HOME/.local/share}/flatpak/overrides/global`; `padilha-dots`
includes that target in its default run.

The override is **user-scoped**: it lives in the user Flatpak installation and
never uses a system-wide override, privilege escalation or a root-owned path.
It is consumed read-only from the sandbox and can be removed at any time.

## What the override contains

| key | purpose |
| --- | --- |
| `filesystems=/usr/share/themes:ro` | makes `adw-gtk3-dark` visible inside the sandbox |
| `filesystems=/usr/share/icons:ro` | makes Papirus-Dark icons visible inside the sandbox |
| `filesystems=xdg-config/gtk-3.0:ro` | exposes the generated `gtk.css`/`thunar.css` read-only |
| `filesystems=xdg-config/gtk-4.0:ro` | exposes the generated GTK 4 CSS read-only |
| `GTK_THEME=adw-gtk3-dark` | selects the base theme inside the sandbox |
| `GTK_CSD=1` | keeps client-side decorations consistent with the GTK 3 theme |

Flatpak mounts the user config paths `xdg-config/gtk-3.0` and
`xdg-config/gtk-4.0` read-only. `padilha-theme` still owns those directories'
`gtk.css` and `thunar.css` files: this repository never copies, links or edits
the generated sheets.

## What follows the theme

| UI | settings source | notes |
| --- | --- | --- |
| GTK 3 apps (Thunar, dialogs, menus) | `gtk-3.0/settings.ini` and generated `gtk-3.0/gtk.css` | the generated sheet imports `thunar.css` |
| GTK 4 apps without libadwaita | `gtk-4.0/settings.ini` and generated `gtk-4.0/gtk.css` | dialogs, menus and choosers use the same settings |
| GTK file choosers | the host portal or the app's GTK settings | `xdg-desktop-portal-gtk` runs outside the sandbox and uses the host GTK 3 settings |
| Flatpak GTK apps | this override plus the exposed host theme files | restart the app after changing the override |
| gtk-icon-theme-name / gtk-font-name | both `settings.ini` files | font and icon names are shared with GTK 4 |

The generated colour sheets are applied by GTK itself. They are not a named
theme, so the Flatpak override exposes the host config directories rather than
trying to copy the colours into the sandbox.

## Apps that ignore these settings

Some applications do not use GTK, or replace the toolkit's theme:

- **libadwaita applications** ignore `gtk-theme-name` and the custom GTK
  stylesheet. They follow the desktop's dark preference and accent colour from
  the XDG desktop portal (or `org.gnome.desktop.interface` under GNOME). They
  still read the icon theme and font. Forcing `GTK_THEME` on a libadwaita app
  is unsupported and can make its styling inconsistent. If the global override
  does that to one app, unset it only for that app:

  ```sh
  flatpak override --user --unset-env=GTK_THEME org.example.App
  ```
- **Firefox and Thunderbird** use their own chrome CSS; their palette is
  generated separately into the profile (`firefox/user.js` and
  `thunderbird/user.js`).
- **Chromium, Electron and other bundled-toolkit apps** keep their own theme
  engine. Some accept `--force-dark-mode` or an app-specific setting, but they
  do not consume `gtk.css`.
- **Qt/KDE applications** use the Qt style and are outside this GTK override.
- **LibreOffice, Java/Swing, games and apps with a private GTK build** ignore
  the host GTK theme or only partially follow it.

## Reversible removal

Remove only the link managed by this checkout:

```sh
padilha-dots flatpak-reset
```

The command leaves a real (non-symlink) override untouched and never deletes
any other Flatpak data. `padilha-dots flatpak` backs up an existing real
`global` file as `global.pre-padilha-*` before linking.

The equivalent user-scoped Flatpak commands are:

```sh
flatpak override --user --show
flatpak override --user --reset
```

Neither command needs root. If the whole user Flatpak installation is removed,
delete the leftover `~/.local/share/flatpak/overrides/global` link; no system
installation is changed.
