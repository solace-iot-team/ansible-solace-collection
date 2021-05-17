Solace Configuration & Action Modules
=====================================

Configuration modules mostly use the Solace Sempv2 Config Api. Some modules also use the Solace Cloud Api where required,
so the same module can be used for both, standalone brokers and Solace Cloud services.

* Solace Sempv2 Config Api: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html
* Solace Cloud Rest Api: https://docs.solace.com/Solace-Cloud/solace_cloud_rest_api.htm

Configuration Settings for Modules
----------------------------------

Each API used, Sempv2, Sempv1, Solace Cloud, offers settings or parameters to be included.

The settings are NOT documented in the modules.

Instead, each module documentation contains the URLs of the SEMP API call / Solace Cloud API call.
Use the official documentation to find the settings for each module.

For example, module: :ref:`solace_queue_module`
is based on the Sempv2 Config Api: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue.

Creating a queue is based on this call: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue/createMsgVpnQueue.

We can see the accepted settings, such as:

  * accessType
  * consumerAckPropagationEnabled
  * deadMsgQueue
  * ...

Example Usage
+++++++++++++

Modify these settings in a playbook using the `settings` argument:

.. code-block:: yaml

  name: Quickstart Configure Playbook
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace_queue:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
    - name: create queue
      solace_queue:
        name: quickstart_queue
        settings:
          accessType: non-exclusive
          consumerAckPropagationEnabled: false
        state: present


Idempotency
-----------
The configuration modules update/add/delete Broker objects in an idempotent manner.

They argument `state=[present, absent]` determines the desired outcome of the module.
The module's behavior is as follows:

**state='present'**:

* get the current object from the broker
* if not found:

  - create a new object

* if found:

  - create a delta settings by comparing current object settings with target settings specified in the playbook
  - update the broker object with the target settings

**state='absent'**:

* check if the object exists
* if found:

  - delete the object

* if not found:

  - do nothing


Module Reference
----------------

.. toctree::
   :glob:
   :maxdepth: 1

   modules/solace_acl_*
   modules/solace_auth*
   modules/solace_bridge*
   modules/solace_cert_authority*
   modules/solace_client*
   modules/solace_dmr_*
   modules/solace_mqtt_session*
   modules/solace_queue*
   modules/solace_rdp*
   modules/solace_replay*
   modules/solace_topic_endpoint*
   modules/solace_vpn
