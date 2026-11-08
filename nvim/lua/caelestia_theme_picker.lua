-- Make the Maria Padilha colorscheme selectable from NvChad's
-- <leader>th picker, which otherwise only lists base46 themes.
local M = {}

function M.setup()
    local ok, nvutils = pcall(require, "nvchad.utils")
    if not ok then
        return
    end

    if not nvutils._caelestia_theme_list then
        local original = nvutils.list_themes
        nvutils.list_themes = function()
            local themes = original()
            if not vim.tbl_contains(themes, "caelestia") then
                table.insert(themes, 1, "caelestia")
            end
            return themes
        end
        nvutils._caelestia_theme_list = true
    end

    local theme_ok, theme_utils = pcall(require, "nvchad.themes.utils")
    if theme_ok and not theme_utils._caelestia_theme_reload then
        local original = theme_utils.reload_theme
        theme_utils.reload_theme = function(name)
            if name == "caelestia" then
                vim.cmd.colorscheme("caelestia")
                return
            end
            return original(name)
        end
        theme_utils._caelestia_theme_reload = true
    end

    local state_ok, state = pcall(require, "nvchad.themes.state")
    if state_ok then
        state.val = nvutils.list_themes()
        state.themes_shown = state.val
        if state.index < 1 or state.index > #state.val then
            state.index = 1
        end
    end
end

return M
