#!/usr/bin/env bash
scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));


##############################################################################################################################
# Prepare

  privateKeyFile="$scriptDir/asc.key"
  certFile="$scriptDir/asc.crt"
  pemFile="$scriptDir/asc.pem"
  sslConfFile="$scriptDir/ssl.conf"

  subjectC="UK"
  subjectST="London"
  subjectL="London"
  subjectO="Solace Corporation"
  subjectCN="ansible-solace-collection"

##############################################################################################################################
# Run

echo ">>> Generating self-signed certificate ..."

  subject="/C=$subjectC/ST=$subjectST/L=$subjectL/O=$subjectO/CN=$subjectCN"

  openssl req \
    -newkey rsa:2048 -nodes -keyout "$privateKeyFile" \
    -x509 -days 3650 -out "$certFile" \
    -extensions req_ext \
    -config "$sslConfFile" \
    -subj "$subject"
  if [[ $? != 0 ]]; then echo " >>> ERROR: generating certificate"; exit 1; fi

  echo "# Subject: $subject" > $pemFile
  cat $certFile >> $pemFile
  cat $privateKeyFile >> $pemFile
  echo "    >>> generated pem file:"
  cat $pemFile
echo ">>> Success."

echo ">>> Add new cert to python CA bundle ..."
  CA_CERT_BUNDLE_FILE=$(python3 -m certifi)
  originalCACertBundleFile="$CA_CERT_BUNDLE_FILE.original"
  if [ ! -f "$originalCACertBundleFile" ]; then
    cp $CA_CERT_BUNDLE_FILE $originalCACertBundleFile
    if [[ $? != 0 ]]; then echo " >>> ERROR: updating $CA_CERT_BUNDLE_FILE"; exit 1; fi
  fi
  # copy original and add to it
  cp $originalCACertBundleFile $CA_CERT_BUNDLE_FILE
  echo "# Subject: $subject" >> $CA_CERT_BUNDLE_FILE
  if [[ $? != 0 ]]; then echo " >>> ERROR: updating $CA_CERT_BUNDLE_FILE"; exit 1; fi
  cat $certFile >> $CA_CERT_BUNDLE_FILE
  if [[ $? != 0 ]]; then echo " >>> ERROR: updating $CA_CERT_BUNDLE_FILE"; exit 1; fi
  cat $CA_CERT_BUNDLE_FILE

echo ">>> Success."
