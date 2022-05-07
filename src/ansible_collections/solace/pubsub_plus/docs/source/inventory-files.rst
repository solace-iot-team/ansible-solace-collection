.. _inventory_files:

Best Practices for Ansible-Solace Inventory Files
=================================================

Ansible works with the concept of hosts. In short, a host for Ansible is a virtual machine.
When you run an Ansible Playbook you specify an Inventory File which contains a list of hosts, groups and sub-groups (children) so you can target your Playbook
at a single host or a specific group of hosts.
The Playbook will then execute once for each entry in the list of hosts you specify.
Please consult the `Ansible documentation for more details on Inventory Files <https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html>`_.

**In Ansible-Solace hosts are not virtual machines but Solace PubSub+ Brokers or Solace Cloud Accounts.**

Here are some examples and best practices for defining Inventory Files for Ansible-Solace.

General Comments
----------------
Inventory Files can be written in YAML or JSON - Ansible handles these transparently.

Entries for a Solace Broker (a host) are then accessible in the Playbook as a variable.
Variables can be accessed using Jinja2 notation in the Playbook.


Inventory File for a Standalone Solace PubSub+ Broker
-----------------------------------------------------

.. code-block:: yaml

  ---
  all:
    hosts:
      my_standalone_broker_1:
        broker_type: standalone
        ansible_connection: local
        sempv2_host: 10.12.34.251
        sempv2_port: 8080
        sempv2_is_secure_connection: false
        sempv2_username: admin
        sempv2_password: admin
        sempv2_timeout: '60'
        vpn: default
        virtual_router: primary
      my_standalone_broker_2:
        broker_type: standalone
        ansible_connection: local
        sempv2_host: 10.12.34.251
        sempv2_port: 8080
        sempv2_is_secure_connection: false
        sempv2_username: admin
        sempv2_password: admin
        sempv2_timeout: '60'
        vpn: default
        virtual_router: primary


The structure:

* **all**:
  The above Inventory File defines one group of hosts, called `all`.
* **hosts**:
  Denotes the start of the hosts section. In this example, there are two Solace Brokers defined, `my_standalone_broker_1` and `my_standalone_broker_2`.
* **my_standalone_broker_N**:
  The name of the Solace Broker entry - choose a name that makes sense in your setup.
* **broker_type: ['standalone', 'solace_cloud']**:
  Sometimes you want to write Playbooks that take a different action depending on the type of Solace Broker.
  Using the variable `broker_type` makes this easier.
* **ansible_connection: local**:
  This variable instructs Ansible that it should NOT try to login to the remote host `my_standalone_broker_1` to gather facts about the machine as this would fail.
* **sempv2_host, sempv2_port, sempv2_is_secure_connection, sempv2_username, sempv2_password, sempv2_timeout**:
  These are the connection details for the Solace Broker Semp calls. Most Ansible Solace modules require these as arguments.
* **vpn**:
  If the Solace Broker only has 1 Vpn configured, you can place it into the Inventory File. If multiple Vpns are configured, then it may be better to place it in
  the Ansible Solace module call directly.
* **virtual_router**:
  Similar to Vpn. Either place it in the Inventory File or a module's arguments.

Using the Inventory File Variables in a Playbook
------------------------------------------------

When calling an Ansible Playbook, you specify the Inventory File as an argument:

.. code-block:: bash

  # single inventory file
  ansible-playbook --inventory ./broker.inventory.yml ./my.playbook.yml

  # or you can specify multiple inventory files which ansible merges automatically
  ansible-playbook --inventory ./broker-1.inventory.yml --inventory ./broker-2.inventory.yml ./my.playbook.yml

Within the Playbook, you reference the variables from the Inventory File.
Here is an example structure:

:download:`configure.playbook.yml <../examples/quickstart/configure.playbook.yml>`:

.. literalinclude:: ../examples/quickstart/configure.playbook.yml
   :language: yaml


* **hosts: all** -
  Denotes the group of hosts in the Inventory File to run the Playbook against.
  Here: `my_standalone_broker_1` and `my_standalone_broker_2`.
* **gather_facts: no** -
  Instruction to NOT run the standard Ansible facts gathering modules on the host.
* **collections: solace.pubsub_plus** -
  Saves typing. Ansible will look for a module name `solace_queue` in the collections `solace.pubsub_plus`.
  Alternateively, you can specify the fully qualified module name: `solace.pubsub_plus.solace_queue`.
* **module_defaults:** -
  This allows to specify default values for every instance of the module used in the playbook.
  Saves typing if the same module is used multiple times.

The module `solace_queue` requires the following arguments:

* **host, port, secure_connection, username, password, timeout, msg_vpn** -
  These we'll take from the Inventory File using Jinja2. These change based on the current host being processed by the Playbook.

.. code-block:: yaml

    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"

* **name** -
  We specify the queue name in the call of `solace_queue` directly.

Inventory File for a Solace Cloud Solace PubSub+ Broker
-------------------------------------------------------

.. code-block:: yaml

  all:
      hosts:
          my_solace_cloud_service:
              ansible_connection: local
              broker_type: solace_cloud
              sempv2_host: mr2343xyz.messaging.solace.cloud
              sempv2_is_secure_connection: true
              sempv2_password: v1mux54pcvqd7nbejdsnqhopsk74
              sempv2_port: 943
              sempv2_timeout: '60'
              sempv2_username: sempv2-admin
              solace_cloud_api_token: the-token
              solace_cloud_service_id: 1lfnha94el97
              virtual_router: primary
              vpn: the_vpn_name

The structure is very similar to the standalone broker with the following differences:

