Concepts of Solace PubSub+ Ansible Collection
=============================================


Facts for Solace Brokers
------------------------

In order to still be able to gather facts about the Broker / Service, the module

  `solace_gather_facts`

exists.

Call it at the beginning of your playbook, so all broker facts are available for the rest of the playbook.

`solace_gather_facts` places the facts gathered in `ansible_facts.solace[inventory_hostname]` as a JSON.
You can save it to file, print it out and find where the fact you are interested in is located.
Using `jinja2`_, you can dynamically retrieve facts based on certain settings.

.. _jinja2:
  https://palletsprojects.com/p/jinja/

Here is a gotcha:

When using modules that require acces to multiple brokers at the same time, for example `solace_bridge_remote_vpn`, we need to ensure that `solace_gather_facts` is executed for
each host in the inventory BEFORE the `solace_bridge_remote_vpn` is called.
The solution is to tell Ansible that by setting **forks 1** parameter for `ansible-playbook`:

.. code-block:: bash

    ansible-playbook \
            --forks 1 \
            -i inventory-with-two-brokers.yml \
            -i $edgeBrokerInventory \
            $playbook

This tells Ansible to execute each task for all hosts BEFORE moving onto the next task.

An additional convenience module is also supported: `solace_get_facts`.
It implements a few functions to directly collect a set of facts without the need to understand the JSON structure.
For example, to get the connection details of a newly created Solace Cloud service use the following in your playbook:

.. code-block:: yaml

  - name: "Gather Solace Facts"
    solace_gather_facts:

  - name: "Get Facts: all client connection details"
    solace_get_facts:
      hostvars: "{{ hostvars }}"
      host: "{{ inventory_hostname }}"
      field_funcs:
        - get_allClientConnectionDetails
    register: result

  - set_fact:
      client_connection_details: "{{ result.facts }}"

  - name: "Save 'client_connection_details' to File"
    copy:
      content: "{{ client_connection_details | to_nice_json }}"
      dest: "./tmp/generated/{{ inventory_hostname }}.client_connection_details.json"


SEMP v2 API Version
-------------------

Across broker releases, the supported SEMP v2 API version evolves.
Where this is the case, the modules affected implement different functionality based on the version and it needs to be passed as a parameter to the module. For example:

.. code-block:: yaml

  - name: "Gather Solace Facts"
    solace_gather_facts:

    # ... create an ACL profile ...

  - name: "ACL Profile Publish Topic Exception"
    solace_acl_publish_topic_exception:
      # jinja2 expression to retrieve the semp version from the gathered facts:
      semp_version: "{{ ansible_facts.solace.about.api.sempVersion }}"
      acl_profile_name: "my-new-profile"
      name: "t/v/a"
      state: present


Settings for ansible-solace modules
-----------------------------------

The settings are NOT documented in the modules.
Instead, the documentation contains the URLs of the SEMP API call / Solace Cloud API call. Use the official documentation to find the settings for each module.


Specifying Solace Cloud Parameters in Playbooks
+++++++++++++++++++++++++++++++++++++++++++++++

Example inventory template including Solace Cloud API token and service id:

.. code-block:: yaml

  ---
  all:
    hosts:
      edge-broker:
        ansible_connection: local
        meta:
          service_name: Ansible-Solace-IoT-Assets-Edge-Broker-1
        sempv2_host: xxx.messaging.solace.cloud
        sempv2_is_secure_connection: true
        sempv2_password: xxxx
        sempv2_port: 943
        sempv2_timeout: '60'
        sempv2_username: xxxx
        solace_cloud_api_token: xxxx
        solace_cloud_service_id: xxxx
        virtual_router: primary
        vpn: xxxx


For example, the module `solace_client_profile` uses a different API for Brokers and Solace Cloud Services.

.. code-block:: yaml

  solace_client_profile:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
    # if inventory contains solace_cloud_api_token and solace_cloud_service_id, use it,
    # otherwise set the parameter to None.
    solace_cloud_api_token: "{{ solace_cloud_api_token | default(omit) }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
