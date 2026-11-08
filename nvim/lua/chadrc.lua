-- This file needs to have same structure as nvconfig.lua
-- https://github.com/NvChad/ui/blob/v3.0/lua/nvconfig.lua
-- Please read that file to know all available options :(

---@type ChadrcConfig
local options = {
  base46 = {
    theme = "caelestia",
    -- hl_override = {
    -- 	Comment = { italic = true },
    -- 	["@comment"] = { italic = true },
    -- },
    theme_toggle = { "caelestia", "caelestia" },
    -- Every Neovim surface follows the terminal surface, including its opacity.
    -- An opaque Normal looked like a different colour next to WezTerm. If you
    -- fall back to base46 ayu_dark on the light daytime terminal, expect light
    -- text over it: switch the theme or the terminal setting in that case.
    transparency = true,
  },

  -- nvdash = { load_on_startup = true },

  ui = {
    tabufline = {
      lazyload = false,
      order = { "buffers", "tabs", "btns" },
    },
  },
}

local status, chadrc = pcall(require, "chadrc")
return vim.tbl_deep_extend("force", options, status and chadrc or {})
