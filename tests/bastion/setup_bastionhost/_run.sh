#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
testTarget=${scriptDir##*/}
scriptLogName="$testTargetGroup.$testTarget.$scriptName"
if [ -z "$PROJECT_HOME" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
source $PROJECT_HOME/.lib/functions.sh

############################################################################################################################
# Environment Variables

  if [ -z "$LOG_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$WORKING_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: WORKING_DIR"; exit 1; fi

##############################################################################################################################
# Prepare

  if [ -z "$AZURE_BROKER_PROJECT_NAME" ]; then export AZURE_BROKER_PROJECT_NAME="asct-broker"; fi
  if [ -z "$AZURE_BASTION_PROJECT_NAME" ]; then export AZURE_BASTION_PROJECT_NAME="asct-bastion"; fi
  if [ -z "$AZURE_LOCATION" ]; then export AZURE_LOCATION="westeurope"; fi
  if [ -z "$AZURE_VM_SEMP_PLAIN_PORT" ]; then export AZURE_VM_SEMP_PLAIN_PORT="8080"; fi
  if [ -z "$AZURE_VM_SEMP_SECURE_PORT" ]; then export AZURE_VM_SEMP_SECURE_PORT="1943"; fi
  # if [ -z "$AZURE_VM_ADMIN_USER" ]; then export AZURE_VM_ADMIN_USER="asct-admin"; fi
  # if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE" ]; then
  #   export AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE=$(assertFile $scriptLogName "$scriptDir/files/template.remotehost.inventory.yml") || exit
  # fi

  if [ -z "$CONFIG_DB_DIR" ]; then export CONFIG_DB_DIR="$WORKING_DIR/config_db"; mkdir -p $CONFIG_DB_DIR; fi
  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

##############################################################################################################################
# Run

  keysDir="$CONFIG_DB_DIR/azure_vms/$AZURE_BASTION_PROJECT_NAME"; mkdir -p $keysDir
  keyName="vm_key"
  # keysDir="$CONFIG_DB_DIR/keys"; mkdir -p $keysDir
  # keyName="$AZURE_BASTION_PROJECT_NAME"_key
  playbook=$(assertFile $scriptLogName "$scriptDir/generate-keys.playbook.yml") || exit
  ansible-playbook \
                $playbook \
                --extra-vars "WORKING_DIR=$WORKING_DIR" \
                --extra-vars "KEYS_DIR=$keysDir" \
                --extra-vars "KEY_NAME=$keyName"
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

  export SSH_PUBLIC_KEY_FILE="$keysDir/$keyName.pub"
  export SSH_PRIVATE_KEY_FILE="$keysDir/$keyName"
  runScript="$scriptDir/../azure/bastion-vm/create.az.vm.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

  inventoryFile=$(assertFile $scriptLogName "$CONFIG_DB_DIR/azure_vms/$AZURE_BASTION_PROJECT_NAME/vm.inventory.json") || exit
  playbook=$(assertFile $scriptLogName "$scriptDir/bootstrap.playbook.yml") || exit
  privateKeyFile=$SSH_PRIVATE_KEY_FILE
  requirementsFile=$(assertFile $scriptLogName "$scriptDir/files/requirements.txt") || exit
  ansible-playbook \
                -i $inventoryFile \
                $playbook \
                --private-key $privateKeyFile \
                --extra-vars "PYTHON_REQUIREMENTS_FILE=$requirementsFile"
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

###
# The End.
