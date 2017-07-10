#!/bin/sh

found_exe() {
    hash "$1" 2>/dev/null
}

check_no_root() {
    if [ $(id -u) -eq 0 ]; then
      echo "This script should not be run as root or with sudo."
      exit 1
    fi
}

install_deps() {
    if found_exe apt-get; then
        echo "Installing python3-pip portaudio19-dev swig vvirtualenv libyaml-dev..."
        sudo apt-get install -y python3-pip portaudio19-dev swig virtualenv libyaml-dev
    else
        if found_exe tput; then
			green="$(tput setaf 2)"
			blue="$(tput setaf 4)"
			reset="$(tput sgr0)"
    	fi
    	echo
        echo "${green}Could not find package manager"
        echo "${green}Make sure to manually install: ${blue}python3-pip portaudio19-dev swig virtualenv libyaml-dev"
        echo $reset
    fi
}

installed_deps() {
    [ -f ".installed_deps" ]
}

mark_complete() {
    touch .installed_deps
}

update_param() {
    [ "$#" -ge "1" ] && [ "$1" = "update" ]
}

find_virtualenv_root() {
    if [ -z "$WORKON_HOME" ]; then
        VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/mycroft_simple"}
    else
        VIRTUALENV_ROOT="$WORKON_HOME/mycroft_simple"
    fi
}

create_virtualenv() {
    if [ ! -d "${VIRTUALENV_ROOT}" ]; then
        mkdir -p $(dirname "${VIRTUALENV_ROOT}")
        virtualenv -p python3 "${VIRTUALENV_ROOT}"
    fi
}

activate_virtualenv() {
    . "${VIRTUALENV_ROOT}/bin/activate"
}

set -eE

if ! installed_deps || update_param $@; then
    install_deps
fi

check_no_root

if update_param $@; then
    git pull --ff-only
fi

find_virtualenv_root
create_virtualenv

activate_virtualenv

if ! found_exe mycroft_simple; then
    pip3 install -e .
fi

mark_complete

mycroft_simple
