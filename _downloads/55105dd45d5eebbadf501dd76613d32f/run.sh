#!/usr/bin/env bash

scriptDir=$(cd $(dirname "$0") && pwd);

# set the working dir
  WORKING_DIR="$scriptDir/tmp"

# create broker service
  ansible-playbook -i $scriptDir/inventory.yml $scriptDir/service.playbook.yml --extra-vars "WORKING_DIR=$WORKING_DIR"

# configure broker service
  # enable logging
    export ANSIBLE_SOLACE_ENABLE_LOGGING=True
    export ANSIBLE_SOLACE_LOG_PATH="$WORKING_DIR/ansible-solace.log"
  ansible-playbook -i $WORKING_DIR/broker.inventory.yml $scriptDir/configure.playbook.yml
