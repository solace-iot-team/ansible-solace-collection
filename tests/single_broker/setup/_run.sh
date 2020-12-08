#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
if [ -z "$PROJECT_HOME" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
projectHome=$PROJECT_HOME
source $projectHome/.lib/functions.sh
testTarget=${scriptDir##*/}
scriptLogName="$testTargetGroup.$testTarget.$scriptName"

############################################################################################################################
# Environment Variables

  if [ -z "$LOG_DIR" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$WORKING_DIR" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: WORKING_DIR"; exit 1; fi
  if [ -z "$RUN_FG" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: RUN_FG"; exit 1; fi
  if [ -z "$INVENTORY_FILE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: INVENTORY_FILE"; exit 1; fi

  if [ -z "$BROKER_TYPE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: BROKER_TYPE"; exit 1; fi
  if [[ "$BROKER_TYPE" == "local" ]]; then
    if [ -z "$BROKER_DOCKER_IMAGE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: BROKER_DOCKER_IMAGE"; exit 1; fi
    if [ -z "$BROKER_DOCKER_COMPOSE_FILE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: BROKER_DOCKER_COMPOSE_FILE"; exit 1; fi
    if [ -z "$LOCAL_BROKER_INVENTORY_FILE" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: LOCAL_BROKER_INVENTORY_FILE"; exit 1; fi
  elif [[ "$BROKER_TYPE" == "solace_cloud" ]]; then
    if [ -z "$SOLACE_CLOUD_API_TOKEN" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: SOLACE_CLOUD_API_TOKEN"; exit 1; fi
  else echo ">>> ERROR: - $scriptLogName - unknown BROKER_TYPE=$BROKER_TYPE"; exit 1; fi


##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"
  rm -rf $WORKING_DIR/*

##############################################################################################################################
# Settings

inventory=$(assertFile $scriptLogName $INVENTORY_FILE) || exit

playbooks=(
  "$scriptDir/main.playbook.yml"
)

##############################################################################################################################
# Run
for playbook in ${playbooks[@]}; do

  playbook=$(assertFile $scriptLogName $playbook) || exit
  ansible-playbook \
                  -i $inventory \
                  $playbook \
                  --extra-vars "WORKING_DIR=$WORKING_DIR" \
                  --extra-vars "BROKER_TYPE=$BROKER_TYPE" \
                  --extra-vars "SOLACE_CLOUD_API_TOKEN=$SOLACE_CLOUD_API_TOKEN" \
                  --extra-vars "LOCAL_BROKER_INVENTORY_FILE=$LOCAL_BROKER_INVENTORY_FILE" \
                  --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE" \
                  --extra-vars "BROKER_DOCKER_COMPOSE_FILE=$BROKER_DOCKER_COMPOSE_FILE"

  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
