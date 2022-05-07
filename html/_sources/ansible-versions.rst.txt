Ansible Version Details
=======================

Ansible-Core: 2.12
------------------


Change in `module_defaults`
+++++++++++++++++++++++++++

`ansible-core 2.12` does not use the `collections:` directive in the playbooks when definining `module_defaults`.
This means each module needs to be specified using its fully qualified name:

.. code-block:: yaml

  module_defaults:
    solace.pubsub_plus.solace_acl_profile:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace.pubsub_plus.solace_client_username:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"


Ansible-Core: 2.11
------------------

No particulars.

Ansible-Core: 2.10
------------------

No particulars.
