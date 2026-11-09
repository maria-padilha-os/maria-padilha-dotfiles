# Maria Padilha zsh prompt.
#
# Mirrors fish's default prompt, which is what WezTerm shows:
#   machine@machinedr ~/C/m/maria-padilha-dotfiles (main)>
# Intermediate directories are shortened to one character, the branch is
# shown, and no colours are forced. Sourced after conda init.
setopt PROMPT_SUBST

function padilha_pwd() {
    local p=${PWD/#$HOME/\~}
    local -a parts out
    parts=("${(@s:/:)p}")
    local i
    for (( i = 1; i <= ${#parts}; i++ )); do
        local part=${parts[i]}
        if (( i == ${#parts} )) || [[ $part == "~" || -z $part ]]; then
            out+=("$part")
        else
            out+=("${part[1]}")
        fi
    done
    local IFS=/
    print -n "${out[*]}"
}

function padilha_git() {
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || return
    [[ -n $branch ]] && print -n " ($branch)"
}

PROMPT='%n@%m $(padilha_pwd)$(padilha_git)> '
PROMPT2='> '
