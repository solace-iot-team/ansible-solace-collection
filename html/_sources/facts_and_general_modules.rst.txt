.. _facts_and_general_modules:


Fact & General Modules
======================

To gather facts about Brokers / Solace Cloud Services and Solace Cloud accounts specialized modules exist.

Example Usage
-------------

Call the module :ref:`solace_gather_facts_module` at the beginning of your playbook, so all broker facts are available for the rest of the playbook.

`solace_gather_facts` places the facts gathered in `ansible_facts.solace[inventory_hostname]` as a JSON.
You can save it to file, print it out and find where the fact you are interested in is located.
Using `jinja2`_, you can dynamically retrieve facts based on certain settings.

.. _jinja2:
  https://palletsprojects.com/p/jinja/

Here is a gotcha:

When using modules that require access to multiple brokers at the same time, for example :ref:`solace_bridge_remote_vpn_module`, we need to ensure that `solace_gather_facts` is executed for
each host in the inventory BEFORE the `solace_bridge_remote_vpn` is called.

The solution is to tell Ansible that by setting **forks 1** parameter for `ansible-playbook`:

.. code-block:: bash

    ansible-playbook \
            --forks 1 \
            -i inventory-with-two-brokers.yml \
            my.playbook.yml

This tells Ansible to execute each task for all hosts BEFORE moving onto the next task.

An additional convenience module allows you to retrieve certain facts from Ansible's `hostvars`: :ref:`solace_get_facts_module`.

It implements a few functions to directly collect a set of facts without the need to understand the JSON structure.
For example, to get the connection details of a newly created Solace Cloud service use the following in your playbook:

.. code-block:: yaml

  - name: "Gather Solace Facts"
    solace_gather_facts:

  - name: get_vpnClientConnectionDetails
    solace_get_facts:
      hostvars: "{{ hostvars }}" # always use this setting
      hostvars_inventory_hostname: "{{ inventory_hostname }}"
      msg_vpn: "{{ vpn }}"
      get_functions:
        - get_vpnClientConnectionDetails
    register: result

  - set_fact:
      client_connection_details: "{{ result.facts.vpnClientConnectionDetails }}"

  - name: "Save 'client_connection_details' to File"
    copy:
      content: "{{ client_connection_details | to_nice_json }}"
      dest: "./tmp/generated/{{ inventory_hostname }}.client_connection_details.json"



Module Reference
----------------

.. toctree::
   :glob:
   :maxdepth: 1

   modules/solace_gather_facts*
   modules/solace_get_facts*
   modules/solace_get_available*
   modules/solace_cloud_account_gather_facts*
   modules/solace_cloud_get_facts*
