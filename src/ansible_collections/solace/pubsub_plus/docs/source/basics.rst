The Basics
==========

The `ansible-solace` modules use a variety of the APIs provided by the Solace PubSub+ Platform:
* Sempv2 Config & Monitor Api
* Sempv1 Api for situations where no equivalent Sempv2 call exists
* Solace Cloud Api for specific functionality only available in Solace Cloud
* A mix of Apis, where the Api used depends on the Solace Broker edition. For example, client profile & certificate authorities.

The modules generally follow the same naming convention as the SEMP v2 API calls so there is an easy mapping between the SEMP documentation and the `ansible-solace` module name.
For example: SEMP v2 API: `clientUsername`_ maps to :ref:`solace_client_username_module`.

.. _clientUsername:
  https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientUsername

Some specific Solace Cloud APIs have modules as well, such as creating and deleting a service. They are named `solace_cloud_{module}`.

Types of Modules
----------------

* **Configuration modules**: `solace_{configuration-object}`.
  - add/update/delete a configuration object
  - support the **state** parameter with **values=['present', 'absent']**
  - support to configure the Broker objects in an idempotent manner
* **Monitor modules**: `solace_get_{configuration_object}s`.
  - retrieve a list of configuration objects, either from the monitor or config Api

Ansible Hosts are not Hosts but Brokers
---------------------------------------

The Ansible concept of a host is that, a machine which Ansible logs into, transfers scripts, executes scripts, etc.

**For `ansible-solace`, hosts are actually Brokers or Solace Cloud Accounts.**

Which means a few things:
  - Ansible cannot login and run it's normal setup / fact gathering routines
  - instead, `ansible-solace` provides specialized fact gathering modules: :ref:`solace_gather_facts_module` and :ref:`solace_cloud_account_gather_facts_module`
  - therefore, always use the following settings in your inventory / playbooks:

.. code-block:: yaml

  ansible_connection: local
  gather_facts: no
