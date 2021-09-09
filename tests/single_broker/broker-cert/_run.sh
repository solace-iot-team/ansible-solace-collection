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

  if [ -z "$BROKER_TYPE" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: BROKER_TYPE"; exit 1; fi
  if [[ "$BROKER_TYPE" == "local" ]]; then
    if [ -z "$BROKER_DOCKER_IMAGE" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: BROKER_DOCKER_IMAGE"; exit 1; fi
  else echo ">>> SUCCESS: $scriptLogName - skipping BROKER_TYPE=$BROKER_TYPE"; exit 0; fi


##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

  brokerDockerComposeFile=$(assertFile $scriptLogName "$scriptDir/files/PubSubStandard_singleNode.plain+secure.yml") || exit
  brokerInventoryFile=$(assertFile $scriptLogName "$scriptDir/files/inventory.yml") || exit
  brokerMountPathSecretsDir="$scriptDir/files/secrets"
  brokerCertFile=$(assertFile $scriptLogName "$brokerMountPathSecretsDir/dummy.pem") || exit
  inventory=$(assertFile $scriptLogName "$scriptDir/files/inventory.yml") || exit

# ##############################################################################################################################
# # Setup
#
#   playbook=$(assertFile $scriptLogName "$scriptDir/main.playbook.yml") || exit
#   ansible-playbook \
#                   -i $inventory \
#                   $playbook \
#                   --extra-vars "BROKER_INVENTORY_FILE=$brokerInventoryFile" \
#                   --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE" \
#                   --extra-vars "BROKER_DOCKER_COMPOSE_FILE=$brokerDockerComposeFile" \
#                   --extra-vars "HOST_MOUNT_PATH_SECRETS_DIR=$brokerMountPathSecretsDir" \
#                   --extra-vars "CERT_FILE=$brokerCertFile"
#
#   code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi
#
#
#
#
# echo ">>> XT_ERROR - $code - script:$scriptLogName, continue here"; exit 1;
#
#

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
                    --extra-vars "BROKER_INVENTORY_FILE=$brokerInventoryFile" \
                    --extra-vars "BROKER_DOCKER_IMAGE=$BROKER_DOCKER_IMAGE" \
                    --extra-vars "BROKER_DOCKER_COMPOSE_FILE=$brokerDockerComposeFile" \
                    --extra-vars "HOST_MOUNT_PATH_SECRETS_DIR=$brokerMountPathSecretsDir" \
                    --extra-vars "CERT_FILE=$brokerCertFile"

  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, playbook:$playbook"; exit 1; fi

done

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
