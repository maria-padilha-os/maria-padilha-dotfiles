# Firefox

Maria Padilha's tracked Firefox configuration: the two user-chrome stylesheets, the
one preference that makes Firefox load them, and the install glue that puts
them in the right profile.

| Path | Purpose |
| --- | --- |
| `user.js` | The single preference Firefox needs: `toolkit.legacyUserProfileCustomizations.stylesheets=true`. Copied, never linked. |
| `chrome/userChrome.css` | Browser chrome: toolbars, tabs, address bar, panels, sidebar, find bar. Linked into the profile. |
| `chrome/userContent.css` | New tab / home, `about:blank` and private browsing. Linked into the profile. |
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

## Theme scope and limitations

- Firefox exposes user chrome as an unsupported customisation point. Selectors
  and token names occasionally change between releases. The rules here target
  Firefox 159 and degrade to Firefox's own colours rather than breaking the
  window.
- `about:preferences`, `about:addons`, the PDF viewer, devtools and web content
  are intentionally not restyled. Their own layouts assume the built-in theme.
  Web pages are never touched: all `userContent.css` rules are scoped with
  `@-moz-document`.
- If a third-party Firefox theme is active, its colours may still show through
  in places Maria Padilha does not override. Choose the default light or dark theme.
- Private windows use the themed chrome, and `about:privatebrowsing` is
  themed; the sites opened in them are ordinary web pages.
- Removing `user.js` does not undo the preference on its own: Firefox has
  already copied it into `prefs.js`. Reset it in `about:config` (or remove it
  from `prefs.js`) after deleting the file.
- Flatpak and Snap are detected but not exercised on this machine; if one of
  them uses a different path, use `LILITH_FIREFOX_PROFILE_DIR`.
- The chrome CSS is loaded only at startup. Restart Firefox after a palette
  change (or after installing the files for the first time).

## Verify locally

The renderer is tested from `maria-padilha-de` with a temporary prefix, so no
real profile is needed. From that checkout:

```sh
bash tests/all.sh
```

For a manual check, create a throwaway tree that looks like `$HOME`, add a
`profiles.ini`, and run:

```sh
tmp=$(mktemp -d)
mkdir -p "$tmp/home/me/.mozilla/firefox/abc.default-release/chrome"
printf '%s\n' \
  '[Profile0]' 'Name=default-release' 'IsRelative=1' \
  'Path=abc.default-release' 'Default=1' > "$tmp/home/me/.mozilla/firefox/profiles.ini"
HOME=/home/me ./bin/padilha-theme apply --seed ff1a1a --mode dark --prefix "$tmp" --no-signals
sed -n '1,20p' "$tmp/home/me/.mozilla/firefox/abc.default-release/chrome/lilith.css"
```
