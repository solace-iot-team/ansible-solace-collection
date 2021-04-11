#!/usr/bin/env bash
scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));

##############################################################################################################################
# Prepare

  certFile="$scriptDir/asc.crt"

##############################################################################################################################
# Run

echo ">>> Add new cert to python CA bundle ..."
  CA_CERT_BUNDLE_FILE=$(python3 -m certifi)
  originalCACertBundleFile="$CA_CERT_BUNDLE_FILE.original"
  if [ ! -f "$originalCACertBundleFile" ]; then
    cp "$CA_CERT_BUNDLE_FILE" "$originalCACertBundleFile"
    code=$?; if [[ $code != 0 ]]; then echo " >>> XT_ERROR: updating $CA_CERT_BUNDLE_FILE - $scriptName"; exit 1; fi
  fi
  # copy original and add to it
  cp "$originalCACertBundleFile" "$CA_CERT_BUNDLE_FILE"
  code=$?; if [[ $code != 0 ]]; then echo " >>> XT_ERROR: updating $CA_CERT_BUNDLE_FILE - $scriptName"; exit 1; fi
  cat "$certFile" >> "$CA_CERT_BUNDLE_FILE"
  code=$?; if [[ $code != 0 ]]; then echo " >>> XT_ERROR: updating $CA_CERT_BUNDLE_FILE - $scriptName"; exit 1; fi
echo ">>> Success."
