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
  if [ -z "$AZURE_LOCATION" ]; then echo ">>> ERROR: - $scriptName - missing env var: AZURE_LOCATION"; exit 1; fi
  if [ -z "$AZURE_VM_IMAGE_URN" ]; then echo ">>> ERROR: - $scriptName - missing env var: AZURE_VM_IMAGE_URN"; exit 1; fi
  if [ -z "$AZURE_VM_SEMP_PORT" ]; then echo ">>> ERROR: - $scriptName - missing env var: AZURE_VM_SEMP_PORT"; exit 1; fi
  if [ -z "$AZURE_VM_ADMIN_USER" ]; then echo ">>> ERROR: - $scriptName - missing env var: AZURE_VM_ADMIN_USER"; exit 1; fi
  if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE" ]; then echo ">>> ERROR: - $scriptName - missing env var: AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE"; exit 1; fi
  if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY" ]; then echo ">>> ERROR: - $scriptName - missing env var: AZURE_VM_REMOTE_HOST_INVENTORY"; exit 1; fi

############################################################################################################################
# Run
inventoryTemplateFile=$(assertFile $scriptLogName "$AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE") || exit
resourceGroupName="$AZURE_PROJECT_NAME-rg"
azLocation="$AZURE_LOCATION"
vmImageUrn="$AZURE_VM_IMAGE_URN"
vmName="$AZURE_PROJECT_NAME-vm"
vmAdminUsr="$AZURE_VM_ADMIN_USER"
vmSempPort="$AZURE_VM_SEMP_PORT"

outputDir="$WORKING_DIR/azure"; mkdir -p $outputDir;
if [ -z "$CLEAN_WORKING_DIR" ]; then rm -rf $outputDir/*; fi
outputInfoFile="$outputDir/vm.info.json"
outputSecretsFile="$outputDir/vm.secrets.json"
outputInventoryFile="$AZURE_VM_REMOTE_HOST_INVENTORY"


echo " >>> Creating Resource Group ..."
  az group create \
    --name $resourceGroupName \
    --location "$azLocation" \
    --tags projectName=$AZURE_PROJECT_NAME \
    --verbose
  if [[ $? != 0 ]]; then echo " >>> ERROR: creating resource group"; exit 1; fi
echo " >>> Success."

echo " >>> Creating azure vm ..."
  az vm create \
    --resource-group $resourceGroupName \
    --name "$vmName" \
    --image "$vmImageUrn" \
    --admin-username $vmAdminUsr \
    --generate-ssh-keys \
    --verbose \
    > $outputInfoFile
  if [[ $? != 0 ]]; then echo " >>> ERROR: creating azure vm"; exit 1; fi
  cat $outputInfoFile | jq .
  ls -la ~/.ssh/id_rsa*
  cat ~/.ssh/id_rsa; if [[ $? != 0 ]]; then echo " >>> ERROR: vm private key"; exit 1; fi
  cat ~/.ssh/id_rsa.pub; if [[ $? != 0 ]]; then echo " >>> ERROR: vm pub key"; exit 1; fi
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  ssh_test=$(ssh "$vmAdminUsr@$vmPublicIpAddress" "bash --version")
  echo "ssh_test=$ssh_test"
  exit 1
echo " >>> Success."

echo " >>> Opening semp port on azure vm ..."
  az vm open-port \
    --port $vmSempPort \
    --resource-group $resourceGroupName \
    --name "$vmName" \
    --verbose
  if [[ $? != 0 ]]; then echo " >>> ERROR: opening semp port on azure vm"; exit 1; fi
echo " >>> Success."

echo " >>> Calling Bootstrap vm ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  export vmPublicIpAddress
  export vmAdminUsr
  runScript="$scriptDir/../azure/bootstrap.Ubuntu-18.vm.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi
echo " >>> Success."

echo " >>> Get python path ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  vmPythonPath=$(ssh "$vmAdminUsr@$vmPublicIpAddress" "which python3")
  if [[ $? != 0 ]]; then echo " >>> ERROR: get python path"; exit 1; fi
echo " >>> Success."

echo " >>> Adding info ..."
  vmInfo=$(cat $outputInfoFile | jq .)
  export vmAdminUsr
  export vmSempPort
  export vmPythonPath
  vmInfo=$(echo $vmInfo | jq ".admin_user=env.vmAdminUsr")
  vmInfo=$(echo $vmInfo | jq ".sempv2_port=env.vmSempPort")
  vmInfo=$(echo $vmInfo | jq ".python_path=env.vmPythonPath")
  echo $vmInfo | jq . > "$outputInfoFile"
  cat $outputInfoFile | jq .
echo " >>> Success."

echo " >>> Creating inventory file ..."
  inventory=$(cat $inventoryTemplateFile | yq .)
  export vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  export vmAdminUsr
  export vmPythonPath
  export vmSempPort
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.ansible_host=env.vmPublicIpAddress")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.ansible_user=env.vmAdminUsr")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.ansible_python_interpreter=env.vmPythonPath")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.semp_port=env.vmSempPort")
  echo $inventory | jq . > "$outputInventoryFile"
  cat "$outputInventoryFile" | jq .
echo " >>> Success."

###
# The End.
