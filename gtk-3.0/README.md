# GTK settings

The tracked settings live in `gtk-3.0/settings.ini` and
`gtk-4.0/settings.ini`. Both select `adw-gtk3-dark`, Papirus-Dark icons, Noto
Sans 10 and the dark preference so Thunar, file choosers, dialogs, menus and
other GTK applications match the Maria Padilha palette.

The colour sheets in these directories (`gtk-3.0/gtk.css`,
`gtk-3.0/thunar.css`, `gtk-4.0/gtk.css` and `gtk-4.0/thunar.css`) are generated
by `padilha-theme` in `maria-padilha-de`. They are not tracked here, are
overwritten by the theme engine, and must not be edited. `padilha-dots` links
only the two `settings.ini` files, so applying a theme never writes into this
checkout.

`padilha-dots gtk` links both settings files; `padilha-dots thunar` links them
too. GTK 3 applications (including Thunar and GTK 3 dialogs, menus and file
choosers) read `gtk-3.0/settings.ini`. GTK 4 applications that do not use
libadwaita read `gtk-4.0/settings.ini`. Libadwaita applications ignore
`gtk-theme-name` and the custom stylesheet; they follow the portal's dark
preference and accent colour instead.

Flatpak applications receive the same theme through the user-scoped
[`../flatpak/overrides/global`](../flatpak/overrides/global) file. It exposes
the host theme, icons and generated config directories read-only and sets
`GTK_THEME`; see [`../flatpak/README.md`](../flatpak/README.md) for the
coverage table, the reversible removal command and the apps that ignore GTK
theming.

See [`../thunar/README.md`](../thunar/README.md) for the complete generated-file
list and the Thunar behaviour.
