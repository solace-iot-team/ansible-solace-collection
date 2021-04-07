#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
testTarget=${scriptDir##*/}
scriptLogName="$testTargetGroup.$testTarget.$scriptName"
if [ -z "$PROJECT_HOME" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
source $PROJECT_HOME/.lib/functions.sh

############################################################################################################################
# Environment Variables

  if [ -z "$LOG_DIR" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$WORKING_DIR" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: WORKING_DIR"; exit 1; fi
  if [ -z "$RUN_FG" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: RUN_FG"; exit 1; fi
  if [ -z "$BROKER_DOCKER_IMAGE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: BROKER_DOCKER_IMAGE"; exit 1; fi
  if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY" ]; then
    export AZURE_VM_REMOTE_HOST_INVENTORY="$WORKING_DIR/azure/vm.inventory.json"
  fi
  if [ -z "$SSL_CERT_FILE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: SSL_CERT_FILE"; exit 1; fi
  if [ -z "$REQUESTS_CA_BUNDLE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: REQUESTS_CA_BUNDLE"; exit 1; fi

##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

##############################################################################################################################
# Settings

  # fix docker image to only one here
  BROKER_DOCKER_IMAGE="solace/solace-pubsub-standard:latest"
  remoteInventory=$(assertFile $scriptLogName "$AZURE_VM_REMOTE_HOST_INVENTORY") || exit
  localInventory=$(assertFile $scriptLogName "$scriptDir/files/inventory.yml") || exit
  playbooks=(
    "$scriptDir/delete.single-node.service.playbook.yml"
    "$scriptDir/create.single-node.plain+secure.playbook.yml"
    "$scriptDir/delete.single-node.service.playbook.yml"
  )
  sslCertFile="$scriptDir/files/secrets/asc.pem"

##############################################################################################################################
# Run

  runScript="$scriptDir/files/secrets/generateSelfSignedCert.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

  runScript="$scriptDir/files/secrets/addCert2PythonCABundle.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

  for playbook in ${playbooks[@]}; do

    playbook=$(assertFile $scriptLogName $playbook) || exit
    ansible-playbook \
                    -i $localInventory \
                    -i $remoteInventory \
                    $playbook \
                    --extra-vars "WORKING_DIR=$WORKING_DIR" \
                    --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE" \
                    --extra-vars "SSL_CERT_FILE=$sslCertFile"
    code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

  done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
