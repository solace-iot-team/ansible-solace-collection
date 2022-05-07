Solace Cloud Modules
====================

Some Solace Cloud modules require the Solace Cloud API Token as an argument.
This can either be provided in the inventory file or as an environment variable for example.

See a detailed discussion here: :ref:`inventory_files_solace_cloud_account`.

Setting Solace Cloud Home Cloud Region
--------------------------------------

Ansible Solace currently supports two Home Cloud Regions: `us` & `au`.

You can either use an environment variable to set the home region for all solace cloud modules and/or you can specify an additional parameter module by module.

Environment Variable: `ANSIBLE_SOLACE_SOLACE_CLOUD_HOME` , values: ["US", "AU"].

Module parameter:

* solace_cloud_home: choices=['us', 'au']

The logic of choosing the home region is as follows:

.. code-block:: none

  - default: US
  - if module parameter solace_cloud_home is set, use value from module parameter
  - else
    - check if env var is set and use value from env
  - else
    - use default


Module Reference
----------------

.. toctree::
   :glob:
   :maxdepth: 1

   modules/solace_cloud*
