# zsh equivalents of the fish behaviour: inline history suggestions and the
# extra completion definitions shipped by zsh-completions.
fpath=(/usr/share/zsh/plugins/zsh-completions/src $fpath)

if [ -r /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ]; then
    ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=8'
    source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
fi

autoload -Uz compinit
compinit -i
