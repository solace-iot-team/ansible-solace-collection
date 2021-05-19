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
  if [ -z "$SSL_CERT_FILE" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: SSL_CERT_FILE"; exit 1; fi
  if [ -z "$REQUESTS_CA_BUNDLE" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: REQUESTS_CA_BUNDLE"; exit 1; fi

##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"
  export RUN_TIME_DIR_LOCAL="$WORKING_DIR/run-time"; mkdir -p $RUN_TIME_DIR_LOCAL
  export RUN_TIME_DIR_REMOTE="/var/local"
  if [ -z "$CONFIG_DB_DIR" ]; then
    export CONFIG_DB_DIR="$WORKING_DIR/config_db";
    mkdir -p $CONFIG_DB_DIR
  fi
  if [ -z "$AZURE_BROKER_PROJECT_NAME" ]; then export AZURE_BROKER_PROJECT_NAME="asct-tr-broker"; fi
  # fix docker image to only one here. changing images sometimes fails to start broker properly with certs
  BROKER_DOCKER_IMAGE="solace/solace-pubsub-standard:latest"
  azureProjectName=$AZURE_BROKER_PROJECT_NAME
  brokerDockerComposeFile=$(assertFile $scriptLogName "$scriptDir/templates/PubSubStandard_singleNode.yml") || exit
  brokerDockerComposeFilePlainSecure=$(assertFile $scriptLogName "$scriptDir/templates/PubSubStandard_singleNode.plain+secure.yml") || exit
  remoteInventory=$(assertFile $scriptLogName "$CONFIG_DB_DIR/azure_vms/$azureProjectName/vm.inventory.json") || exit
  localInventory=$(assertFile $scriptLogName "$scriptDir/files/inventory.yml") || exit
  playbooks=(
    "$scriptDir/delete.single-node.service.playbook.yml"
    # "$scriptDir/create.single-node.plain+secure.playbook.yml"
    "$scriptDir/delete.single-node.service.playbook.yml"
    "$scriptDir/create.single-node.default.playbook.yml"
    "$scriptDir/delete.single-node.service.playbook.yml"
    "$scriptDir/create.single-node.docker-compose-file.playbook.yml"
    "$scriptDir/delete.single-node.service.playbook.yml"
    "$scriptDir/ex-1.playbook.yml"
  )
  sslCertFile="$scriptDir/files/secrets/asc.pem"

  # wipe docker clean
  # docker container stop $(docker container ls –aq)
  # docker system prune -af --volumes

##############################################################################################################################
# Run

  if [ -z "$NO_GENERATE_NEW_CERT" ]; then
    runScript="$scriptDir/files/secrets/generateSelfSignedCert.sh"
    $runScript
    code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

    runScript="$scriptDir/files/secrets/addCert2PythonCABundle.sh"
    $runScript
    code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi
  fi

  for playbook in ${playbooks[@]}; do

    playbook=$(assertFile $scriptLogName $playbook) || exit
    ansible-playbook \
                    -i $localInventory \
                    -i $remoteInventory \
                    $playbook \
                    --extra-vars "CONFIG_DB_DIR=$CONFIG_DB_DIR" \
                    --extra-vars "RUN_TIME_DIR_LOCAL=$RUN_TIME_DIR_LOCAL" \
                    --extra-vars "RUN_TIME_DIR_REMOTE=$RUN_TIME_DIR_REMOTE" \
                    --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE" \
                    --extra-vars "BROKER_DOCKER_COMPOSE_FILE=$brokerDockerComposeFile" \
                    --extra-vars "BROKER_DOCKER_COMPOSE_FILE_PLAIN_SECURE=$brokerDockerComposeFilePlainSecure" \
                    --extra-vars "SSL_CERT_FILE=$sslCertFile"
    code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

  done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
