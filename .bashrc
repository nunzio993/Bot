# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]; then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
if [ -d ~/.bashrc.d ]; then
    for rc in ~/.bashrc.d/*; do
        if [ -f "$rc" ]; then
            . "$rc"
        fi
    done
fi
unset rc
export BINANCE_APY_KEY="5gslQFwhB1A2eo5eETDQkHZzsE4fECHvvh2npVLpCkDEuVWPgSOIJNv3GARLdFwK"
export BINACNE_API_SECRET="iyPgm84XXph1VIs3hj3ICpTS8nzrJnMI703y1C7fpByasLKY8pkCugiiC6kK8GgS"
