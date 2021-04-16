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
  sudo apt-get update
  sudo apt-get -y upgrade
  # echo ">>> docker =================================================="
  # sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y
  # curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  # sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
  # apt-cache policy docker-ce
  # sudo apt-get install --upgrade docker-ce -y
  echo ">>> python =================================================="
  sudo apt-get install --upgrade python3
  sudo apt-get install --upgrade python3-pip -y
  sudo -H python3 -m pip install --upgrade pip
  # sudo -H python3 -m pip install --upgrade docker
  # sudo -H python3 -m pip install --upgrade docker-compose
  echo ">>> upgrading =================================================="
  sudo apt-get update
  sudo apt-get -y upgrade
BOOT_EOL

if [[ $? != 0 ]]; then echo " >>> XT_ERROR: bootstrap vm"; exit 1; fi

echo " >>> Success."


###
# The End.
