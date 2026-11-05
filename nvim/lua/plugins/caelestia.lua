-- The Lilith colorscheme is opt-in. NvChad's selected base46 theme (ayu_dark)
-- stays in charge unless this is enabled before the plugin loads:
--
--     vim.g.caelestia_colorscheme = true
--
-- To try it once: :colorscheme caelestia
--
-- vim.g.caelestia_transparent = true   -- see-through background (opaque by default)

if not vim.g.caelestia_colorscheme then
    return {}
end

-- VimEnter so plugins shipping highlight groups have loaded first
vim.api.nvim_create_autocmd("VimEnter", {
    once = true,
    group = vim.api.nvim_create_augroup("caelestia_colorscheme", { clear = true }),
    callback = function() pcall(vim.cmd.colorscheme, "caelestia") end,
})

-- nvim-tree is lazy and NvChad's opts run base46's nvimtree integration, which
-- repaints NvimTreeNormal dark after the colorscheme applied. Re-apply only the
-- tree groups (a full :colorscheme would run highlight clear and wipe groups
-- installed by later plugins).
vim.api.nvim_create_autocmd("User", {
    pattern = "NvimTreeSetup",
    group = vim.api.nvim_create_augroup("caelestia_nvimtree", { clear = true }),
    callback = function()
        if vim.g.colors_name == "caelestia" and _G.caelestia_nvimtree_highlights then
            _G.caelestia_nvimtree_highlights()
        end
    end,
})

-- optional = true so this only applies if LazyVim is already installed
return {
    { "LazyVim/LazyVim", optional = true, opts = { colorscheme = "caelestia" } },
}
