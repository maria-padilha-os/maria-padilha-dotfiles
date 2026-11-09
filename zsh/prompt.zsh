# Maria Padilha zsh prompt.
#
# A small native prompt, deliberately not Starship. ANSI colour names follow
# the terminal palette, so it tracks the caelestia light/dark scheme. This file
# is sourced after conda init so conda's plain "(base) %m%#" PS1 cannot win.
autoload -Uz vcs_info
zstyle ':vcs_info:git:*' formats ' %F{yellow}(%b)%f'
setopt PROMPT_SUBST
precmd() { vcs_info }

PROMPT='%F{red}%n@%m%f %F{blue}%~%f${vcs_info_msg_0_} %F{red}❯%f '
PROMPT2='%F{red}…%f '
