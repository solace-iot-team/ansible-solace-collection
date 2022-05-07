Solace Get Object List Modules
==============================

Get Object List modules mostly use the Solace Sempv2 Config and Monitor Apis to get a list of objects.
Some modules also use the Solace Cloud Api where required, so the same module can be used for both,
standalone brokers and Solace Cloud services.

* Solace Sempv2 Config Api: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html
* Solace Sempv2 Monitor Api: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html
* Solace Cloud Rest Api: https://docs.solace.com/Solace-Cloud/solace_cloud_rest_api.htm


Module Reference
----------------

.. toctree::
   :glob:
   :maxdepth: 1

   modules/solace_get_*

.. toctree::
   :hidden:

   modules/solace_get_available
   modules/solace_get_facts
