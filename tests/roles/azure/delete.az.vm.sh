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

  if [ -z "$WORKING_DIR" ]; then export WORKING_DIR="$PROJECT_HOME/tmp"; mkdir -p $WORKING_DIR; fi
  if [ -z "$LOG_DIR" ]; then export LOG_DIR="$WORKING_DIR/logs"; mkdir -p $LOG_DIR; fi

  if [ -z "$AZURE_PROJECT_NAME" ]; then echo ">>> ERROR: - $scriptName - missing env var: AZURE_PROJECT_NAME"; exit 1; fi

############################################################################################################################
# Run

resourceGroupName="$AZURE_PROJECT_NAME-rg"

echo " >>> Check Resource Group ..."
  resp=$(az group exists --name $resourceGroupName)
echo " >>> Success."

if [ "$resp" == "false" ]; then
  echo " >>> INFO: resoure group does not exist";
else
  echo " >>> Deleting Resource Group ..."
    az group delete \
        --name $resourceGroupName \
        --yes \
        --verbose
    if [[ $? != 0 ]]; then echo " >>> ERROR: deleting resource group"; exit 1; fi
  echo " >>> Success."
fi

echo  " >>> Clean working dir ..."
  rm -f $WORKING_DIR/azure/*.*
  if [[ $? != 0 ]]; then echo " >>> ERROR: cleaning working dir"; exit 1; fi
echo " >>> Success."


###
# The End.
