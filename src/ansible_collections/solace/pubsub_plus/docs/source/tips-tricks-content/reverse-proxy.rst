.. _tips-tricks-content-reverse-proxy:

Reverse Proxy / API Gateway
***************************

For securing and managing SEMP API permissions for self-hosted Solace Brokers an API Gateway or Reverse Proxy may be used.
This chapter describes how to configure the inventory and the ansible-solace modules to 'go via' the reverse proxy.

.. note::

  - The below does not work for modules that use the Solace Cloud API, only for SEMP V1 and V2.

Configuring the Reverse Proxy
#############################

When using the ``reverse_proxy`` setting, the ansible-solace modules compose the URL based on the following pattern:

``http(s)://{proxy-host}:{proxy-port}/{proxy-base-path}/<the original SEMP path for the module's operation>``

In addition, two header fields can be selected to be populated at run-time by the module:

  - ``x-asc-module: {module name}``
  - ``x-asc-module-op: {module operation}``

Query parameters of URLs
------------------------

Note that the ``get object list`` modules add query parameters to the URL. Ensure the ``reverse_proxy`` is configured to let them pass through **WITHOUT** URL encoding the ``,`` and ``*``.

Example URL with `where` and `select` query parameters:

.. code-block::

  https://{proxy-host}:{proxy-port}/{proxy-base-path}/SEMP/v2/config/msgVpns/{vpn}/clientUsernames?count=100&select=clientUsername,enabled,guaranteedEndpointPermissionOverrideEnabled&where=clientUsername==ansible-solace*,enabled==true,guaranteedEndpointPermissionOverrideEnabled==true

Example URL with `paging` query parameters:

.. code-block::

  https://{proxy-host}:{proxy-port}/SEMP/v2/config/msgVpns/{vpn}/clientUsernames?cursor=%3Crpc%20semp-version%3D%22soltr%2F9_7VMR%22%3E%3Cshow%3E%3Cclient-username%3E%3Cname%3E%2A%3C%2Fname%3E%3Cvpn-name%3E{vpn}%3C%2Fvpn-name%3E%3Cdetail%2F%3E%3Cfollowing-username%2F%3E%3Cvpn-id-index-param%3E2%3C%2Fvpn-id-index-param%3E%3Cusername-index-param%3E%23client-username%3C%2Fusername-index-param%3E%3Ccount%2F%3E%3Cnum-elements%3E1%3C%2Fnum-elements%3E%3C%2Fclient-username%3E%3C%2Fshow%3E%3C%2Frpc%3E&count=1


Return Codes
------------

The HTTP return codes of the reverse proxy should not interfere with the framework's handling of return codes:

  - ``502`` and ``504`` - the framework will retry the HTTP request a number of times before returning an error
  - ``404`` - the framework interprets it as 'object not found on broker' in a response to a GET call. Returning a ``404`` by the reverse proxy should be avoided.
  - ``500`` and ``501`` - the framework interprets these as an error from the reverse proxy and aborts with a user message


Using the Reverse Proxy
#######################

The ansible-solace modules support the setting ``reverse_proxy``.

Template inventory file specifying the ``semp_reverse_proxy`` settings which can then be used in all playbooks:

.. code-block:: yaml

  ---
  all:
    hosts:
      broker_service_1:
        broker_type: self_hosted
        ansible_connection: local
        semp_is_secure_connection: true
        semp_host: {proxy-host}
        semp_port: {proxy-port}
        semp_username: {username if used}
        semp_password: {password if used}
        semp_timeout: 60
        semp_reverse_proxy:
          # use semp_username + semp_password as basic auth
          use_basic_auth: false
          # dictionary of query parameters the reverse proxy requires
          query_params:
            theApiCode: {code}
            another_param: {value}
          # dictionary of headers the reverse proxy requires
          headers:
            theApiKeyHeader: {api-key}
            # set to true to include the module name in the header
            x-asc-module: true
            # set to true to include the module operation code in the header
            x-asc-module-op: true
          # base path prepended to standard semp api paths
          semp_base_path: {proxy-semp-base-path}


Within a playbook, we can use the inventory setting ``semp_reverse_proxy`` to configure the modules:

.. code-block:: yaml

  hosts: all
  gather_facts: yes
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace_gather_facts:
      secure_connection: "{{ semp_is_secure_connection }}"
      host: "{{ semp_host }}"
      port: "{{ semp_port }}"
      username: "{{ semp_username }}"
      password: "{{ semp_password }}"
      timeout: "{{ semp_timeout }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_get_vpns:
      secure_connection: "{{ semp_is_secure_connection }}"
      host: "{{ semp_host }}"
      port: "{{ semp_port }}"
      username: "{{ semp_username }}"
      password: "{{ semp_password }}"
      timeout: "{{ semp_timeout }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_client_username:
      secure_connection: "{{ semp_is_secure_connection }}"
      host: "{{ semp_host }}"
      port: "{{ semp_port }}"
      username: "{{ semp_username }}"
      password: "{{ semp_password }}"
      timeout: "{{ semp_timeout }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_get_client_usernames:
      secure_connection: "{{ semp_is_secure_connection }}"
      host: "{{ semp_host }}"
      port: "{{ semp_port }}"
      username: "{{ semp_username }}"
      password: "{{ semp_password }}"
      timeout: "{{ semp_timeout }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"

When the modules make calls to the SEMP V1 or V2 APIs, the URL and headers are composed according to the following pattern:

.. code-block::

  http(s)://{host}:{port}/{semp_base_path}/<the original SEMP path for the operation>?{list of query_params from reverse_proxy settings}&{list of query params from the module}

  headers:
   {list of headers from reverse_proxy settings}
   x-asc-module: {module name} # if set to true in reverse_proxy settings
   x-asc-module-op: {module operation} # if set to true in reverse_proxy settings

The headers ``x-asc-module`` and ``x-asc-module-op`` can be used by the reverse proxy for module-based permissioning as opposed to URL resource-based permissioning.
This is useful to permission some SEMP V1 calls since the SEMP V1 URL is always the same.
Using these headers certain module / operation combinations may be allowed/disallowed.

The following operation codes are used:

.. literalinclude:: ../../../plugins/module_utils/solace_module_ops_consts.py
