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
  if [ -z "$CONFIG_DB_DIR" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: CONFIG_DB_DIR"; exit 1; fi
  if [ -z "$AZURE_BASTION_PROJECT_NAME" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_BASTION_PROJECT_NAME"; exit 1; fi

############################################################################################################################
# Prepare

  azureProjectName=$AZURE_BASTION_PROJECT_NAME
  resourceGroupName="$azureProjectName-rg"
  outputDir="$CONFIG_DB_DIR/azure_vms/$azureProjectName"

############################################################################################################################
# Run

echo " >>> Check resource group $resourceGroupName ..."
  resp=$(az group exists --name $resourceGroupName)
echo " >>> Success."

if [ "$resp" == "false" ]; then
  echo " >>> INFO: resoure group does not exist";
else
  echo " >>> Deleting resource group $resourceGroupName ..."
    az group delete \
        --name $resourceGroupName \
        --yes \
        --verbose
    if [[ $? != 0 ]]; then echo " >>> XT_ERROR: deleting resource group"; exit 1; fi
  echo " >>> Success."
fi

echo  " >>> Clean output dir $outputDir ..."
  rm -rf $outputDir
  if [[ $? != 0 ]]; then echo " >>> XT_ERROR: cleaning output dir"; exit 1; fi
echo " >>> Success."


###
# The End.
