#!/bin/bash

PARENT_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}")" && cd .. && pwd )"

# command line arguments
ENV_DIR=${1:-$PARENT_DIR/env}
CORE_ROOT=${2:-$PARENT_DIR}

# check for dependencies
if ! hash virtualenv 2>/dev/null; then
        echo "The virtualenv executable is not installed."
        echo "Install using 'pip install virtualenv'"
        exit 1
fi

# check if environment directory exists
if [ -d "$ENV_DIR" ]; then
    echo "Environment directory already exists, updating"
else
    # create the virtualenv
    virtualenv "$ENV_DIR"
fi

# activate the virtualenv
source "$ENV_DIR/bin/activate"

# install or upgrade the athos code in the virtualenv
pip install --upgrade "$CORE_ROOT"