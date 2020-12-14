#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
projectHome=${scriptDir%/ansible-solace-collection/*}
if [[ ! $projectHome =~ "ansible-solace-collection" ]]; then
  projectHome=$projectHome/ansible-solace-collection
fi
export PROJECT_HOME=$projectHome


ansibleSolaceTests=(
  "make"
)
export ANSIBLE_SOLACE_TESTS="${ansibleSolaceTests[*]}"

export LOG_DIR=$scriptDir/logs
mkdir -p $LOG_DIR
rm -rf $LOG_DIR/*

export RUN_FG=true
# export RUN_FG=false

export SOLACE_PUBSUB_PLUS_COLLECTION_PATH="$PROJECT_HOME/src/ansible_collections/solace/pubsub_plus"

../_run.sh

###
# The End.
