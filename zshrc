LOCAL_HOME="$HOME"
[[ -f "$ZDOTDIR/zshextra" ]] && source "$ZDOTDIR/zshextra"
if [[ $TERM == "screen.xterm-256color" ]]
then
  export TERM=xterm-256color
fi

# Path to your oh-my-zsh installation.
export ZSH="$LOCAL_HOME/.local/share/zsh/oh-my-zsh"

ZSH_THEME="lambda"

# Uncomment the following line to enable command auto-correction.
ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
COMPLETION_WAITING_DOTS="true"

plugins=(
  git
  colored-man-pages
  vi-mode
)

zle -N __clear__
source $ZSH/oh-my-zsh.sh
autoload -Uz surround
zle -N delete-surround surround
zle -N add-surround surround
zle -N change-surround surround
bindkey -a cs change-surround
bindkey -a ds delete-surround
bindkey -a ys add-surround
bindkey -M visual S add-surround
bindkey -M vicmd 'H' beginning-of-line
bindkey -M vicmd 'L' end-of-line
bindkey -M viins '^A' beginning-of-line
bindkey -M viins '^E' end-of-line
bindkey -M viins '^P' history-search-backward
bindkey -M viins '^N' history-search-forward
bindkey -M viins '^U' backward-kill-line
bindkey -M viins '^L' __clear__

function __clear__() {
  yes ' ' | head --lines 200
  clear
  zle reset-prompt
}

function activate() {
  if [[ -z $1 ]]
  then
    if [[ -f ./venv/bin/activate ]]
    then
      source ./venv/bin/activate
    fi
  else
    [[ -f $1/bin/activate ]] && source $1/bin/activate
  fi
}

# Use ripgrep for fzf search
export FZF_DEFAULT_COMMAND="fd"
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# lsd aliases
alias ls='lsd'
alias l='ls -l'
alias la='ls -a'
alias ll='ls -la'
alias lt='ls --tree'

KEYMAP=main

# -------------------
# User configuration
# -------------------
# Prompt
PS1='%(?:$fg[green]:$fg[red])◉ %{$fg[cyan]%}%~%{$reset_color%} $(git_prompt_info)
 (${${KEYMAP/vicmd/cmd}/(viins|main)/ins}) λ > '
PS2=' (${${KEYMAP/vicmd/cmd}/(viins|main)/ins})   > '

function set_brightness() {
  xrandr \
  | grep '[^(dis)]connected' \
  | cut --delimiter ' ' --fields 1 \
  | xargs --replace={} xrandr --output {} --brightness $1
}
function cd() {
  HOME="$LOCAL_HOME" builtin cd $@
}
function __fix_compile_database__() {
  ln --symbolic --force build/debug/gcc/compile_commands.json
  setopt local_options nonomatch
  for pch in build/**/cmake_pch.hxx; do
    [[ -e "$pch" ]] || continue
    ln --symbolic --force cmake_pch.hxx ${pch%.hxx}_.hxx
  done
  for cmd_db in build/**/compile_commands.json; do
    [[ -e "$cmd_db" ]] || continue
    sed --in-place 's/cmake_pch.hxx/cmake_pch_.hxx/g' $cmd_db
  done
}
function __cmake_config__() {
  if [[ ! -f 'CMakeLists.txt' ]] then; return; fi
  zparseopts -D           \
    -libcxx=use_libcxx    \
    -asan=use_address_san \
    -msan=use_memory_san \
    -ubsan=use_ub_san     \

  build_dirs=(debug/gcc release/gcc san/gcc debug/clang release/clang san/clang)

  for d in $build_dirs; do
    printf %"$COLUMNS"s'\n' |tr ' ' '-'
    echo at: $d

    rm --force build/$d/CMakeCache.txt
    mkdir --parents build/$d
    local extra_opts=($@)

    if [[ $d == san* ]]
    then
      local build_type=Debug

      if [[ -n $use_address_san ]] then
        local extra_opts=($extra_opts '-DENABLE_SANITIZER_ADDRESS=ON')
      fi
      if [[ -n $use_memory_san ]] then
        local extra_opts=($extra_opts '-DENABLE_SANITIZER_MEMORY=ON')
      fi
      if [[ -n $use_ub_san ]] then
        local extra_opts=($extra_opts '-DENABLE_SANITIZER_UNDEFINED_BEHAVIOR=ON')
      fi

    elif [[ $d == debug* ]]
    then
      local build_type=Debug
    else
      local build_type=Release
    fi

    local use_libcxx=''
    if [[ $d == *gcc ]]
    then
      local CC=gcc
      local CXX=g++
    else
      local CC=clang
      local CXX=clang++
      if [[ -n $use_libcxx ]] then
        local extra_opts=($extra_opts '-DUSE_LIBCXX=ON')
      fi
    fi

    CC=$CC CXX=$CXX \
      cmake -H. -B build/$d \
      -DCMAKE_BUILD_TYPE=$build_type $extra_opts \
      || return -1

    if [[ $d == debug/gcc ]]
    then
      __fix_compile_database__
    fi
  done
}
function __cmake_run__() {
  /usr/bin/time --format '\nCompilation time: %E' \
    make -j4 --directory $1 $2
  local err=$?
  __fix_compile_database__

  if [[ $err != 0 ]] then
    return $err
  fi

  local bin_file=./$1/bin/$2
  if [[ ! -f $bin_file ]] then
    local bin_file=./$1/$2
  fi
  if [[ ! -f $bin_file ]] then
    return 0;
  fi

  local args=($@)
  args=($args[3,-1])
  echo '\nRunning:\n'$bin_file $args'\n'
  $bin_file $args
  return $?
}
function __cmake_show_options__() {
  __cmake_config__ $@ --log-level=WARNING -DCONAN_QUIET=ON -LH
}
function new () {
  local output=$($DOTDIR/proj $@)
  echo $output | head --lines -2
  local post_cmd=$(echo $output | tail --lines 2 | head --lines 1)
  local name=$(echo $output | tail --lines 1)
  cd $name
  eval $post_cmd
}

