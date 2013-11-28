#!/bin/bash

# Installs toolbox in a virtualenv
VIRTUALENV=$(which virtualenv)
${VIRTUALENV} toolbox
cd toolbox
. bin/activate
mkdir src
git clone git://github.com/mozilla/toolbox.git
cd toolbox
python setup.py develop
# now run:
# paster serve paste.ini
# from the toolbox virtualenv to serve the sample app