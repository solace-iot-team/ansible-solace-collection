#!/usr/bin/env bash
# (c) 2020 Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
projectHome=${scriptDir%/ansible-solace-collection/*}
if [[ ! $projectHome =~ "ansible-solace-collection" ]]; then
  projectHome=$projectHome/ansible-solace-collection
fi
source $projectHome/.lib/functions.sh
export testTargetGroup=${scriptDir##*/}
scriptLogName="$testTargetGroup.$scriptName"

############################################################################################################################
# Environment Variables

  if [ -z "$LOG_DIR" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$RUN_FG" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: RUN_FG"; exit 1; fi

  if [ -z "$ANSIBLE_SOLACE_TESTS" ]; then
    export ANSIBLE_SOLACE_TESTS=(
      "setup"
      "solace_get_available"
      "teardown"
    )
  fi

##############################################################################################################################
# Prepare

export WORKING_DIR="$scriptDir/tmp"
mkdir -p $WORKING_DIR

##############################################################################################################################
# Run

  for ansibleSolaceTest in ${ANSIBLE_SOLACE_TESTS[@]}; do

      runScript="$scriptDir/$ansibleSolaceTest/_run.sh"

      echo ">>> TEST: $testTargetGroup/$ansibleSolaceTest"

      if [[ "$RUN_FG" == "false" ]]; then
        $runScript > $LOG_DIR/$testTargetGroup.$ansibleSolaceTest._run.sh.out 2>&1
      else
        $runScript
      fi
      code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

  done

###
# The End.
