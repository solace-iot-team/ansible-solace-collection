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
  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"
  if [ -z "$CONFIG_DB_DIR" ]; then export CONFIG_DB_DIR="$WORKING_DIR/config_db"; fi

##############################################################################################################################
# Run

  runScript="$scriptDir/../azure/bastion-vm/delete.az.vm.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

###
# The End.
