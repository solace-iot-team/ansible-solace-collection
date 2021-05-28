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

  if [ -z "$WORKING_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: WORKING_DIR"; exit 1; fi
  if [ -z "$LOG_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi

##############################################################################################################################
# Settings
export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"
existingInventoryFile="$scriptDir/../files/broker.inventory.yml"
targetInventoryFile="$WORKING_DIR/broker.inventory.yml"

playbooks=(
  "$scriptDir/main.playbook.yml"
)

##############################################################################################################################
# Run
for playbook in ${playbooks[@]}; do

  playbook=$(assertFile $scriptLogName $playbook) || exit
  ansible-playbook \
                  $playbook \
                  --extra-vars "WORKING_DIR=$WORKING_DIR" \
                  --extra-vars "EXISTING_INVENTORY_FILE=$existingInventoryFile" \
                  --extra-vars "TARGET_INVENTORY_FILE=$targetInventoryFile" \
                  --extra-vars "REVERSE_PROXY_HOST=$REVERSE_PROXY_HOST" \
                  --extra-vars "REVERSE_PROXY_API_KEY=$REVERSE_PROXY_API_KEY" \
                  --extra-vars "REVERSE_PROXY_SEMP_BASE_PATH=$REVERSE_PROXY_SEMP_BASE_PATH"
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
