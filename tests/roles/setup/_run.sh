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

  if [ -z "$AZURE_PROJECT_NAME" ]; then export AZURE_PROJECT_NAME="asct"; fi
  if [ -z "$AZURE_LOCATION" ]; then export AZURE_LOCATION="westeurope"; fi
  # az vm image list --output table
  # az vm image list --offer UbuntuServer --all --output table
  if [ -z "$AZURE_VM_IMAGE_URN" ]; then export AZURE_VM_IMAGE_URN="UbuntuLTS"; fi
  if [ -z "$AZURE_VM_SEMP_PORT" ]; then export AZURE_VM_SEMP_PORT="8080"; fi
  if [ -z "$AZURE_VM_ADMIN_USER" ]; then export AZURE_VM_ADMIN_USER="$AZURE_PROJECT_NAME-admin"; fi
  if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE" ]; then
    export AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE=$(assertFile $scriptLogName "$scriptDir/files/template.remotehost.inventory.yml") || exit
  fi
  if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY" ]; then export AZURE_VM_REMOTE_HOST_INVENTORY="$WORKING_DIR/azure/vm.inventory.json"; fi

##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

##############################################################################################################################
# Run

runScript="$scriptDir/../azure/create.az.vm.sh"
$runScript
code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
