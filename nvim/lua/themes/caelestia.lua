-- Base16 preview for NvChad's <leader>th picker.
--
-- The actual colourscheme lives in colors/caelestia.lua. NvChad's picker
-- requires a themes.<name> module for the palette swatch, so expose the same
-- roles here. Read the generated scheme so the swatch follows the wallpaper.
local M = {}

local fallback = {
    surface = "#1a1110", surfaceContainer = "#271d1c", surfaceContainerHigh = "#322826",
    outlineVariant = "#524340", onSurfaceVariant = "#d7c2bd", onSurface = "#f1dfdb",
    error = "#ffb4ab", primary = "#ffb4a3", tertiary = "#e0c38c", success = "#b9ccb9",
    secondary = "#e8bdb6", outline = "#a08c88",
}

local colours = fallback
local scheme_path = vim.fn.expand "~/.local/state/caelestia/scheme.json"
local lines = vim.fn.readfile(scheme_path)
if #lines > 0 then
    local ok, decoded = pcall(vim.json.decode, table.concat(lines, "\n"))
    if ok and type(decoded) == "table" and type(decoded.colours) == "table" then
        colours = decoded.colours
    end
end

local function hex(name)
    local value = colours[name] or fallback[name] or "000000"
    return "#" .. value:gsub("^#", "")
end

M.type = "light"
if colours.surface then
    local r = tonumber(colours.surface:sub(1, 2), 16) or 0
    local g = tonumber(colours.surface:sub(3, 4), 16) or 0
    local b = tonumber(colours.surface:sub(5, 6), 16) or 0
    if (r + g + b) / 3 < 128 then
        M.type = "dark"
    end
end

M.base_16 = {
    base00 = hex "surface",
    base01 = hex "surfaceContainer",
    base02 = hex "surfaceContainerHigh",
    base03 = hex "outlineVariant",
    base04 = hex "onSurfaceVariant",
    base05 = hex "onSurface",
    base06 = hex "onSurface",
    base07 = hex "onSurface",
    base08 = hex "error",
    base09 = hex "primary",
    base0A = hex "tertiary",
    base0B = hex "success",
    base0C = hex "secondary",
    base0D = hex "primary",
    base0E = hex "secondary",
    base0F = hex "outline",
}

return M
