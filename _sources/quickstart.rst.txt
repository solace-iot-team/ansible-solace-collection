Quickstart for Solace PubSub+ Ansible Collection
================================================

Installation & Dependencies
---------------------------

.. literalinclude:: ../../meta/runtime.yml

Prerequisites:
  - install python >=3.8
  - install docker

Download the python dependencies:
:download:`requirements <../examples/requirements.txt>`:

.. literalinclude:: ../examples/requirements.txt

Install:

.. code-block:: bash

  # upgrade to latest pip3
  $ python3 -m pip install --upgrade pip
  $ pip install -r requirements.txt
  $ pip install ansible

.. note::
  Installing a specific version of ansible:

  .. code-block:: bash

    pip install "ansible>=2.10.3,<2.11", # for latest ansible_core 2.10
    pip install "ansible>=4.10.0,<5.0.0", # for latest ansible_core 2.11
    pip install "ansible>=5.1.0,<6.0.0" # for latest ansible core 2.12

Install the Solace PubSub+ Ansible Collection::

  $ ansible-galaxy collection install solace.pubsub_plus


Playbooks
---------

We need to run two playbooks:
  - ``service.playbook.yml``: creates a local broker service running in docker and generates the broker inventory file
  - ``configure.playbook.yml``: configures the broker service we have just created

:download:`service.playbook.yml <../examples/quickstart/service.playbook.yml>`:

.. literalinclude:: ../examples/quickstart/service.playbook.yml
   :language: yaml

:download:`configure.playbook.yml <../examples/quickstart/configure.playbook.yml>`:

.. literalinclude:: ../examples/quickstart/configure.playbook.yml
   :language: yaml

Run
---

When we run the first playbook, the role ``solace.pubsub_plus.solace_broker_service``
will download the latest Solace PubSub+ Standard Edition broker and start it on
the local machine using Docker.
It will also create the inventory file for newly created service in the ``$WORKING_DIR``.
The second playbook will then configure two simple objects: a queue and a subscription
to the queue.

Run the playbooks using
:download:`run.sh <../examples/quickstart/run.sh>`:

.. literalinclude:: ../examples/quickstart/run.sh
   :language: bash

Open a new private window in your browser and log into the Broker's admin
console at http://localhost:8080 with credentials **admin/admin**.

Navigate to Queues to see the queue created.

In the ``$WORKING_DIR`` you will find two files:
  - ``ansible-solace.log`` - the log file of all SEMP requests / responses to/from the broker service
  - ``broker.inventory.yml`` - the generated inventory for the created broker service

Using an Existing Broker / Service
----------------------------------

To use an existing standalone broker or Solace Cloud Service, you must provide the inventory file to the playbook `configure.playbook.yml`.

For a discussion on Ansible Solace Inventory Files, see :ref:`inventory_files`.
