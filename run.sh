#!/bin/sh

apt_packages="python3-pip portaudio19-dev python3-dev swig virtualenv libyaml-dev libpulse-dev vlc libfann-dev"
pip_packages="$(cat setup.py | tr -d '\n' | tr -d ' ' | grep -Eo 'install_requires=\[[^]]*\]')"

found_exe() {
    hash "$1" 2>/dev/null
}

found_lib() {
    IFS=:
    found=1

    for p in ${LD_LIBRARY_PATH}; do
        if [ -e ${p}/$1 ]; then
            found=0
        fi
    done
    IFS=$' '
    return $found
}

check_no_root() {
    if [ $(id -u) -eq 0 ]; then
      echo "This script should not be run as root or with sudo."
      exit 1
    fi
}

install_fann() {
    echo "Compiling FANN..."
    if ! found_exe cmake; then
        echo "Please install cmake first."
        exit 1
    fi
    rm -rf /var/tmp/fann-2.2.0
    curl -L https://github.com/libfann/fann/archive/2.2.0.tar.gz | tar xvz -C /var/tmp
    pushd /var/tmp/fann-2.2.0
    cmake .
    sudo make install
    popd
}

install_deps() {
    if found_exe apt-get; then
        echo "Installing $apt_packages..."
        sudo apt-get install -y $apt_packages
        fann_version=$(dpkg -s libfann-dev 2>/dev/null | grep Version | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+')
        if [ $fann_version == 0.2.2 ]; then
            sudo apt-get remove -y libfann-dev
        fi
    else
        if found_exe tput; then
			green="$(tput setaf 2)"
			blue="$(tput setaf 4)"
			reset="$(tput sgr0)"
    	fi
    	echo
        echo "${green}Could not find package manager"
        echo "${green}Make sure to manually install:${blue} $apt_packages"
        echo $reset
    fi
    if ! found_lib libdoublefann.so; then
        install_fann /var/tmp/fann
    fi
}

installed_deps() {
    [ -f ".installed_deps" ] && [ "$(cat .installed_deps)" == "$apt_packages $pip_packages" ]
}

mark_complete() {
    echo "$apt_packages $pip_packages" > .installed_deps
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

if ! found_exe mycroft_simple || ! installed_deps; then
    pip3 install -e .
fi

mark_complete

mycroft_simple
