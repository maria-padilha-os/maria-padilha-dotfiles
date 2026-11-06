> Maria Padilha note: this config uses the palette-following `caelestia`
> colorscheme. Neovim's `Normal` background is intentionally transparent (both
> `caelestia_transparent` and base46 transparency) so it always matches the
> WezTerm surface and its 0.85 opacity; the terminal supplies the colour.

## Defold keys

Defold's project build runs on `<F5>` and the no-build relaunch on `<F6>`.
Backspace is not mapped, so it keeps Neovim's normal cursor movement.

## DSH theme

DSH normally detects light/dark through the terminal's OSC 11 reply, which
Neovim's embedded terminal does not provide. The colorscheme exports
`DSH_TUI_THEME` from the current caelestia mode, and the `<leader>ld` mapping
also sets it at launch, so DSH uses the readable light or dark palette instead
of falling back to light text on a light surface.

**This repo is supposed to be used as config by NvChad users!**

- The main nvchad repo (NvChad/NvChad) is used as a plugin by this repo.
- So you just import its modules , like `require "nvchad.options" , require "nvchad.mappings"`
- So you can delete the .git from this repo ( when you clone it locally ) or fork it :)

# Credits

1) Lazyvim starter https://github.com/LazyVim/starter as nvchad's starter was inspired by Lazyvim's . It made a lot of things easier!
