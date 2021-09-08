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
  if [ -z "$RUN_FG" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: RUN_FG"; exit 1; fi
  if [ -z "$BROKER_DOCKER_IMAGE" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: BROKER_DOCKER_IMAGE"; exit 1; fi

##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"
  export RUN_TIME_DIR_LOCAL="$WORKING_DIR/run-time"; mkdir -p $RUN_TIME_DIR_LOCAL
  if [ -z "$CONFIG_DB_DIR" ]; then
    export CONFIG_DB_DIR="$WORKING_DIR/config_db";
    mkdir -p $CONFIG_DB_DIR
  fi
  brokerDockerComposeFile=$(assertFile $scriptLogName "$scriptDir/templates/PubSubStandard_singleNode.yml") || exit
  brokerDockerComposeFilePlainSecure=$(assertFile $scriptLogName "$scriptDir/templates/PubSubStandard_singleNode.plain+secure.yml") || exit
  localInventory=$(assertFile $scriptLogName "$scriptDir/files/inventory.yml") || exit

  playbooks=(
    "$scriptDir/delete.single-node.service.playbook.yml"
    "$scriptDir/create.single-node.default.playbook.yml"
    "$scriptDir/delete.single-node.service.playbook.yml"
    "$scriptDir/create.single-node.plain+secure.playbook.yml"
    "$scriptDir/delete.single-node.service.playbook.yml"
  )
  sslCertFile="$scriptDir/files/secrets/dummy.pem"

  # wipe docker clean
  # docker container stop $(docker container ls –aq)
  # docker system prune -af --volumes

##############################################################################################################################
# Run

  for playbook in ${playbooks[@]}; do

    playbook=$(assertFile $scriptLogName $playbook) || exit
    ansible-playbook \
                    -i $localInventory \
                    $playbook \
                    --extra-vars "CONFIG_DB_DIR=$CONFIG_DB_DIR" \
                    --extra-vars "RUN_TIME_DIR_LOCAL=$RUN_TIME_DIR_LOCAL" \
                    --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE" \
                    --extra-vars "BROKER_DOCKER_COMPOSE_FILE=$brokerDockerComposeFile" \
                    --extra-vars "BROKER_DOCKER_COMPOSE_FILE_PLAIN_SECURE=$brokerDockerComposeFilePlainSecure" \
                    --extra-vars "SSL_CERT_FILE=$sslCertFile"
    code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

  done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
