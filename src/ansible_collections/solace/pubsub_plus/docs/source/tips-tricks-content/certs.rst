.. _tips-tricks-content-certs:

Working with Self-Signed Certificates
=====================================

For development it is sometimes useful to generate and use self-signed certificates and standup Broker Services that use TLS for SEMP calls.

Here is a set of examples of how to:

* generate a self-signed certificate for a number of domains of your chosing, including `localhost`
* add the certificate to the certificate authority bundle of your python installation
* add the certificate to your keychain if you are using a Mac


Generating the Certificate
--------------------------

Using the following example ssl config file, you can add as many domains as needed, including `localhost`:

.. literalinclude:: ../../examples/tips-tricks/certs/ssl.conf
   :language: bash

.. note::
  Only use 1 wildcard in your domain. For example `*.*.cloudapp.azure.com` will not work.

The following script:

* generates a private key in `asc.key`
* generates a certificate in `asc.crt`
* creates the PEM file combining the certificate & private key in `asc.pem`

.. literalinclude:: ../../examples/tips-tricks/certs/generateSelfSignedCert.sh
   :language: bash

Python does not use the machine's keychain or truststore but it's own Certificate Authority Bundle file.
The following script will:

* find the CA Bundle file your python3 installation uses - `python3 -m certifi`
* make a backup of it - `*.original`
* append the new certificate `asc.crt` to the bundle file

.. literalinclude:: ../../examples/tips-tricks/certs/addCert2PythonCABundle.sh
   :language: bash


Finally, if you are using a Mac, this script registers the new certificate with the keychain so you can access the Broker Service via your Browser using https:

.. literalinclude:: ../../examples/tips-tricks/certs/registerCert.mac.sh
   :language: bash


.. seealso::

  - :ref:`solace_broker_service_role` - for an example of using a certificate to secure a Broker Service
