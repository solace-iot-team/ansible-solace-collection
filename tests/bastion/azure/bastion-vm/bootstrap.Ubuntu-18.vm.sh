#!/usr/bin/env bash

scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));

############################################################################################################################
# Bootstrap Ubuntu-18 VM with prerequisites to run role solace_broker_service.
# Note:
#   ssh requires public key to be available in ~/.ssh/
#


############################################################################################################################
# Check Environment Variables

  if [ -z "$vmAdminUsr" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: vmAdminUsr"; exit 1; fi
  if [ -z "$vmPublicIpAddress" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: vmPublicIpAddress"; exit 1; fi
  if [ -z "$vmPrivateKeyFile" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: vmPrivateKeyFile"; exit 1; fi

############################################################################################################################
# Run

echo " >>> Bootstrap vm ..."

ssh -i $vmPrivateKeyFile "$vmAdminUsr@$vmPublicIpAddress" <<BOOT_EOL
  echo ">>> uptime =================================================="
  uptime
  sleep 60
  uptime
  sleep 30
  echo ">>> update =================================================="
  sudo apt-get update
  if [[ $? != 0 ]]; then exit 1; fi
  sleep 10
  sudo apt-get -y upgrade
  if [[ $? != 0 ]]; then exit 1; fi
  echo ">>> python =================================================="
  sudo apt-get install --upgrade python3
  if [[ $? != 0 ]]; then exit 1; fi
  sudo apt-get install --upgrade python3-pip -y
  if [[ $? != 0 ]]; then exit 1; fi
  sudo -H python3 -m pip install --upgrade pip
  if [[ $? != 0 ]]; then exit 1; fi
  echo ">>> upgrading =================================================="
  sudo apt-get update
  if [[ $? != 0 ]]; then exit 1; fi
  sudo apt-get -y upgrade
  if [[ $? != 0 ]]; then exit 1; fi
BOOT_EOL

if [[ $? != 0 ]]; then echo " >>> XT_ERROR: bootstrap vm"; exit 1; fi

echo " >>> Success."


###
# The End.
