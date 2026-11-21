# GTK 4 settings

`settings.ini` mirrors the tracked GTK 3 settings so GTK 4 dialogs, menus,
file choosers and non-libadwaita applications use the same theme, icons, font
and dark preference.

The generated colour sheets (`gtk.css`, `thunar.css`) stay in this directory at
runtime, are written by `padilha-theme` in `maria-padilha-de`, and are never
tracked or edited here. Libadwaita applications ignore `gtk-theme-name`; see
[`../flatpak/README.md`](../flatpak/README.md) for the supported appearance
path and the full list of applications that ignore GTK theming.

See [`../gtk-3.0/README.md`](../gtk-3.0/README.md) for the shared behaviour and
the Flatpak override.
