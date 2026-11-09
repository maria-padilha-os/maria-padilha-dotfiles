# Maria Padilha zsh prompt.
#
# Use the same Starship configuration as the WezTerm fish prompt did. This is
# sourced after conda init so conda's PS1 cannot override it.
if command -v starship >/dev/null 2>&1; then
    export STARSHIP_CONFIG="$HOME/.config/zsh/starship-zsh.toml"
    # Manjaro's Powerlevel prompt installs precmd hooks that repaint PROMPT
    # after this file runs. Clear them; Starship owns the prompt from here.
    precmd_functions=()
    preexec_functions=()
    # The partial-line marker adds padding and a "%" that zsh can repaint
    # over the command line when the prompt wraps.
    unsetopt PROMPT_SP
    unsetopt PROMPT_CR
    eval "$(starship init zsh)"
fi
