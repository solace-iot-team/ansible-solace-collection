#!/usr/bin/env bash
scriptDir=$(cd $(dirname "$0") && pwd);

##############################################################################################################################
# Prepare

  certFile="$scriptDir/asc.crt"
  subjectCN="ansible-solace-collection"

##############################################################################################################################
# Run

echo ">>> Register self-signed certificate mac ..."

  sudo security delete-certificate -c "$subjectCN"
  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$certFile"
  sudo security find-certificate -c "$subjectCN"

echo ">>> Success."
