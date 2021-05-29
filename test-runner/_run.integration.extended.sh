#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
testRunner="test-runner"
scriptLogName="$testRunner.$scriptName"
if [ -z "$PROJECT_HOME" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
source $PROJECT_HOME/.lib/functions.sh

############################################################################################################################
# Environment Variables

  if [ -z "$REVERSE_PROXY_HOST" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: REVERSE_PROXY_HOST"; exit 1; fi
  if [ -z "$REVERSE_PROXY_API_KEY" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: REVERSE_PROXY_API_KEY"; exit 1; fi
  if [ -z "$REVERSE_PROXY_SEMP_BASE_PATH" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: REVERSE_PROXY_SEMP_BASE_PATH"; exit 1; fi
  if [ -z "$LOG_DIR" ]; then echo ">>> XT_ERROR: - $scriptName - missing env var: LOG_DIR"; exit 1; fi

##############################################################################################################################
# Settings
  export RUN_FG=false

  baseLogDir=$LOG_DIR
  testsBaseDir="$PROJECT_HOME/tests"

#################################################################################################################################################
ansibleSolaceTestTargetGroup="reverse_proxy"
#################################################################################################################################################

  export LOG_DIR="$baseLogDir/$ansibleSolaceTestTargetGroup"
  mkdir -p $LOG_DIR
  echo "##############################################################################################################"
  echo "# Test target group: $ansibleSolaceTestTargetGroup"

  runScript="$testsBaseDir/$ansibleSolaceTestTargetGroup/_run.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi


###
# The End.
