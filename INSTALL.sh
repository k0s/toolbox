#!/bin/bash

# Installs toolbox in a virtualenv
VIRTUALENV=$(which virtualenv)
${VIRTUALENV} toolbox
cd toolbox
. bin/activate
mkdir src
git clone https://github.com/k0s/toolbox # TODO
cd toolbox
python setup.py develop
# now run: 
# paster serve paste.ini
# from the toolbox virtualenv