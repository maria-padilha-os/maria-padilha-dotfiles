// Live Maria Padilha palette for dsh-tui.
//
// Registers one runtime theme and refreshes it when the caelestia scheme
// changes. DSH_TUI_THEME=padilha:dynamic selects it; no TUI restart needed.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const SCHEME = path.join(os.homedir(), '.local/state/caelestia/scheme.json')
const THEME = 'padilha:dynamic'

function hex(value) {
  return value ? '#' + String(value).replace(/^#/, '') : undefined
}

function readScheme() {
  try {
    return JSON.parse(fs.readFileSync(SCHEME, 'utf8'))
  } catch {
    return undefined
  }
}


// Material roles are chosen for surfaces, but a few (notably "success" and
// light-theme accents) are intentionally pale. Ensure every foreground role
// stays readable against the actual background instead of trusting the role.
function rgbOf(value) {
  const match = /^#?([0-9a-f]{6})$/i.exec(value || '')
  if (!match) return undefined
  return [0, 2, 4].map(i => parseInt(match[1].slice(i, i + 2), 16))
}

function luminance([r, g, b]) {
  const channel = value => {
    value /= 255
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
}

function contrast(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}

function readable(foreground, background, mode) {
  const fg = rgbOf(foreground)
  const bg = rgbOf(background)
  if (!fg || !bg || contrast(fg, bg) >= 4.5) return foreground
  const target = mode === 'dark' ? [255, 255, 255] : [0, 0, 0]
  let result = fg
  for (let step = 1; step <= 20; step++) {
    result = fg.map((value, index) => Math.round(value + (target[index] - value) * step / 20))
    if (contrast(result, bg) >= 4.5) break
  }
  return '#' + result.map(value => value.toString(16).padStart(2, '0')).join('')
}

function readablePalette(colors, mode) {
  const background = colors.background
  const backgroundRoles = new Set([
    'background', 'inverseText', 'selectionBg', 'inputBackground',
    'userMessageBackground', 'userMessageBackgroundHover',
    'toolCardBackground', 'toolCardBackgroundDim',
  ])
  const out = { ...colors }
  for (const key of Object.keys(out)) {
    if (backgroundRoles.has(key)) continue
    if (typeof out[key] === 'string' && out[key].startsWith('#'))
      out[key] = readable(out[key], background, mode)
  }
  return out
}

function palette(scheme) {
  const c = scheme?.colours
  if (!c?.surface || !c?.onSurface) return undefined
  const mode = scheme.mode === 'dark' ? 'dark' : 'light'
  const colors = {
      background: hex(c.surface),
      text: hex(c.onSurface),
      inverseText: hex(c.surface),
      accent: hex(c.primary),
      accentShimmer: hex(c.secondary),
      activity: hex(c.tertiary),
      activityShimmer: hex(c.secondary),
      promptBorder: hex(c.outline),
      promptBorderShimmer: hex(c.primary),
      permission: hex(c.tertiary),
      permissionShimmer: hex(c.secondary),
      success: hex(c.success),
      error: hex(c.error),
      warning: hex(c.tertiary),
      merged: hex(c.secondary),
      inactive: hex(c.onSurfaceVariant),
      subtle: hex(c.outline),
      selectionBg: hex(c.primaryContainer),
      inputBackground: hex(c.surfaceContainer),
      userMessageBackground: hex(c.surfaceContainer),
      userMessageBackgroundHover: hex(c.surfaceContainerHigh),
      toolCardBackground: hex(c.surfaceContainer),
      toolCardBackgroundDim: hex(c.surfaceContainerLow),
      toolDotExec: hex(c.primary),
      toolDotRead: hex(c.secondary),
      toolDotWrite: hex(c.tertiary),
      toolDotWeb: hex(c.blue),
      toolDotTask: hex(c.tertiary),
      syntaxKeyword: hex(c.primary),
      syntaxString: hex(c.success),
      syntaxComment: hex(c.outline),
      syntaxNumber: hex(c.tertiary),
      syntaxFunction: hex(c.secondary),
      syntaxType: hex(c.primary),
      syntaxVariable: hex(c.onSurface),
      syntaxOperator: hex(c.primary),
      syntaxPunctuation: hex(c.outline),
      syntaxConstant: hex(c.tertiary),
  }
  return { base: mode, colors: readablePalette(colors, mode) }
}

export const name = 'padilha-theme-sync'

export function apply(ctx) {
  ctx.inject(['tuiThemes'], (themesCtx) => {
  const themes = themesCtx.tuiThemes

  let dispose
  let last = ''

  const sync = () => {
    const scheme = readScheme()
    const next = palette(scheme)
    if (!next) return
    const key = JSON.stringify(next)
    if (key === last) return

    // Re-registering the same id requires releasing the old contribution first.
    dispose?.()
    dispose = themes.register({
      name: THEME,
      displayName: 'Maria Padilha',
      base: next.base,
      colors: next.colors,
    }, themesCtx)
    last = key
  }

  sync()
  const timer = setInterval(sync, 1000)
  ctx.effect(() => () => {
    clearInterval(timer)
    dispose?.()
  })
  })
}
