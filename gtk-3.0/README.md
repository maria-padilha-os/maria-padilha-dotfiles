# GTK 3 settings

`settings.ini` is the only tracked file here. It selects `adw-gtk3-dark`,
Papirus-Dark icons, Noto Sans 10 and the dark preference so Thunar and the
other GTK 3 applications match the Maria Padilha palette.

The colour sheets in this directory (`gtk.css` and `thunar.css`) are generated
by `padilha-theme` in `maria-padilha-de`. They are not tracked here, are
overwritten by the theme engine, and must not be edited. `padilha-dots` links
only `settings.ini`, so applying a theme never writes into this checkout.

See [`../thunar/README.md`](../thunar/README.md) for the complete generated-file
list and the Thunar behaviour.
