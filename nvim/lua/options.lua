require "nvchad.options"
local opt = vim.opt
-- local o = vim.o

opt.foldmethod = "indent"
opt.foldexpr = "nvim_treesitter#foldexpr()"
opt.foldlevel = 99
opt.wrap = false

vim.cmd[[ au FileType vim setlocal fo-=c fo-=r fo-=o ]]

vim.filetype.add({
  extension = {
    script = "lua",
    gui_script = "lua",
    fp = "glsl",
    fs = "glsl",
    vp = "glsl",
  }
})

-- All nvim terminals use zsh; never inherit a fish shell from an old session.
vim.o.shell = '/usr/bin/fish'

-- Nvim's embedded terminal does not answer OSC 11. Give child programs the
-- same foreground/background hint WezTerm would report, following day/night.
local function set_terminal_colour_hint()
  local mode = "light"
  local ok, lines = pcall(vim.fn.readfile, vim.fs.normalize "~/.local/state/caelestia/scheme.json")
  if ok and table.concat(lines, "\n"):match('"mode"%s*:%s*"dark"') then
    mode = "dark"
  end
  vim.env.COLORFGBG = mode == "dark" and "15;0" or "0;15"
end
set_terminal_colour_hint()
