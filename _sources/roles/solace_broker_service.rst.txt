
.. _solace_broker_service_role:

solace_broker_service - manage a broker service
===============================================

Manage a self-hosted Broker Service running in Docker.

This role is a wrapper around `community.general.docker_compose`_.
It also uses :ref:`solace_get_available_module` for state=present to ensure the broker service has initialized properly.

.. note::
  The role only supports a single node (not H/A).

  When using a remote VM:
    - ensure ansible has access to the public key for the VM
    - ensure the SEMP http/https ports on the VM are open


Prerequisites
-------------

- collection: `community.general.docker_compose`_

.. _community.general.docker_compose:
  https://docs.ansible.com/ansible/latest/collections/community/docker/docker_compose_module.html

Examples
--------

Start Single Broker on Remote Ubuntu-18 VM
++++++++++++++++++++++++++++++++++++++++++

**Example ansible controller ssh config:**

Switch off host key checking:

.. code-block:: bash

  mkdir -p ~/.ssh
  echo "Host *" > ~/.ssh/config
  echo " StrictHostKeyChecking no" >> ~/.ssh/config


**Example Bootstrap for Ubuntu-18:**

.. literalinclude:: ../../examples/roles/solace_broker_service/remotevm/bootstrap.Ubuntu-18.vm.sh
   :language: bash

**Example Template Inventory File for Remote VM:**

.. literalinclude:: ../../examples/roles/solace_broker_service/remotevm/template.remotehost.inventory.yml
   :language: yaml

**Example Inventory File for Local Machine (the Ansible controller):**

.. code-block:: yaml

  ---
  all:
   hosts:
     localhost:
       ansible_connection: local


**Example Playbook to Create & Delete a Service using the default settings:**

.. literalinclude:: ../../examples/roles/solace_broker_service/example-1.playbook.yml
   :language: yaml


**Run the Playbook:**

This playbook will:
  - download the latest Solace PubSub+ standard edition image from docker hub
  - start the docker container
  - wait until the broker service is up and running, including a test if message spool is availabe
  - uses the default ``definition`` values for ``docker-compose``
  - outputs

    - the entire role results
    - the inventory of the broker service created
    - the settings used for `community.general.docker_compose`_
    - the docker logs

  - delete the service again

    - using the same project name
    - using the same docker compose definition

.. code-block:: bash

  ansible-playbook \
                -i {inventory-file} \
                {playbook-file}

**Example Playbook with default settings and docker compose file:**

.. literalinclude:: ../../examples/roles/solace_broker_service/example-2.playbook.yml
   :language: yaml

**Example Playbook with default settings and inline definition for docker compose:**

.. literalinclude:: ../../examples/roles/solace_broker_service/example-3.playbook.yml
  :language: yaml

**Example docker compose definition for secure SEMP:**

.. literalinclude:: ../../examples/roles/solace_broker_service/example-4.playbook.yml
  :language: yaml

Check the certificate of the broker service:

.. code-block:: bash

  openssl s_client -showcerts -servername {fqdns} -connect {fqdns}:1943


Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - Variable
     - Examples/Options
     - Description

   * - generate
     - inventory_settings
     - Combined with ``default_generate``, allowing to override only required values

   * - generate.inventory_settings
     - inventory_hostname, sempv2_host, sempv2_port, sempv2_username, sempv2_password, sempv2_is_secure_connection, vpn, virtual_router
     - The settings used to generate the broker service inventory

   * - docker_compose_settings
     - all settings provided by `community.general.docker_compose`_
     - Combined with ``default_docker_compose_settings``, allowing to override only required values

Defaults
--------

.. literalinclude:: ../../../roles/solace_broker_service/defaults/main.yml
   :language: yaml

Return Values
-------------

.. list-table::
   :header-rows: 1
   :widths: 25 45

   * - Variable
     - Description

   * - solace_broker_service_result
     - Result dict

   * - solace_broker_service_result.inventory
     - The combined inventory for the broker service

   * - solace_broker_service_result.docker_compose_settings
     - The combined ``docker_compose_settings``

   * - solace_broker_service_result.docker_logs
     - The docker logs from the created services. Only applies to ``state=present``


Example Generated Broker Service Inventory Files
++++++++++++++++++++++++++++++++++++++++++++++++

The ``ansible_hostname`` variable is used as the host entry.

``solace_broker_service_result.inventory``

**Remote VM:**

.. code-block:: yaml

  all:
    hosts:
      {ansible_hostname}:
        ansible_connection: local
        broker_type: local
        sempv2_host: {FQDNS}
        sempv2_is_secure_connection: 'True'
        sempv2_password: admin
        sempv2_port: '1943'
        sempv2_timeout: '60'
        sempv2_username: admin
        virtual_router: primary
        vpn: default


**Localhost:**

.. code-block:: yaml

  all:
    hosts:
      {ansible_hostname}:
        ansible_connection: local
        broker_type: local
        sempv2_host: localhost
        sempv2_is_secure_connection: 'True'
        sempv2_password: admin
        sempv2_port: '1943'
        sempv2_timeout: '60'
        sempv2_username: admin
        virtual_router: primary
        vpn: default

Example Output Docker Compose Settings
++++++++++++++++++++++++++++++++++++++

``solace_broker_service_result.docker_compose_settings``

.. code-block:: yaml

  definition:
    services:
      primary:
        container_name: pubSubStandardSingleNode
        deploy:
          restart_policy:
            condition: on-failure
            max_attempts: 3
        environment:
        - username_admin_globalaccesslevel=admin
        - username_admin_password=admin
        - system_scaling_maxconnectioncount=100
        - tls_servercertificate_filepath=/run/secrets/asc.pem
        image: solace/solace-pubsub-standard:latest
        ports:
        - 1943:1943
        - 8080:8080
        restart: unless-stopped
        shm_size: 1g
        ulimits:
          core: 2
          nofile:
            hard: 38048
            soft: 2448
        user: '4000'
        volumes:
        - /var/local/broker_services/asc-test_roles_broker_service_single_node/secrets:/run/secrets
        - /var/local/broker_services/asc-test_roles_broker_service_single_node/data/spool/softAdb:/usr/sw/internalSpool/softAdb:Z
        - /var/local/broker_services/asc-test_roles_broker_service_single_node/data/spool:/usr/sw/internalSpool:Z
        - /var/local/broker_services/asc-test_roles_broker_service_single_node/data/jail:/usr/sw/jail:Z
        - /var/local/broker_services/asc-test_roles_broker_service_single_node/data/diagnostics:/var/lib/solace/diags:Z
        - /var/local/broker_services/asc-test_roles_broker_service_single_node/data/adbBackup:/usr/sw/adb:Z
        - /var/local/broker_services/asc-test_roles_broker_service_single_node/data/var:/usr/sw/var:Z
    version: '3.3'
  project_name: asc-test_roles_broker_service_single_node
  services:
  - primary


.. seealso::

  - `community.general.docker_compose`_
  - :ref:`solace_get_available_module`
