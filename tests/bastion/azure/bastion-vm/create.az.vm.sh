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

  if [ -z "$WORKING_DIR" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: WORKING_DIR"; exit 1; fi
  if [ -z "$LOG_DIR" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$CONFIG_DB_DIR" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: CONFIG_DB_DIR"; exit 1; fi

  if [ -z "$AZURE_BASTION_PROJECT_NAME" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_BASTION_PROJECT_NAME"; exit 1; fi
  if [ -z "$AZURE_LOCATION" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_LOCATION"; exit 1; fi
  if [ -z "$AZURE_VM_IMAGE_URN" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_VM_IMAGE_URN"; exit 1; fi
  # if [ -z "$AZURE_VM_SEMP_PLAIN_PORT" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_VM_SEMP_PLAIN_PORT"; exit 1; fi
  # if [ -z "$AZURE_VM_SEMP_SECURE_PORT" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_VM_SEMP_SECURE_PORT"; exit 1; fi
  # if [ -z "$AZURE_VM_ADMIN_USER" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_VM_ADMIN_USER"; exit 1; fi
  # if [ -z "$AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: AZURE_VM_REMOTE_HOST_INVENTORY_TEMPLATE"; exit 1; fi
  if [ -z "$SSH_PUBLIC_KEY_FILE" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: SSH_PUBLIC_KEY_FILE"; exit 1; fi
  if [ -z "$SSH_PRIVATE_KEY_FILE" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: SSH_PRIVATE_KEY_FILE"; exit 1; fi

############################################################################################################################
# Prepare
  azureProjectName=$AZURE_BASTION_PROJECT_NAME
  inventoryTemplateFile=$(assertFile $scriptLogName "$scriptDir/files/template.inventory.yml") || exit
  resourceGroupName="$azureProjectName-rg"
  azLocation="$AZURE_LOCATION"
  vmImageUrn="$AZURE_VM_IMAGE_URN"
  vmName="$azureProjectName-vm"
  # vmAdminUsr="$AZURE_VM_ADMIN_USER"
  # if [ -z "$AZURE_VM_ADMIN_USER" ]; then export AZURE_VM_ADMIN_USER="asct-admin"; fi
  vmAdminUsr="$azureProjectName"
  vmPrivateKeyFile="$SSH_PRIVATE_KEY_FILE"
  vmPublicKeyFile="$SSH_PUBLIC_KEY_FILE"

  # vmSempPlainPort="$AZURE_VM_SEMP_PLAIN_PORT"
  # vmSempSecurePort="$AZURE_VM_SEMP_SECURE_PORT"

  outputDir="$CONFIG_DB_DIR/azure_vms/$azureProjectName"; mkdir -p $outputDir;
  outputInfoFile="$outputDir/vm.info.json"
  outputInventoryFile="$outputDir/vm.inventory.json"

############################################################################################################################
# Run
echo " >>> Creating Resource Group ..."
  az group create \
    --name $resourceGroupName \
    --location "$azLocation" \
    --tags projectName=$azureProjectName \
    --verbose
  if [[ $? != 0 ]]; then echo " >>> XT_ERROR: creating resource group"; exit 1; fi
echo " >>> Success."

echo " >>> Creating azure vm ..."
  az vm create \
    --resource-group $resourceGroupName \
    --name "$vmName" \
    --image "$vmImageUrn" \
    --authentication-type ssh \
    --nsg-rule SSH \
    --admin-username $vmAdminUsr \
    --ssh-key-values $vmPublicKeyFile \
    --public-ip-address-dns-name $vmName \
    --verbose \
    > $outputInfoFile
  if [[ $? != 0 ]]; then echo " >>> XT_ERROR: creating azure vm"; exit 1; fi
  # cat $outputInfoFile | jq .
echo " >>> Success."

echo " >>> Test ssh to vm ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  tries=0; max=10; code=1;
  while [[ $tries -lt $max && $code -gt 0 ]]; do
    ((tries++))
    ssh_test=$(ssh -i $vmPrivateKeyFile "$vmAdminUsr@$vmPublicIpAddress" "bash --version")
    code=$?
    echo "tries=$tries, ssh_test=$ssh_test"
    if [[ $code != 0 ]]; then echo "code=$code && tries=$tries, sleep 1m"; sleep 1m; fi
  done
  if [[ $code != 0 || -z "$ssh_test" ]]; then echo " >>> XT_ERROR: ssh into vm"; exit 1; fi
echo " >>> Success."

echo " >>> Calling Bootstrap vm ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  export vmPublicIpAddress
  export vmAdminUsr
  export vmPrivateKeyFile
  runScript="$scriptDir/bootstrap.Ubuntu-18.vm.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi
echo " >>> Success."

echo " >>> Get python path ..."
  vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  vmPythonPath=$(ssh -i $vmPrivateKeyFile "$vmAdminUsr@$vmPublicIpAddress" "which python3")
  if [[ $? != 0 ]]; then echo " >>> XT_ERROR: get python path"; exit 1; fi
echo " >>> Success."

echo " >>> Vm info ..."
  vmInfo=$(cat $outputInfoFile | jq .)
  export vmAdminUsr
  # export vmSempPlainPort
  # export vmSempSecurePort
  export vmPythonPath
  vmInfo=$(echo $vmInfo | jq ".adminUser=env.vmAdminUsr")
  # vmInfo=$(echo $vmInfo | jq ".semp_port_plain=env.vmSempPlainPort")
  # vmInfo=$(echo $vmInfo | jq ".semp_port_secure=env.vmSempSecurePort")
  vmInfo=$(echo $vmInfo | jq ".python_path=env.vmPythonPath")
  echo $vmInfo | jq . > "$outputInfoFile"
  cat $outputInfoFile | jq .
echo " >>> Success."

echo " >>> Creating ansible inventory file ..."
  inventory=$(cat $inventoryTemplateFile | yq .)
  export vmPublicIpAddress=$(cat $outputInfoFile | jq -r '.publicIpAddress')
  # export vmFQDNS=$(cat $outputInfoFile | jq -r '.fqdns')
  export vmAdminUsr
  export vmPythonPath
  # export vmSempPlainPort
  # export vmSempSecurePort
  inventory=$(echo $inventory | jq ".all.hosts.bastionhost.ansible_host=env.vmPublicIpAddress")
  inventory=$(echo $inventory | jq ".all.hosts.bastionhost.ansible_user=env.vmAdminUsr")
  inventory=$(echo $inventory | jq ".all.hosts.bastionhost.ansible_python_interpreter=env.vmPythonPath")
  # inventory=$(echo $inventory | jq ".all.hosts.remotehost.solace_broker_service.semp_host=env.vmFQDNS")
  # inventory=$(echo $inventory | jq ".all.hosts.remotehost.solace_broker_service.semp_port_plain=env.vmSempPlainPort")
  # inventory=$(echo $inventory | jq ".all.hosts.remotehost.solace_broker_service.semp_port_secure=env.vmSempSecurePort")
  echo $inventory | jq . > "$outputInventoryFile"
  cat "$outputInventoryFile" | jq .
echo " >>> Success."

###
# The End.
