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

function palette(scheme) {
  const c = scheme?.colours
  if (!c?.surface || !c?.onSurface) return undefined
  const mode = scheme.mode === 'dark' ? 'dark' : 'light'
  return {
    base: mode,
    colors: {
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
    },
  }
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
