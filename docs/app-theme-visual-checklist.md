# Application theme visual checklist

Use this after a palette apply (`padilha-theme apply --wallpaper ...`). Run the
static checks first:

```sh
python3 tests/app_theme_config.py
tests/ci.sh
```

Test both a light and a dark palette. For each mode, restart the app or reload
it as noted; GTK, Qt, Firefox, Thunderbird, Discord and micro do not all
hot-reload.

## Firefox and Thunderbird

- [ ] Firefox: the tab strip, address bar, toolbar hover states, hamburger
      menu, context menu, downloads panel, sidebar (`Ctrl+B`) and find bar
      (`Ctrl+F`) use the current surfaces and readable text.
- [ ] Firefox: a new tab, `about:blank`, `about:privatebrowsing`,
      `about:sessionrestore` and `about:welcome` follow the palette; an
      ordinary website keeps its own CSS.
- [ ] Firefox: `about:preferences`, `about:addons` and devtools keep the native
      Firefox styling by design.
- [ ] Firefox: focus visibly moves through the address bar, toolbar, menus and
      sidebar; no focused control disappears into its background.
- [ ] Thunderbird: the folder tree, message list, preview pane, menus and
      compose window use the palette after a restart.

## Thunar, GTK and Flatpak

- [ ] Thunar: window, headerbar, sidebar, list view, location entry, menus,
      tooltips, file chooser, selected row and disabled controls are readable.
- [ ] Open a GTK 3 app, a GTK 4 app and a libadwaita app. Window, headerbar,
      sidebar, card, dialog, popover and menu backgrounds follow the palette.
- [ ] Hover and focus a tooltip, menu row and disabled label; the disabled
      text stays readable rather than fading below body contrast.
- [ ] Tab through a dialog and file chooser; every stop has a visible primary
      focus ring, including a selected row.
- [ ] If a Flatpak app is installed, confirm whether it sees the palette via
      the XDG settings portal. If it ignores the host config, record the app id
      and report the sandbox gap instead of copying files into `~/.var/app`.
- [ ] Confirm `~/.config/gtk-3.0/settings.ini` and
      `~/.config/gtk-4.0/settings.ini` resolve to this checkout while
      `gtk.css`/`thunar.css` remain local generated files.

## btop, cava, fuzzel and micro

- [ ] btop: main background/text, CPU/memory/network/process boxes, selected
      process row, meter backgrounds, graph labels and dividers all follow the
      current palette. Restart btop or send `SIGUSR2`.
- [ ] cava: bars use the eight-stop gradient on an explicit surface
      background; no colour is inherited from the previous terminal program.
      Restart cava or send `SIGUSR2`.
- [ ] fuzzel: background, text, prompt, placeholder, match, selected row,
      selection text, counter and border are readable and opaque. Reopen the
      launcher after a palette change.
- [ ] micro: open a source file with comments, strings, a number, a keyword and
      a type. Status line, tab bar, selection, search highlight, cursor line
      and gutter are readable in both modes. Restart micro or reselect the
      `padilha` colourscheme.

## Midnight Commander

- [ ] Open MC in the terminal. Panels, selected row, marked files, function-key
      bar, menus, dialogs, editor frame and help use the `caelestia` skin.
- [ ] Change to a light palette and reopen MC; the skin is regenerated and the
      panel backgrounds are light with dark text.
- [ ] On upstream MC, restart MC after a palette change; the fork reloads on
      `SIGUSR1`.

## Spotify / Spicetify

- [ ] Run `spicetify config current_theme caelestia color_scheme caelestia`
      and `spicetify apply` after the palette apply.
- [ ] Sidebar, main view, cards, context menus, player bar, search bar, hover
      row, selected row, buttons and equalizer use the generated colours.
- [ ] Restart Spotify if a surface keeps the previous palette. Album art,
      canvas and lyrics keep their own colours and are expected not to match.
- [ ] If Spicetify is not installed, confirm Spotify keeps its stock colours;
      this repository does not install or patch it.

## Discord (only if a client mod is already installed manually)

- [ ] The client-mod theme folder contains a self-contained
      `caelestia.theme.css` with no remote `@import` or asset.
- [ ] Server list, channel sidebar, chat, member list, menus, settings, focus
      rings and scrollbars use the generated surfaces.
- [ ] Disabling the theme restores the stock Discord appearance; the repository
      did not install, patch or update the client.

## Other installed apps

- [ ] Qt apps launched with `QT_QPA_PLATFORMTHEME=qtengine` use the generated
      colours; if `qt5ct`/Kvantum overrides them, record the active style rather
      than editing generated files.
- [ ] Electron/Chromium apps (Obsidian, Todoist, YouTube Music, Bitwarden,
      Chromium, Steam) are checked only for their own light/dark setting and
      GTK frame; their web surfaces are not expected to follow the palette.
- [ ] GIMP, LibreOffice and other self-themed GTK apps are checked for readable
      chrome; their own theme overrides are reported, not patched.

If a screenshot is useful, use a dedicated empty workspace and do not capture
the DSH terminal, Firefox, Discord, Spotify, a private window or a notification.
