# fish shell configurations

# aliases
alias cdd="cd ~/dotfiles"
alias cdc="cd ~/code"
alias cdt="cd ~/thesis"
alias ll="ls -alhF"
alias la="ls -A"
alias ipy="ipython3"
alias py="python3"
alias ipdb="ipython3"
alias pdb="python3"

# greeting message
function fish_greeting
end

# environment variables
set -Ux LESS "-iRw"
set -Ux EDITOR vim

# bindings
# bind

# functions
fzf_key_bindings
