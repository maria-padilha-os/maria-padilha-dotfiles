vim.g.base46_cache = vim.fn.stdpath "data" .. "/base46/"
vim.g.mapleader = " "

-- Maria Padilha's colorscheme: ayu-like light/dark grammar, following the wallpaper.
-- Set this to false to keep NvChad's selected base46 theme instead.
vim.g.caelestia_colorscheme = true

-- WezTerm already paints the wallpaper-derived surface at 0.85 opacity. Let
-- that show through Normal so nvim and the terminal have the same background;
-- base46's own transparency stays off, because its dark themes would become
-- unreadable on the light daytime terminal.
vim.g.caelestia_transparent = true

-- bootstrap lazy and all plugins
local lazypath = vim.fn.stdpath "data" .. "/lazy/lazy.nvim"

if not vim.uv.fs_stat(lazypath) then
  local repo = "https://github.com/folke/lazy.nvim.git"
  vim.fn.system { "git", "clone", "--filter=blob:none", repo, "--branch=stable", lazypath }
end

vim.opt.rtp:prepend(lazypath)

local lazy_config = require "configs.lazy"

-- load plugins
require("lazy").setup({
  {
    "NvChad/NvChad",
    lazy = false,
    branch = "v2.5",
    import = "nvchad.plugins",
  },

  { import = "plugins" },
}, lazy_config)

-- load theme
dofile(vim.g.base46_cache .. "defaults")
dofile(vim.g.base46_cache .. "statusline")

require "options"
require "autocmds"
require "sessions"

vim.schedule(function()
  require "mappings"
end)
