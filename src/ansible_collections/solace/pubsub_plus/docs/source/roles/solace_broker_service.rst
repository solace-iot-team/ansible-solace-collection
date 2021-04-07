
.. _solace_broker_service_role:

solace_broker_service - manage a broker service
===============================================

TODO: re-write


Manage a self-hosted Broker Service running in Docker.

.. note::
  The role only supports plain http SEMP.

  When using a remote VM:
    - ensure ansible has access to the public key for the VM
    - ensure the SEMP port on the VM is open


Prerequisites
-------------

- collection: `docker_compose`_

.. _docker_compose:
  https://docs.ansible.com/ansible/latest/collections/community/docker/docker_compose_module.html

Usage Examples
--------------

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

**Example Playbook to Create & Delete a Service:**

.. literalinclude:: ../../examples/roles/solace_broker_service/create-delete.playbook.yml
   :language: yaml


**Run the Playbook:**

This playbook will:
  - download the latest Solace PubSub+ standard edition image from docker hub
  - start the docker container
  - wait until the broker service is up and running, including a test if message spool is availabe
  - generate the inventory file for the new broker service in the ``./tmp`` directory
  - uses the default ``definition`` values for ``docker-compose``
  - delete the service again

.. code-block:: bash

  ansible-playbook \
                -i {inventory-file} \
                {playbook-file}

**Example Playbook with default settings and docker compose file:**

.. literalinclude:: ../../examples/roles/solace_broker_service/example-2.playbook.yml
   :language: yaml


Start Single Broker on Local Machine with Default Settings
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Use this example to start a broker service in a docker container on your local machine (the ansible controller).

**Inventory File:**

.. code-block:: yaml

  ---
  all:
    hosts:
      localhost:
        ansible_connection: local


Example Generated Broker Service Inventory Files
++++++++++++++++++++++++++++++++++++++++++++++++

The ``project_name`` variable is used as the host entry.

**Remote VM:**

.. code-block:: yaml

  all:
    hosts:
      broker_service_single_node:
        ansible_connection: local
        broker_type: local
        sempv2_host: {the vm public ip address }
        sempv2_is_secure_connection: 'False'
        sempv2_password: admin
        sempv2_port: '8080'
        sempv2_timeout: '60'
        sempv2_username: admin
        virtual_router: primary
        vpn: default


**Localhost:**

.. code-block:: yaml

  all:
    hosts:
      broker_service_single_node:
        ansible_connection: local
        broker_type: local
        sempv2_host: localhost
        sempv2_is_secure_connection: 'False'
        sempv2_password: admin
        sempv2_port: '8080'
        sempv2_timeout: '60'
        sempv2_username: admin
        virtual_router: primary
        vpn: default



List of select variables
------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - Variable
     - Examples/Options
     - Description

   * - service_type
     - options: [docker_single_node], default: docker_single_node
     - The type of service to manage.

   * - generated_inventory_file
     - ./tmp/inventory.yml
     - Filename (incl. path) of resulting inventory to create.

   * - state
     - options: [present, absent], default: present
     - Create or delete broker service & inventory file.

   * - project_name
     - my_project
     - Project name for community.general.docker_compose.

   * - container_name
     - default: pubSubStandardSingleNode
     - Container name.

   * - image
     - default: solace/solace-pubsub-standard:latest
     - Image for docker compose.


.. seealso::

  `docker_compose`_

Full list of variables & default values
---------------------------------------

.. literalinclude:: ../../../roles/solace_broker_service/defaults/main.yml
   :language: yaml
