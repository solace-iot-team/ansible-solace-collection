#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
testTarget=${scriptDir##*/}
scriptLogName="$testTargetGroup.$testTarget.$scriptName"
if [ -z "$PROJECT_HOME" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
source $PROJECT_HOME/.lib/functions.sh


############################################################################################################################
# Environment Variables

  if [ -z "$WORKING_DIR" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: WORKING_DIR"; exit 1; fi
  if [ -z "$LOG_DIR" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$CONFIG_DB_DIR" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: CONFIG_DB_DIR"; exit 1; fi
  if [ -z "$AZURE_BROKER_PROJECT_NAME" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: AZURE_BROKER_PROJECT_NAME"; exit 1; fi
  if [ -z "$AZURE_LOCATION" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: AZURE_LOCATION"; exit 1; fi
  if [ -z "$AZURE_VM_SEMP_PLAIN_PORT" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: AZURE_VM_SEMP_PLAIN_PORT"; exit 1; fi
  if [ -z "$AZURE_VM_SEMP_SECURE_PORT" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: AZURE_VM_SEMP_SECURE_PORT"; exit 1; fi
  if [ -z "$AZURE_VM_ADMIN_USER" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: AZURE_VM_ADMIN_USER"; exit 1; fi
  if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE" ]; then echo ">>> $scriptName:XT_ERROR: - $scriptName - missing env var: AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE"; exit 1; fi

# defaults
  if [ -z "$AZURE_VM_IMAGE_URN" ]; then export AZURE_VM_IMAGE_URN="Canonical:0001-com-ubuntu-server-focal:20_04-lts:latest"; fi

############################################################################################################################
# Prepare

  inventoryTemplateFile=$(assertFile $scriptLogName "$AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE") || exit
  azureProjectName=$AZURE_BROKER_PROJECT_NAME
  resourceGroupName="$azureProjectName-rg"
  azLocation="$AZURE_LOCATION"
  vmImageUrn="$AZURE_VM_IMAGE_URN"
  vmName="$azureProjectName-vm"
  vmAdminUsr="$AZURE_VM_ADMIN_USER"
  vmSempPlainPort="$AZURE_VM_SEMP_PLAIN_PORT"
  vmSempSecurePort="$AZURE_VM_SEMP_SECURE_PORT"

  outputDir="$CONFIG_DB_DIR/azure_vms/$azureProjectName"; mkdir -p $outputDir; rm -rf $outputDir/*;
  outputInfoFile="$outputDir/vm.info.json"
  outputInventoryFile="$outputDir/vm.inventory.json"

############################################################################################################################
# Run
echo " >>> $scriptName: Creating Resource Group $resourceGroupName ..."
  az group create \
    --name $resourceGroupName \
    --location "$azLocation" \
    --tags projectName=$azureProjectName \
    --verbose
  if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: creating resource group"; exit 1; fi
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Creating azure vm ..."
  az vm create \
    --resource-group $resourceGroupName \
    --name "$vmName" \
    --image "$vmImageUrn" \
    --admin-username $vmAdminUsr \
    --generate-ssh-keys \
    --public-ip-address-dns-name $vmName \
    --verbose \
    > $outputInfoFile
  if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: creating azure vm"; exit 1; fi
  cat $outputInfoFile | jq .
  ls -la ~/.ssh/id_rsa*
  # cat ~/.ssh/id_rsa; if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: vm private key"; exit 1; fi
  # cat ~/.ssh/id_rsa.pub; echo ""; if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: vm pub key"; exit 1; fi
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Opening plain semp port on azure vm ..."
  az vm open-port \
    --port $vmSempPlainPort \
    --priority 101 \
    --resource-group $resourceGroupName \
    --name "$vmName" \
    --verbose
  if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: opening semp plain port $vmSempPlainPort on azure vm"; exit 1; fi
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Opening secure semp port on azure vm ..."
  az vm open-port \
    --port $vmSempSecurePort \
    --priority 100 \
    --resource-group $resourceGroupName \
    --name "$vmName" \
    --verbose
  if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: opening semp secure port $vmSempSecurePort on azure vm"; exit 1; fi
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Test ssh to vm ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  tries=0; max=10; code=1;
  while [[ $tries -lt $max && $code -gt 0 ]]; do
    ((tries++))
    ssh_test=$(ssh "$vmAdminUsr@$vmPublicIpAddress" "bash --version")
    code=$?
    echo "tries=$tries, ssh_test=$ssh_test"
    if [[ $code != 0 ]]; then echo "code=$code && tries=$tries, sleep 1m"; sleep 1m; fi
  done
  if [[ $code != 0 || -z "$ssh_test" ]]; then echo " >>> $scriptName:XT_ERROR: ssh into vm"; exit 1; fi
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Calling Bootstrap vm ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  export vmPublicIpAddress
  export vmAdminUsr
  runScript="$scriptDir/../azure/bootstrap.Ubuntu-18.vm.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> $scriptName:XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Get python path ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  vmPythonPath=$(ssh "$vmAdminUsr@$vmPublicIpAddress" "which python3")
  if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: get python path"; exit 1; fi
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Adding info ..."
  vmInfo=$(cat $outputInfoFile | jq .)
  export vmAdminUsr
  export vmSempPlainPort
  export vmSempSecurePort
  export vmPythonPath
  vmInfo=$(echo $vmInfo | jq ".admin_user=env.vmAdminUsr")
  vmInfo=$(echo $vmInfo | jq ".semp_port_plain=env.vmSempPlainPort")
  vmInfo=$(echo $vmInfo | jq ".semp_port_secure=env.vmSempSecurePort")
  vmInfo=$(echo $vmInfo | jq ".python_path=env.vmPythonPath")
  echo $vmInfo | jq . > "$outputInfoFile"
  cat $outputInfoFile | jq .
echo " >>> $scriptName: Success."

echo " >>> $scriptName: Creating inventory file ..."
  yq --version
  inventory=$(cat $inventoryTemplateFile | yq e -j - )
  if [[ $? != 0 ]]; then echo " >>> $scriptName:XT_ERROR: get inventory with yq"; exit 1; fi
  export vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  export vmFQDNS=$(cat $outputInfoFile | jq -r '.fqdns')
  export vmAdminUsr
  export vmPythonPath
  export vmSempPlainPort
  export vmSempSecurePort
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.ansible_host=env.vmPublicIpAddress")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.ansible_user=env.vmAdminUsr")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.ansible_python_interpreter=env.vmPythonPath")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.solace_broker_service.semp_host=env.vmFQDNS")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.solace_broker_service.semp_port_plain=env.vmSempPlainPort")
  inventory=$(echo $inventory | jq ".all.hosts.remotehost.solace_broker_service.semp_port_secure=env.vmSempSecurePort")
  echo $inventory | jq . > "$outputInventoryFile"
  cat "$outputInventoryFile" | jq .
echo " >>> $scriptName: Success."

###
# The End.
