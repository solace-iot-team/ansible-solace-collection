#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
if [ -z "$PROJECT_HOME" ]; then
  projectHome=${scriptDir%/ansible-solace-collection/*}
  if [[ ! $projectHome =~ "ansible-solace-collection" ]]; then
    projectHome=$projectHome/ansible-solace-collection
  fi
  export PROJECT_HOME=$projectHome
fi
source $PROJECT_HOME/.lib/functions.sh

############################################################################################################################
# Environment Variables

  if [ -z "$LOG_DIR" ]; then export LOG_DIR=$scriptDir/logs; fi
  if [ -z "$RUN_FG" ]; then export RUN_FG=false; fi

##############################################################################################################################
# Settings
scriptLogName=$scriptName
SOLACE_PUBSUB_PLUS_COLLECTION_PATH="$PROJECT_HOME/src/ansible_collections/solace/pubsub_plus"
# export ANSIBLE_DOC_FRAGMENT_PLUGINS="/Users/rjgu/Dropbox/Solace-Contents/Solace-IoT-Team/ansible-dev/ansible-solace-collection/src/ansible_collections/solace/pubsub_plus/plugins/doc_fragments"

############################################################################################################################
# Prepare

  mkdir -p $LOG_DIR
  rm -rf $LOG_DIR/*

##############################################################################################################################
# Run

  echo "##############################################################################################################"
  echo "# make docs"

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
