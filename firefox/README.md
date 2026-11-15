# Firefox

Maria Padilha's tracked Firefox configuration: the two user-chrome stylesheets, the
one preference that makes Firefox load them, and the install glue that puts
them in the right profile.

| Path | Purpose |
| --- | --- |
| `user.js` | The single preference Firefox needs: `toolkit.legacyUserProfileCustomizations.stylesheets=true`. Copied, never linked. |
| `chrome/userChrome.css` | Browser chrome: toolbars, tabs, address bar, panels, sidebar, find bar. Linked into the profile. |
| `chrome/userContent.css` | New tab / home, `about:blank`, private browsing, session restore and welcome. Linked into the profile. |
| `../tests/firefox_theme.py` | Static checks for local imports, `--lilith-*` fallbacks, scoped content rules and remote assets. |
| `../bin/padilha-dots firefox` | Detects the default profile and installs the files. |

The files here contain **rules and fallbacks only**. The palette lives in
`chrome/lilith.css`, which `padilha-theme` in `maria-padilha-de` writes from the
current Material You scheme:

```sh
padilha-theme apply --wallpaper "$(cat ~/.local/state/caelestia/wallpaper/path.txt)"
```

The generated file defines `--lilith-bg`, `--lilith-surface`,
`--lilith-on-surface`, `--lilith-primary`, `--lilith-outline` and the other
roles used by both stylesheets. Both sheets import it, so a normal wallpaper or
palette change only rewrites that one file.

Both stylesheets also carry a `:where(:root)` fallback palette and a
`light-dark()` fallback on every `var(--lilith-*)` use. The fallback is used
while `lilith.css` is missing or incomplete, and follows the system light/dark
preference in that state. A complete generated palette has higher specificity
and wins, so the fallbacks never override the active Material You scheme.

## The first launch matters

Firefox does not create `~/.mozilla/firefox` until it runs for the first time.
`padilha-dots firefox` therefore cannot install anything before that. It is
deliberately non-fatal: it prints a note, exits successfully, and repeats the
installation next time.

One-time sequence on a new machine:

1. Launch Firefox once and quit it. This creates the default profile and
   `profiles.ini`.
2. Install the config:

   ```sh
   # from the maria-padilha-dotfiles checkout
   ./bin/padilha-dots firefox
   ```

   (Plain `./bin/padilha-dots` includes `firefox` too, along with hypr, nvim,
   wezterm and mc.)

3. Generate the palette into the new profile. If you have already applied a
   theme, re-apply it; otherwise change the wallpaper as usual:

   ```sh
   padilha-theme apply --wallpaper "$(cat ~/.local/state/caelestia/wallpaper/path.txt)"
   ```

   The file written is
   `~/.mozilla/firefox/<profile>/chrome/lilith.css`.

4. Restart Firefox. The chrome and the new tab page should use the current
   Maria Padilha palette.

You can confirm the profile folder and the preference in Firefox:
`about:support` shows the profile directory; `about:config` shows
`toolkit.legacyUserProfileCustomizations.stylesheets = true`.

## Restart is required

Firefox reads `userChrome.css`, `userContent.css` and their `lilith.css` import
only while starting a browser process. Editing a sheet or running
`padilha-theme apply` does **not** hot-reload the chrome or the new-tab page.
Quit every Firefox window (including a background process), then start Firefox
again. Toggling the `toolkit.legacyUserProfileCustomizations.stylesheets`
preference may reload the sheets in some builds, but a full restart is the
supported, predictable path.

## What `padilha-dots firefox` touches

It reads `profiles.ini` and picks, in order:

1. a `[ProfileN]` section with `Default=1`;
2. the `Default=` profile named by an `[Install...]` section;
3. the first profile whose directory exists.

Candidate roots are the native `~/.mozilla/firefox`, then the Flatpak
(`~/.var/app/org.mozilla.firefox/.mozilla/firefox`) and Snap
(`~/snap/firefox/common/.mozilla/firefox`) locations. For a non-standard
layout, set `LILITH_FIREFOX_PROFILE_DIR=/path/to/profile`; both
`padilha-dots` and `padilha-theme` read it.

It then:

- **copies** `user.js` into the profile root. An existing `user.js` with
  different content is moved to `user.js.pre-padilha-<timestamp>` first; an
  identical one is simply refreshed. It is copied because Firefox and profile
  managers expect a real file at that path.
- **symlinks** `chrome/userChrome.css` and `chrome/userContent.css` into the
  profile's `chrome/` directory. A real file in the way is moved to
  `<name>.pre-padilha-<timestamp>`, never deleted.
- leaves `chrome/lilith.css` to `padilha-theme`; it does not create or edit it.
- never touches `prefs.js`, `bookmarks.html`, `places.sqlite`, sessions or any
  other profile file.

Running the command again is safe: an identical `user.js` is refreshed without
a backup, and links already pointing at this checkout are left alone.

