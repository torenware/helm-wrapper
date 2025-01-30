#! /usr/bin/env bash

set -e

if [ ! -f ./hwrap_settings.py ]; then
  echo "The hwrap_settings.py file should be in the current directory" >&2
  exit 1
fi

. ./hwrap_settings.py

if [ ! -f $REAL_HELM -o ! -x $REAL_HELM ]; then
  echo "Warning: helm executable not found at $REAL_HELM" >&2
  exit 1
fi 

if ! ping -c 3 $HARBOR_HOST ; then
  echo "Could not find a server (hoping harbor) at $HARBOR_HOST" >&2 
  exit 1
else
  echo "DNS for our harbor host resolves" >&2
fi 

echo "Copying components to the $WRAPPER_INSTALL_DIR directory..."
echo
echo "cp helm-wrapper $WRAPPER_INSTALL_DIR/helm"
sudo cp helm-wrapper $WRAPPER_INSTALL_DIR/helm
echo "cp helm_wrap.py $WRAPPER_INSTALL_DIR"
sudo cp helm_wrap.py $WRAPPER_INSTALL_DIR
echo "cp hwrap_settings.py $WRAPPER_INSTALL_DIR"
sudo cp hwrap_settings.py $WRAPPER_INSTALL_DIR

if type -a helm | grep $WRAPPER_INSTALL_DIR/helm > /dev/null ; then 
  echo "helm installed in $WRAPPER_INSTALL_DIR"
  HELM_IN_PATH=$(type -p helm)
  if [ "$HELM_IN_PATH" != $WRAPPER_INSTALL_DIR/helm ]; then
    echo "BUT... fake helm is not first in path :-("
  fi
fi