alias cconfig=__cmake_config__
alias crun=__cmake_run__
alias copt=__cmake_show_options__

function __cmake_run__completion() {
  _arguments '1:build_dir:_dirs' '2:targets:->targets'
  case $state in
    (targets)
      local target_list=$(make -C "$words[2]" help \
                          | tail --lines=+3 \
                          | head --lines=-1 \
                          | cut --delimiter=' ' --fields='2')
      compadd ${(f)target_list}
      ;;
  esac
}

# 10ms for key sequences
KEYTIMEOUT=1

export LANG=en_US.UTF-8
export EDITOR='nvim'

alias vim=nvim
alias base="activate ""$LOCAL_HOME/.local/share/python/venv"
alias o=xdg-open
alias e=code -r
alias   use-gcc="sudo update-alternatives --set cc  /usr/bin/gcc    &&\
                 sudo update-alternatives --set c++ /usr/bin/g++      "
alias use-clang="sudo update-alternatives --set cc  /usr/bin/clang  &&\
                 sudo update-alternatives --set c++ /usr/bin/clang++  "
function disassemble() {
  local merge_call_lines=(
    '/ *[0-f]*:\t\([0-f][0-f] \)* *\tcall/{'
    'N; s/\( *[0-f]*:\t\([0-f][0-f] \)* *\t'
    'call\) .*'
    'R_X86_64_PLT32\t/\1   /g}'
  )
  local merge_jmp_lines=(
    '/ *[0-f]*:\t\([0-f][0-f] \)* *\tjmp/{'
    'N; s/\( *[0-f]*:\t\([0-f][0-f] \)* *\t'
    'jmp\) .*'
    'R_X86_64_PLT32\t/\1   /g}'
  )
  objdump                                           \
      --disassemble                                 \
      --reloc                                       \
      --demangle                                    \
      --line-numbers                                \
      -M intel                                      \
      --source $@                                   \
  | sed '/^ *[0-f]*:\t\([0-f][0-f] \)*$/d'                  \
  | sed ${(j::)merge_call_lines}                    \
  | sed ${(j::)merge_jmp_lines}                    \

}

# Completions
fpath=($LOCAL_HOME/.local/share/zsh/completions $fpath)
export fpath
autoload -Uz compinit
if [[ -f ./venv/bin/activate &&  $(date +'%j') != \
  $(date +'%j' --reference /tmp/.zcompdump)  ]]; then
  compinit -d /tmp/.zcompdump
else
  compinit -C -d /tmp/.zcompdump
fi

compdef __cmake_run__completion __cmake_run__

# Rust paths
export CARGO_HOME="$LOCAL_HOME/.cargo"
export RUSTUP_HOME="$LOCAL_HOME/.rustup"
export VCPKG_ROOT=$LOCAL_HOME/vcpkg
export VCPKG_FEATURE_FLAGS=manifests,
export VCPKG_DISABLE_METRICS=

PATH="$LOCAL_HOME/.cargo/bin:$PATH"
PATH="$LOCAL_HOME/.local/bin:$PATH"
PATH="/snap/bin:$PATH"
PATH="$HOME/.yarn/bin:$PATH"
PATH="$HOME/.config/yarn/global/node_modules/.bin:$PATH"
PATH="$HOME/.node/bin:$PATH"
export PATH

MANPATH="$LOCAL_HOME/.cargo/share/man:$MANPATH"
MANPATH="$LOCAL_HOME/.local/share/man:$MANPATH"

base

export CMAKE_EXPORT_COMPILE_COMMANDS=ON
export ASAN_OPTIONS="detect_stack_use_after_return=1"
export UBSAN_OPTIONS="print_stacktrace=1"
export MSAN_OPTIONS="poison_in_dtor=1"
export RUSTFLAGS="-C target-cpu=native"

SAN_FLAGS=(-g
           -fsanitize=address,undefined
           -fno-omit-frame-pointer
           -fno-optimize-sibling-calls
           -fsanitize-address-use-after-scope)

function run-steam() {
  export XDG_CONFIG_HOME=$LOCAL_HOME/.config/
  export XDG_DATA_HOME=$LOCAL_HOME/.local/share/
  flatpak run com.valvesoftware.Steam & disown
  exit
}
