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


Playbook & Inventory
--------------------

Our playbook requires the local broker
:download:`inventory <../examples/quickstart/local.broker.inventory.yml>`:

.. literalinclude:: ../examples/quickstart/local.broker.inventory.yml
   :language: yaml

Now we can create a few simple Broker Objects using the following
:download:`playbook <../examples/quickstart/quickstart.playbook.yml>`:

.. literalinclude:: ../examples/quickstart/quickstart.playbook.yml
   :language: yaml

When we run the playbook, Ansible will download the latest Solace PubSub+
Standard Edition broker and start it on the local machine using Docker.
It will then configure two simple objects: a queue and attach a subscription
to the queue.

Run
---
Run the playbook::

  $ ansible-playbook -i local.broker.inventory.yml quickstart.playbook.yml

Open a new private window in your browser and log into the Broker's admin
console at http://localhost:8080 with credentials **admin/admin**.

Navigate to Queues to see the queue created.
