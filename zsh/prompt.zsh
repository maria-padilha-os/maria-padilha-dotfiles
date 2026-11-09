# Maria Padilha zsh prompt.
#
# Use the same Starship configuration as the WezTerm fish prompt did. This is
# sourced after conda init so conda's PS1 cannot override it.
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init zsh)"
fi
