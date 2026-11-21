# Follow-up for `maria-padilha-de`

This file records the generator-side work found by the dotfiles app-theme
audit. Nothing in the sibling `maria-padilha-de` checkout was edited; this is a
request for its owner.

## 1. Refresh/replace stale generated Discord themes

**Files:** `share/templates/discord.scss`, `lib/apply.lua`, the Discord theme
tests.

**Observed defect:** the current template is self-contained, but the client
theme files on the audited host were legacy “Midnight (Caelestia)” files
beginning with:

```css
@import url("https://refact0r.github.io/midnight-discord/build/midnight.css");
```

Those files were not produced by the current template. They are stale output
from an older generator and still make a remote request, which contradicts the
current contract in `share/templates/README.md`.

**Requested change:**

- When `enableDiscord = true`, replace an existing
  `<client>/themes/caelestia.theme.css` with the compiled current template, even
  when the client directory already contains an old file. Keep the existing
  “only write into client-mod directories that already exist” rule.
- Add a generated-output assertion used by the theme tests: the compiled CSS
  contains no `@import`, no `http://`/`https://`, no `url(` asset, no
  `@font-face`, and no JavaScript/network API. The existing dotfiles
  `tests/discord_theme.py` is the static contract for the opt-in file; the
  generator should emit the same shape.
- Do not write into the dotfiles `discord/theme.css`. The dotfiles file is the
  static fallback and the two are intentionally separate.

## 2. Keep Spicetify’s `color.ini` generation and leave `config-xpui.ini` to dotfiles

**Files:** `share/templates/spicetify-dark.ini`, `share/templates/spicetify-light.ini`, `lib/apply.lua`.

**Current state:** the engine writes only
`~/.config/spicetify/Themes/caelestia/color.ini`. That is correct: Spicetify
rewrites `config-xpui.ini` itself.

**Requested change:** keep it that way. The dotfiles repository now seeds
`spicetify/config-xpui.ini` and a static `color.ini` fallback only when they
are missing, so the generator must not start owning or symlinking
`config-xpui.ini`. If the generator later emits a `user.css`, it must be
palette-only and must not replace a user’s local layout tweaks. Add a test that
a non-existent Spicetify directory remains untouched (no package installation,
no launched client).

## 3. Document the Flatpak boundary; do not generate into `~/.var/app`

**Files:** `docs/app-themes.md`, `docs/gtk-qt-visual-checklist.md` (already has
the caveat), `lib/apply.lua`.

**Current state:** GTK 3/4 colour sheets are written to the host
`~/.config/gtk-*` only. A Flatpak app has its own XDG config and may use its
runtime theme or the XDG settings portal.

**Requested change:** no template change is needed. If a Flatpak helper is
added later, make it an explicit user opt-in; never write into
`~/.var/app/<id>/config` or a Flatpak cache during `padilha-theme apply`, and
never treat a portal/sandbox failure as a reason to escalate privileges.

## 4. No palette-template change needed for the remaining apps

The following templates already match the current scheme and the new dotfiles
fallbacks were rendered from them:

- `share/templates/btop.theme`
- `share/templates/cava.conf`
- `share/templates/fuzzel.ini`
- `share/templates/micro.micro`
- `share/templates/mc-skin.ini`

Do not move these files into the dotfiles repository or make the dotfiles
symlink their destinations: the engine writes the whole file, and the dotfiles
now seed a copy only when the destination is absent. The only generator-side
defect found in this audit is item 1.

## Acceptance checks for the follow-up

```sh
# from maria-padilha-de
bash tests/all.sh
```

Add or extend a generated-output test so that a temporary
`enableDiscord = true` run asserts the compiled stylesheet has no remote
import, and that an existing legacy `caelestia.theme.css` is replaced. Keep
the dotfiles `discord/theme.css` and `tests/discord_theme.py` unchanged.
