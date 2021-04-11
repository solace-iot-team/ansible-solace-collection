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
    -x509 -days 3650 -out "$certFile.x" \
    -extensions req_ext \
    -config "$sslConfFile" \
    -subj "$subject"
  code=$?
  if [[ $code != 0 ]]; then echo " >>> XT_ERROR: generating certificate - $scriptName"; exit 1; fi

  echo "# Subject: $subject" > "$certFile"
  cat "$certFile.x" >> "$certFile"
  echo "# Subject: $subject" > "$pemFile"
  cat "$certFile.x" >> "$pemFile"
  cat "$privateKeyFile" >> "$pemFile"
  rm -f "$certFile.x"
  echo "    >>> generated pem file:"
  cat "$pemFile"
echo ">>> Success."
