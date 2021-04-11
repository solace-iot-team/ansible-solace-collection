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

# add python and ansible version to LOG_DIR
pythonVersion=$(python -c "from platform import python_version; print(python_version())")
firstLine=$(ansible --version | head -1)
ansibleVersion=${firstLine//" "/"_"}
export LOG_DIR="$LOG_DIR/python_$pythonVersion/$ansibleVersion"
mkdir -p $LOG_DIR


FAILED=0
# $scriptDir/_run.sh > $LOG_DIR/$scriptLogName.out 2>&1
$scriptDir/_run.integration.sh
code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - $scriptLogName"; FAILED=1; fi

##############################################################################################################################
# Check for warnings

# 2021-02-13 12:17:06,587 - WARNING - root - solace_api - log_http_roundtrip(): this is a warning
# shopt -s globstar
# filePattern="$LOG_DIR/**/*ansible-solace*.*"
filePattern="$LOG_DIR"
warnings=$(grep -n -r -e " - WARNING - " $filePattern )

if [[ -z "$warnings" ]]; then
  echo ">>> FINISHED:NO_WARNINGS - $scriptLogName"
  touch "$LOG_DIR/$scriptLogName.NO_WARNINGS.out"
else
  echo ">>> FINISHED:WITH_WARNINGS";
  if [ ! -z "$warnings" ]; then
    while IFS= read line; do
      echo $line >> "$LOG_DIR/$scriptLogName.WARNINGS.out"
    done < <(printf '%s\n' "$warnings")
  fi
fi

##############################################################################################################################
# Check for errors

filePattern="$LOG_DIR"
errors=$(grep -n -r -e "XT_ERROR" $filePattern )

if [[ -z "$errors" && "$FAILED" -eq 0 ]]; then
  echo ">>> FINISHED:SUCCESS - $scriptLogName"
  touch "$LOG_DIR/$scriptLogName.SUCCESS.out"
else
  echo ">>> FINISHED:FAILED";
  if [ ! -z "$errors" ]; then
    while IFS= read line; do
      echo $line >> "$LOG_DIR/$scriptLogName.XT_ERROR.out"
    done < <(printf '%s\n' "$errors")
  fi
  exit 1
fi


###
# The End.
