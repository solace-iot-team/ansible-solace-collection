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

##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

##############################################################################################################################
# Settings

remoteInventory=$(assertFile $scriptLogName "$AZURE_VM_REMOTE_HOST_INVENTORY") || exit
remote_playbooks=(
  # "$scriptDir/create.remote.playbook.yml"
  # "$scriptDir/delete.remote.playbook.yml"
)

localInventory=$(assertFile $scriptLogName "$scriptDir/files/inventory.yml") || exit
local_playbooks=(
  # "$scriptDir/create.local-plain.playbook.yml"
  "$scriptDir/create.local-secure.playbook.yml"
  # "$scriptDir/delete.local.playbook.yml"
)

sslCertFile="$scriptDir/files/secrets/asc.pem"

# # looks like python requires this?
# CERT_FILE=$(python -m certifi)
# export SSL_CERT_FILE=${CERT_FILE}
# export REQUESTS_CA_BUNDLE=${CERT_FILE}

##############################################################################################################################
# Run Remote
for playbook in ${remote_playbooks[@]}; do

  playbook=$(assertFile $scriptLogName $playbook) || exit
  ansible-playbook \
                  -i $remoteInventory \
                  $playbook \
                  --extra-vars "WORKING_DIR=$WORKING_DIR" \
                  --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE"
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

done

##############################################################################################################################
# Run Local
for playbook in ${local_playbooks[@]}; do

  playbook=$(assertFile $scriptLogName $playbook) || exit
  ansible-playbook \
                  -i $localInventory \
                  $playbook \
                  --extra-vars "WORKING_DIR=$WORKING_DIR" \
                  --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE" \
                  --extra-vars "BROKER_HOST_MOUNT_PATH_DATA=$WORKING_DIR/broker_mount_data" \
                  --extra-vars "BROKER_HOST_MOUNT_PATH_SECRETS=$WORKING_DIR/broker_mount_secrets" \
                  --extra-vars "SSL_CERT_FILE=$sslCertFile"
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
