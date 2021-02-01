
.. _solace_broker_service_role:

solace_broker_service - manage a broker service
===============================================

Manage a Broker Service running in Docker.

Prerequisites
-------------

- collections: community.general
  - docker_compose


Example playbooks
-----------------

This playbook will:
  - download the latest Solace PubSub+ standard edition image from docker hub
  - start the docker container
  - wait until the broker service is up and running
  - create the inventory file in the ``.tmp`` directory
  - uses the default ```definition`` values for ``docker-compose``

.. literalinclude:: ../../examples/roles/broker_service.playbook.yml
   :language: yaml

This playbook uses a docker-compose file to start the service:

.. literalinclude:: ../../examples/roles/broker_service2.playbook.yml
   :language: yaml

**List of select variables:**

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

  `community.general.docker_compose <https://docs.ansible.com/ansible/latest/collections/community/general/docker_compose_module.html>`_

Full list of variables & default values
---------------------------------------

.. literalinclude:: ../../../roles/solace_broker_service/defaults/main.yml
   :language: yaml
