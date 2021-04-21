#!/usr/bin/env bash
# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
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
  if [ -z "$AZURE_BASTION_PROJECT_NAME" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: AZURE_BASTION_PROJECT_NAME"; exit 1; fi
  if [ -z "$SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS"; exit 1; fi

##############################################################################################################################
# Prepare

  if [ -z "$CONFIG_DB_DIR" ]; then export CONFIG_DB_DIR="$WORKING_DIR/config_db"; fi
  if [ ! -d "$CONFIG_DB_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - directory not found: CONFIG_DB_DIR=$CONFIG_DB_DIR"; exit 1; fi
  export RUN_TIME_DIR="$WORKING_DIR/run-time"; mkdir -p $RUN_TIME_DIR
  export ANSIBLE_SOLACE_CONTROLLER_LOGS_BASE_PATH="$LOG_DIR/$scriptLogName"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

##############################################################################################################################
# Test

  tree $CONFIG_DB_DIR

##############################################################################################################################
# Run

  inventory_array=($(ls $CONFIG_DB_DIR/broker_services/**/bastion.broker_service.inventory.yml))
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, ls inventory files"; exit 1; fi
  inventory_line=""
  for inventory in ${inventory_array[@]}; do
    inventory_file=$(assertFile $scriptLogName "$inventory") || exit
    inventory_line+="-i $inventory_file "
  done
  # echo $inventory_line
  playbooks=(
    "$scriptDir/main.playbook.yml"
  )
  bastionPrivateKeyFile=$(assertFile $scriptLogName "$CONFIG_DB_DIR/azure_vms/$AZURE_BASTION_PROJECT_NAME/vm_key") || exit
  for playbook in ${playbooks[@]}; do

    playbook=$(assertFile $scriptLogName $playbook) || exit
    ansible-playbook \
                  $inventory_line \
                  $playbook \
                  --private-key $bastionPrivateKeyFile \
                  --extra-vars "RUN_TIME_DIR=$RUN_TIME_DIR" \
                  --extra-vars "SOLACE_CLOUD_API_TOKEN=$SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS" \
                  --extra-vars "ANSIBLE_SOLACE_CONTROLLER_LOGS_BASE_PATH=$ANSIBLE_SOLACE_CONTROLLER_LOGS_BASE_PATH"
    code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

  done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
