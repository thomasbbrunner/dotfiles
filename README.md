# dotfiles

To install these dotfiles:

`python3 ./install.py install`

To unpack archives:

`python3 ./install.py unpack`

To pack archives:

`python3 ./install.py pack`

## TODO
* Find way to save root folder of dotfiles to variable to use in the scripts, instead of assuming the dotfiles are located in ~/
* Create warning when launching bash when code in ~/code is not committed and pushed (by running script in bashrc)
* Create template git repo with general .gitignore and 'main' branch (instead of 'master')

### Add gnome settings to dotfiles
Consider using `gsettings` instead of `dconf` for Gnome settings (it is the native way)

Nautilus default columns and columns order
https://askubuntu.com/questions/712047/how-to-set-visible-columns-default-for-the-files-file-manager/1062836#1062836
https://old.reddit.com/r/pop_os/comments/uezydz/nautilus_columns/
```
dconf write /org/gnome/nautilus/list-view/default-visible-columns "['name', 'size', 'date_modified', 'date_created']"
dconf write /org/gnome/nautilus/list-view/default-column-order "['name', 'size', 'date_modified', 'date_created']"
```

Switching windows and apps only on current workspace
```
# when using alt+tab
dconf write /org/gnome/shell/window-switcher/current-workspace-only true
# when using alt+`
dconf write /org/gnome/shell/app-switcher/current-workspace-only true
```

### Install Packages
```
ipython
python3-numpy
python3-ipdb
neovim
htop
tmux
fish
fzf
curl
gcc
cmake
make
git
gimp
python3-pip
silversearcher-ag
locate
ffmpeg
vlc
fdfind
```

### Add Useful Scripts
Optimize jpeg files:
```
jpegoptim --all-progressive --preserve --totals --verbose ./*
```

Recursive option (with parallel execution):
```
fdfind -e .jpg  --exec jpegoptim --all-progressive --preserve --totals --verbose
```

Overwrite and delete all files in directory:
```
fdfind --type file --hidden --exec shred --iterations=1 --remove='unlink' --verbose
```

Compare all images in two directories and save differences:
```
fdfind -e .jpg --base-directory <dir1> --exec compare <dir1>{} <dir2>{} -compose src <result dir>{}
```

Compare all images in two directories and save differences if images differ:
```
fdfind -e .jpg --base-directory todo_pictures_compare/Pictures2 --exec ./script {}
```
```
#!/usr/bin/fish

if not compare "/home/thomas/cloud_tmp/todo_pictures_compare/Pictures2/$argv[1]" \
        "/home/thomas/cloud_tmp/todo_pictures_compare/Pictures2_optimized/$argv[1]" \
        -compose src NULL:
  compare "/home/thomas/cloud_tmp/todo_pictures_compare/Pictures2/$argv[1]" \
        "/home/thomas/cloud_tmp/todo_pictures_compare/Pictures2_optimized/$argv[1]" \
        -compose src "/home/thomas/cloud_tmp/diffs/$argv[2]"
  echo "Found image with differences: $argv[1]"
end
```

```
function git_prune_merged
  get merged branches
  git branch --merged master
  delete branches
  git branch -d <>
  remore references to inexisting remote branches
  git fetch --prune
end
```

Find duplicate files
```
fclones group --hidden --no-ignore --symbolic-links --output duplicates.txt .

fclones remove --path ./Android2 --dry-run < duplicates.txt
```

### Make fish default shell
`chsh` command

## References
* https://dotfiles.github.io/
