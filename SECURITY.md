# Security policy

These are configuration files, not a daemon, but they are loaded by Hyprland,
Neovim, WezTerm, Firefox, micro, and Midnight Commander. Report a vulnerability
privately through this repository's **Security → Report a vulnerability** page.

Do not commit `hypr/hyprland/env.local.lua`; it is ignored and is where local API
keys belong. If a secret was committed, rotate it first and then open a private
report.

The desktop application's policy is in
[maria-padilha-de/SECURITY.md](https://github.com/maria-padilha-os/maria-padilha-de/blob/main/SECURITY.md).