* **solace_cloud_service_id** - the service id, which is required for certain calls to the Solace Cloud Api.
* **solace_cloud_api_token** - the api token, which is required for certain calls to the Solace Cloud Api.
* **broker_type:** - is now set to `solace_cloud`.

If security policies do not allow the api token to be stored in files, a simple way to comply is by setting an
environment variable and referencing it in the Playbook instead:

.. code-block:: bash

  export SOLACE_CLOUD_API_TOKEN="the-token"
  ansible-playbook --inventory ./broker.inventory.yml \
                    ./my.playbook.yml \
                    --extra-vars "solace_cloud_api_token=$SOLACE_CLOUD_API_TOKEN"

In the Playbook, you can now reference both, host variables and environment variables:

.. code-block:: yaml

  -
    name: "my playbook"
    hosts: all
    gather_facts: no
    any_errors_fatal: true
    collections:
      - solace.pubsub_plus
    module_defaults:
      solace_cert_authority:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        solace_cloud_api_token: "{{ solace_cloud_api_token if broker_type=='solace_cloud' else omit }}"
        solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"


Using the Jinja2 expressions
`solace_cloud_api_token: "{{ solace_cloud_api_token if broker_type=='solace_cloud' else omit }}"`
and
`solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"`
you now have a Playbook that can cope with standalone brokers and Solace Cloud broker Inventory Files equally.

.. _inventory_files_solace_cloud_account:

Inventory File for a Solace Cloud Account
-----------------------------------------

.. code-block:: yaml

  ---
  all:
    hosts:
      solace-iot-team:
        ansible_connection: local
        broker_type: solace_cloud
        solace_cloud_api_token: the-token
        solace_cloud_home: us

When your Playbook only manages a Solace Cloud account, for example to start/stop services, all you need in the Inventory File is the api token with the correct permissions.

Note: The same considerations as discussed above apply to providing the api-token in the Inventory File or via an environment variable.


Generating Inventory Files for new Brokers
------------------------------------------

In case you want to create services and standalone brokers in a pipeline, Ansible Solace provides tools to
  * create the service / standalone broker
  * generate the inventory files automatically so you can use them in subsequent Playbooks

The following Playbook creates a new standalone broker on the local host and generates the inventory file automatically.
It uses the Ansible Solace role :ref:`solace_broker_service_role`.

.. code-block:: yaml

  -
    name: "create standalone broker in docker"
    hosts: all
    vars:
      genenrated_inventory_file: "./generated-inventories/broker.inventory.yml"
    tasks:
      - name: "Broker Service Setup"
        include_role:
          name: solace.pubsub_plus.solace_broker_service
        vars:
          service_type: docker_single_node
          state: present
          project_name: my_single_node_broker
          container_name: "pubSubStandardSingleNode"
          image: "solace/solace-pubsub-standard:latest"
          generated_inventory_file: "{{ genenrated_inventory_file }}"

Once the broker has been started, the generated Inventory File for subsequent configuration Playbooks is written to:
`./generated-inventories/broker.inventory.yml`.

In the Inventory File for this Playbook you actually specify a virtual machine. So, here, a host IS a host.

`localhost` example:

.. code-block:: yaml

  ---
  all:
    hosts:
      localhost:
        ansible_connection: local

`remote host` example:

.. code-block:: yaml

  ---
  all:
    hosts:
      my-remote-vm:
        ansible_host: 10.21.2.251
        ansible_user: admin-user
        ansible_become: true
        ansible_python_interpreter: "/usr/bin/python"

A similar approach is used for Solace Cloud services. The Playbook:

.. code-block:: yaml

  -
    name: "Start Solace Cloud service"
    hosts: all
    gather_facts: no
    collections:
      - solace.pubsub_plus
    vars:
      genenrated_inventory_file: "./generated-inventories/solace_cloud_service.inventory.yml"
    tasks:
    - name: "Create Solace Cloud Service"
      solace_cloud_service:
        api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
        name: my-new-service
        settings:
          datacenterId: "aws-ca-central-1a"
          serviceTypeId: "enterprise"
          serviceClassId: "enterprise-250-nano"
        state: present
      register: result

    - set_fact:
        sc_service_id: "{{ result.response.serviceId }}"
        sc_service_info: "{{ result.response }}"

    - name: "Get Solace Cloud Service Inventory"
      solace_cloud_get_facts:
        from_dict: "{{ sc_service_info }}"
        get_formattedHostInventory:
          host_entry: my-new-service
          meta:
            service_name: "{{ sc_service_info.name }}"
            sc_service_id: "{{ sc_service_info.serviceId }}"
            datacenterId: "{{ sc_service_info.datacenterId }}"
            serviceTypeId: "{{ sc_service_info.serviceTypeId}}"
            serviceClassId: "{{ sc_service_info.serviceClassId }}"
            serviceClassDisplayedAttributes: "{{ sc_service_info.serviceClassDisplayedAttributes }}"
      register: result

    - name: "Save Solace Cloud Service Inventory to File"
      copy:
        content: "{{ result.facts.formattedHostInventory | to_nice_yaml }}"
        dest: "{{ genenrated_inventory_file }}"
      changed_when: false
      delegate_to: localhost

The Inventory File for the Solace Cloud account:

.. code-block:: yaml

  ---
  all:
    hosts:
      solace-iot-team:
        ansible_connection: local
        broker_type: solace_cloud
        solace_cloud_api_token: the-token


Once the service has been started, the generated Inventory File for subsequent configuration Playbooks is written to:
`./generated-inventories/solace_cloud_service.inventory.yml`.
