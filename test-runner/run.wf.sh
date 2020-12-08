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
testRunner="test-runner"
scriptLogName="$testRunner.$scriptName"

if [ -z "$LOG_DIR" ]; then
  export LOG_DIR=$scriptDir/logs
fi
mkdir -p $LOG_DIR
rm -rf $LOG_DIR/*

export ANSIBLE_DEBUG=False
export ANSIBLE_VERBOSITY=3
export ANSIBLE_SOLACE_ENABLE_LOGGING=True

FAILED=0
# $scriptDir/_run.sh > $LOG_DIR/$scriptLogName.out 2>&1
$scriptDir/_run.sh
code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - $scriptLogName"; FAILED=1; fi

##############################################################################################################################
# Check for errors

filePattern="$LOG_DIR"
errors=$(grep -n -r -e "ERROR" $filePattern )

if [[ -z "$errors" && "$FAILED" -eq 0 ]]; then
  echo ">>> FINISHED:SUCCESS - $scriptLogName"
  touch "$LOG_DIR/$scriptLogName.SUCCESS.out"
else
  echo ">>> FINISHED:FAILED";
  if [ ! -z "$errors" ]; then
    while IFS= read line; do
      echo $line >> "$LOG_DIR/$scriptLogName.ERROR.out"
    done < <(printf '%s\n' "$errors")
  fi
  exit 1
fi

###
# The End.
