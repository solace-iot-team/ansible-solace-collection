#!/usr/bin/env bash
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
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
  if [ -z "$SOLACE_CLOUD_API_TOKEN_US" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: SOLACE_CLOUD_API_TOKEN_US"; exit 1; fi
  if [ -z "$SOLACE_CLOUD_API_TOKEN_AU" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: SOLACE_CLOUD_API_TOKEN_AU"; exit 1; fi

##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

##############################################################################################################################
# Settings

inventory=$(assertFile $scriptLogName $INVENTORY_FILE) || exit

playbooks=(
  "$scriptDir/setup.playbook.yml"
  "$scriptDir/ex.playbook.yml"
)

homeClouds=(
  "NOT_SET"
  "AU"
  "US"
)

##############################################################################################################################
# Run
for playbook in ${playbooks[@]}; do

  for homeCloud in ${homeClouds[@]}; do

    if [[ "$homeCloud" == "NOT_SET" ]]; then
      unset ANSIBLE_SOLACE_SOLACE_CLOUD_HOME;
    else
      export ANSIBLE_SOLACE_SOLACE_CLOUD_HOME="$homeCloud"
    fi

    export SOLACE_CLOUD_INVENTORY_FILE_NAME="solace_cloud.inventory.$homeCloud.yml"

    # debug
    # echo ">>> XT_DEBUG:$scriptLogName: ANSIBLE_SOLACE_SOLACE_CLOUD_HOME=$ANSIBLE_SOLACE_SOLACE_CLOUD_HOME"
    # echo ">>> XT_DEBUG:$scriptLogName: SOLACE_CLOUD_API_TOKEN=$SOLACE_CLOUD_API_TOKEN"
    # echo;

    playbook=$(assertFile $scriptLogName $playbook) || exit
    ansible-playbook \
                    -i $inventory \
                    $playbook \
                    --extra-vars "WORKING_DIR=$WORKING_DIR" \
                    --extra-vars "SOLACE_CLOUD_API_TOKEN_US=$SOLACE_CLOUD_API_TOKEN_US" \
                    --extra-vars "SOLACE_CLOUD_API_TOKEN_AU=$SOLACE_CLOUD_API_TOKEN_AU" \
                    --extra-vars "ANSIBLE_SOLACE_SOLACE_CLOUD_HOME=$ANSIBLE_SOLACE_SOLACE_CLOUD_HOME" \
                    --extra-vars "SOLACE_CLOUD_INVENTORY_FILE_NAME=$SOLACE_CLOUD_INVENTORY_FILE_NAME"

    code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

  done

done

##############################################################################################################################
# Run Post setup playbooks

playbooks=(
  "$scriptDir/module-params.playbook.yml"
  "$scriptDir/teardown.playbook.yml"
)

for playbook in ${playbooks[@]}; do

  for homeCloud in ${homeClouds[@]}; do

    if [[ "$homeCloud" == "NOT_SET" ]]; then
      unset ANSIBLE_SOLACE_SOLACE_CLOUD_HOME;
    else
      export ANSIBLE_SOLACE_SOLACE_CLOUD_HOME="$homeCloud"
    fi

    export SOLACE_CLOUD_INVENTORY_FILE_NAME="solace_cloud.inventory.$homeCloud.yml"
    inventory_file="$WORKING_DIR/$SOLACE_CLOUD_INVENTORY_FILE_NAME"

    playbook=$(assertFile $scriptLogName $playbook) || exit
    ansible-playbook \
                    -i $inventory_file \
                    $playbook \
                    --extra-vars "WORKING_DIR=$WORKING_DIR" \
                    --extra-vars "SOLACE_CLOUD_API_TOKEN_US=$SOLACE_CLOUD_API_TOKEN_US" \
                    --extra-vars "SOLACE_CLOUD_API_TOKEN_AU=$SOLACE_CLOUD_API_TOKEN_AU" \
                    --extra-vars "ANSIBLE_SOLACE_SOLACE_CLOUD_HOME=$ANSIBLE_SOLACE_SOLACE_CLOUD_HOME" \
                    --extra-vars "SOLACE_CLOUD_INVENTORY_FILE_NAME=$SOLACE_CLOUD_INVENTORY_FILE_NAME"

    code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

  done

done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
