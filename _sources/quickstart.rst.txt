Quickstart for Solace PubSub+ Ansible Collection
================================================

Installation & Dependencies
---------------------------

Prerequisites:
  - install python >=3.6
  - install docker

Download the python dependencies:
:download:`requirements <../examples/requirements.txt>`:

.. literalinclude:: ../examples/requirements.txt

and the
:download:`quickstart.requirements <../examples/quickstart/quickstart.requirements.txt>`:

.. literalinclude:: ../examples/quickstart/quickstart.requirements.txt

Install:

.. code-block:: bash

  # upgrade to latest pip3
  $ python3 -m pip install --upgrade pip
  $ pip install -r requirements.txt
  $ pip install -r quickstart.requirements.txt
  $ pip install ansible

Install the Solace PubSub+ Ansible Collection::

  $ ansible-galaxy collection install solace.pubsub_plus


Playbooks
---------

We need to run two playbooks:
  - ``service.playbook.yml``: creates a local broker service running in docker and the broker inventory file
  - ``configure.playbook.yml``: configures the broker service we have just created

:download:`service.playbook.yml <../examples/quickstart/service.playbook.yml>`:

.. literalinclude:: ../examples/quickstart/service.playbook.yml
   :language: yaml

:download:`configure.playbook.yml <../examples/quickstart/configure.playbook.yml>`:

.. literalinclude:: ../examples/quickstart/configure.playbook.yml
   :language: yaml

We also need the initial
:download:`inventory.yml <../examples/quickstart/inventory.yml>`:

.. literalinclude:: ../examples/quickstart/inventory.yml
  :language: yaml

Run
---

When we run the first playbook, the role ``solace.pubsub_plus.broker_service``
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
