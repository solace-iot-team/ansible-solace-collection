.. _tips-tricks:

Tips & Tricks
=============

Working with Bridges & Links
----------------------------

When working with bridges and links, the Ansible playbook needs to configure both sides of the bridge or link.
For example, when configuring a bridge between two brokers `broker_a` and `broker_b` the sequence is as follows:

:client username: for the bridge to use to connect to the remote broker
:queue: the queue for the bridge
:queue subscription: the subscription to events going into the queue
:bridge: the bridge
:bridge remote vpn: the remote broker connection
:bridge remote subscription: the subscription to events going across the bridge

The key here is that the above sequence needs to be run on *broker_a* **AND** *broker_b* whilst having access to the remote broker's facts.

Let's use the following inventory file:

* defines two brokers: *broker_a* and *broker_b*
* on each broker, defines the bridge remote counterpart: *broker_a==>broker_b* and *broker_b==>broker_a*

.. code-block:: yaml

  ---
  all:
    hosts:
      broker_a:
        # ansible-solace module configuration
        broker_type: local
        ansible_connection: local
        sempv2_host: broker_a_vm.messaging.acme.com
        sempv2_port: 8080
        sempv2_is_secure_connection: false
        sempv2_username: admin
        sempv2_password: admin
        sempv2_timeout: '60'
        vpn: broker_a_vpn
        virtual_router: primary
        # bridge remote counterpart configuration
        bridge_1:
          remote_host: broker_b
          remote_vpn: broker_b_vpn
      broker_b:
        # ansible-solace module configuration
        broker_type: local
        ansible_connection: local
        sempv2_host: broker_b_vm.messaging.acme.com
        sempv2_port: 8080
        sempv2_is_secure_connection: false
        sempv2_username: admin
        sempv2_password: admin
        sempv2_timeout: '60'
        vpn: broker_b_vpn
        virtual_router: primary
        # bridge remote counterpart configuration
        bridge_1:
          remote_host: broker_a
          remote_vpn: broker_a_vpn


Let's take this cut down playbook:

.. code-block:: yaml

  tasks:
    - solace_gather_facts:

    - solace_client_username:
      name: bridge_1
      settings:
        enabled: true
        password: bridge_1_password
      state: present

    # ... create queue, subscription

    - solace_bridge:
      name: bridge_1
      settings:
        enabled: false
        remoteAuthenticationBasicClientUsername: bridge_1
        remoteAuthenticationBasicPassword: bridge_1_password
        remoteAuthenticationScheme: basic
      state: present

      # read the bridge parameters from the inventory
    - set_fact:
        remote_inventory_hostname: "{{ bridge_1.remote_host }}"
        remote_vpn: "{{ bridge_1.remote_vpn }}"

      # get the facts of the remote broker
    - solace_get_facts:
        hostvars: "{{ hostvars }}"
        hostvars_inventory_hostname: "{{ remote_inventory_hostname }}"
        msg_vpn: "{{ remote_vpn }}"
        get_functions:
          - get_vpnBridgeRemoteMsgVpnLocations
      register: remote_host_bridge

      # set the remote parameters on the bridge
    - solace_bridge_remote_vpn:
        name: "{{ remote_vpn }}"
        bridge_name: bridge_1
        bridge_virtual_router: auto
        # choose the correct remote location depending on the settings.tlsEnabled, settings.compressedDataEnabled
        remote_vpn_location: "{{ remote_host_bridge.facts.vpnBridgeRemoteMsgVpnLocations.plain }}"
        settings:
          enabled: false
          tlsEnabled: false
          compressedDataEnabled: false
          queueBinding: bridge_1
        state: present

    # ... add a trusted common name if required

    - solace_bridge_remote_subscription:
        bridge_name: bridge_1
        bridge_virtual_router: auto
        remote_subscription_topic: "ansible/solace/test/bridge/da/>"
        settings:
          deliverAlwaysEnabled: true
        state: present


The correct execution of the above playbook depends on ensuring that it has access to the facts from all brokers in the task
**solace_get_facts**.
To achieve that, we can use a simple trick Ansible provides, setting **forks=1**. This ensures that each task is executed on all hosts in the
inventory before the playbook moves on to the next task.

Example:

.. code-block:: bash

  ansible-playbook \
                --forks 1 \
                -i my-inventory-file.yml
                my-bridge-playbook.yml


.. seealso::

  - `Ansible Solace - Solace Cloud Full Mesh`_ for an example of setting up a full mesh using DMR and external links



.. _Ansible Solace - Solace Cloud Full Mesh:
  https://github.com/solace-iot-team/ansible-solace/tree/master/solace-cloud-full-mesh
