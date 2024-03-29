#!/bin/bash
# Build the macos app

# Created 2022 by James Bishop (james@bishopdynamics.com)

APP_NAME='TreeView'
VENV_NAME='venv'

function bail() {
	echo "An unexpected error occurred"
	exit 1
}

# create venv if missing
if [ ! -d "$VENV_NAME" ]; then
  ./setup-venv.sh || bail
fi

# we need modules in the venv
# now activate the venv so we can install stuff inside it
if [ "$(uname -s)" == "Darwin" ] || [ "$(uname -s)" == "Linux" ]; then
  source "${VENV_NAME}/bin/activate" || bail
else
  # assume Windows
  source "${VENV_NAME}/Scripts/activate" || bail
fi

# make sure our build workspace is clean
rm -rf build dist

# store the current commit id into a file: commit_id which will end up inside the app under "data"
GIT_COMMIT=$(git rev-parse --short HEAD)
echo "$GIT_COMMIT" > commit_id

# using the .spec file, build a macos app out of our project
if [ "$(uname -s)" == "Darwin" ]; then
  # do not use onefile for macos, since it builds an app
  pyinstaller ${APP_NAME}.macos.spec || {
    deactivate
    bail
  }
else
  # use onefile option for Linux and Windows
  pyinstaller ${APP_NAME}.spec || {
    deactivate
    bail
  }
fi

rm -r build || bail

# zip up the app for release
ZIP_FILE_NAME="${APP_NAME}_${GIT_COMMIT}.zip"
echo "Creating archive: ${ZIP_FILE_NAME}"

if [ "$(uname -s)" == "Darwin" ]; then
  # on macos, we must properly zip the resulting app in order to distribute it
  pushd 'dist' || bail
  # this command is exactly the same as when you right-click and Compress in the UI
  #   https://superuser.com/questions/505034/compress-files-from-os-x-terminal
  ditto -c -k --sequesterRsrc --keepParent ${APP_NAME}.app "${ZIP_FILE_NAME}" || {
    echo "failed to compress app using \"ditto\" command"
    bail
  }
  popd || bail
fi

# all done, deactivate the venv
deactivate

if [ "$(uname -s)" == "Darwin" ]; then
  echo "Success, resulting app: \"dist/${APP_NAME}.app"
elif [ "$(uname -s)" == "Linux" ]; then
  echo "Success, resulting binary: \"dist/${APP_NAME}"
else
  # assume Windows
  echo "Success, resulting executable: \"dist/${APP_NAME}.exe"
fi
