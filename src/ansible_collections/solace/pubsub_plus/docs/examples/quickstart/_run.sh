#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
testTarget=${scriptDir##*/}
if [ -z "$testTargetGroup" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: testTargetGroup"; exit 1; fi
scriptLogName="$testTargetGroup.$testTarget.$scriptName"
if [ -z "$PROJECT_HOME" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
source "$PROJECT_HOME/.lib/functions.sh"

############################################################################################################################
# Environment Variables

  if [ -z "$LOG_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$WORKING_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: WORKING_DIR"; exit 1; fi
  if [ -z "$RUN_FG" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: RUN_FG"; exit 1; fi

##############################################################################################################################
# Prepare

  export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible-solace.log"
  export ANSIBLE_LOG_PATH="$LOG_DIR/$scriptLogName.ansible.log"

##############################################################################################################################
# Settings

runScript="$scriptDir/run.sh"
$runScript
code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - script:$scriptLogName, script:$runScript"; exit 1; fi

echo ">>> SUCCESS: $scriptLogName"

###
# The End.
