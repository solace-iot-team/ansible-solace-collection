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

  if [ -z "$LOG_DIR" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$WORKING_DIR" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: WORKING_DIR"; exit 1; fi
  if [ -z "$RUN_FG" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: RUN_FG"; exit 1; fi
  if [ -z "$SOLACE_PUBSUB_PLUS_COLLECTION_PATH" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: SOLACE_PUBSUB_PLUS_COLLECTION_PATH"; exit 1; fi

##############################################################################################################################
# Run

  runScriptDir="$SOLACE_PUBSUB_PLUS_COLLECTION_PATH/docs"
  runScript="./make.sh"
  logFile="$LOG_DIR/$scriptLogName.details.out"

  cd $runScriptDir

  if [[ "$RUN_FG" == "false" ]]; then
    $runScript > $logFile 2>&1
  else
    $runScript 2>&1 | tee $logFile
  fi

  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code - script:$scriptLogName"; exit 1; fi
  cd $scriptDir


##############################################################################################################################
# Check for warnings

filePattern="$logFile"
errors=$(grep -n -r -e "WARNING" $filePattern )

if [[ -z "$errors" && "$FAILED" -eq 0 ]]; then
  echo ">>> SUCCESS - $scriptLogName"
else
  echo ">>> ERROR - script:$scriptLogName";
  if [ ! -z "$errors" ]; then
    while IFS= read line; do
      echo $line
    done < <(printf '%s\n' "$errors")
  fi
  exit 1
fi

###
# The End.
