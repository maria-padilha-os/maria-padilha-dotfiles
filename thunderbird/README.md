# Thunderbird

Maria Padilha's tracked Thunderbird customisations.

| Path | Purpose |
| --- | --- |
| `user.js` | Enables profile stylesheets. Copied into the profile. |
| `chrome/userChrome.css` | Mail chrome, tabs, folder/thread panes, message header, compose window. Linked into the profile. |
| `chrome/userContent.css` | Message body and attachment surfaces. Linked into the profile. |

The files contain **rules and variables only**. The palette and Thunderbird's
accent aliases are generated into `chrome/padilha.css` by `padilha-theme` in
`maria-padilha-de`:

```sh
padilha-theme apply --wallpaper "$(cat ~/.local/state/caelestia/wallpaper/path.txt)"
./bin/padilha-dots thunderbird
```

Restart Thunderbird after either command. The profile is found from
`profiles.ini`; set `PADILHA_THUNDERBIRD_PROFILE_DIR` to override it.