## Theme scope

The chrome sheet covers the surfaces that otherwise keep Firefox's built-in
colours:

- the tab strip: selected, hovered, pinned, attention and close-button states;
- the address bar: focused/open border, identity area, page actions, text,
  placeholder and the result list;
- toolbar buttons: hover, active/open, disabled, badges and icon fills;
- menus and popups: the app menu, context menus, overflow/extensions panels,
  downloads, notification popups, tooltips and menu accelerators;
- the sidebar: header, splitter, search box and bookmark/history tree rows;
- the find bar: input, buttons, status text and the not-found state;
- the status bubble, downloads and notification controls;
- private windows: the indicator, toolbar border and address-bar border.

The content sheet deliberately themes only these internal pages:

- `about:newtab` and `about:home` (activity stream: search, top sites, cards,
  customize/context menus);
- `about:blank`;
- `about:privatebrowsing`;
- `about:sessionrestore`;
- `about:welcome`.

`about:preferences`, `about:addons`, `about:config`, the PDF viewer, devtools
and ordinary web pages are intentionally **not** restyled. Every rule in
`userContent.css` is inside an `@-moz-document` scope; only the `lilith.css`
import is global, and it defines custom properties rather than painting
anything.

## Verification checklist

Run the repository checks first. They parse the CSS statically, install nothing,
and need no profile or network:

```sh
# from the maria-padilha-dotfiles checkout
sh tests/ci.sh
python3 tests/firefox_theme.py
```

`tests/firefox_theme.py` checks that every `@import` is local and stays inside
`chrome/` (the generated `lilith.css` is allowed as the documented runtime
palette), every `var(--lilith-*)` has a non-empty fallback and every used
property is declared in the fallback palette, no remote URL or font asset is
referenced, and every `userContent.css` rule is scoped by `@-moz-document`.

Then verify the rendered result after a full restart:

- [ ] `about:support` shows the expected profile; `about:config` shows
      `toolkit.legacyUserProfileCustomizations.stylesheets = true`.
- [ ] Install or re-apply a **light** palette, restart, and check the tab strip,
      address bar, toolbar hover states, hamburger menu, a context menu, the
      downloads panel, the sidebar (`Ctrl+B`) and the find bar (`Ctrl+F`).
- [ ] Install or re-apply a **dark** palette, restart, and repeat the same
      inspection. Text, icons, placeholders and selected rows must stay
      readable on every surface.
- [ ] Focus the address bar, then press `Tab` through the toolbar, menus, find
      bar and sidebar. Every focused control gets a visible primary-coloured
      outline that does not blend into its background.
- [ ] Open `Ctrl+Shift+P` (private window). The private-browsing indicator and
      `about:privatebrowsing` are readable, and the window still uses the
      themed chrome.
- [ ] Open a new tab/home, `about:blank`, `about:sessionrestore` and
      `about:welcome`. They use the palette and do not fall back to white text
      on a light card or dark text on a dark card.
- [ ] Open an ordinary website and confirm its own CSS is untouched. Also open
      `about:preferences` and `about:addons` and confirm they keep Firefox's
      native styling.
- [ ] The theme's CSS makes no remote requests: `tests/firefox_theme.py` reports
      no remote URLs, and the sheets reference only the local `lilith.css`.

If a surface is still using built-in colours, check that no third-party Firefox
theme is active (choose the default light or dark theme), confirm the
`lilith.css` file exists next to the linked sheets, and restart again. The
selectors target Firefox 159; a future release may rename a selector or token,
in which case the fallbacks keep the window readable until the sheet is updated.

## Verify the install path locally

The renderer is tested from `maria-padilha-de` with a temporary prefix, so no
real profile is needed. From that checkout:

```sh
bash tests/all.sh
```

For an install-only check, create a throwaway tree that looks like `$HOME`, add
a `profiles.ini`, and exercise `padilha-dots` (and, from `maria-padilha-de`, the
palette renderer) without touching the live profile:

```sh
tmp=$(mktemp -d)
mkdir -p "$tmp/home/me/.mozilla/firefox/abc.default-release/chrome"
printf '%s\n' \
  '[Profile0]' 'Name=default-release' 'IsRelative=1' \
  'Path=abc.default-release' 'Default=1' > "$tmp/home/me/.mozilla/firefox/profiles.ini"
HOME="$tmp/home" ./bin/padilha-dots firefox
HOME="$tmp/home" ./bin/padilha-theme apply --seed ff1a1a --mode dark --prefix "$tmp" --no-signals
sed -n '1,20p' "$tmp/home/me/.mozilla/firefox/abc.default-release/chrome/lilith.css"
```

`bin/padilha-dots firefox` is safe to run again: it refreshes an identical
`user.js`, leaves links that already point at this checkout alone, and backs up
anything it has to replace instead of deleting it.
