# Release Notes

## Version: 1.5.1
Client Profile & Bug Fixes

**New Modules**
* **[solace_cloud_client_profile](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_cloud_client_profile.html)**
  - separated client profile management into Solace Cloud API and SempV2 API

**Updated Modules**
* **[solace_client_profile](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_client_profile.html)**
  - removed support for Solace Cloud

**Bug Fixes**
* **[solace_client_profile](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_client_profile.html)**
  - settings value conversion from ansible to SEMP v2 API fixed
* **[solace_service_authentication_ldap_profile](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_service_authentication_ldap_profile.html)**
  - set min sempv1 version to 9.1

## Version: 1.5.0
Framework Enhancements & New Modules

**New Modules**
* **[solace_queue_subscriptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_queue_subscriptions.html)**
* **[solace_get_acl_publish_topic_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_acl_publish_topic_exceptions.html)**
* **[solace_acl_publish_topic_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_acl_publish_topic_exceptions.html)**
* **[solace_get_acl_subscribe_topic_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_acl_subscribe_topic_exceptions.html)**
* **[solace_acl_subscribe_topic_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_acl_subscribe_topic_exceptions.html)**
* **[solace_get_acl_subscribe_share_name_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_acl_subscribe_share_name_exceptions.html)**
* **[solace_acl_subscribe_share_name_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_acl_subscribe_share_name_exceptions.html)**
* **[solace_get_acl_client_connect_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_acl_client_connect_exceptions.html)**
* **[solace_acl_client_connect_exceptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_acl_client_connect_exceptions.html)**
* **[solace_get_bridge_remote_subscriptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_bridge_remote_subscriptions.html)**
* **[solace_bridge_remote_subscriptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_bridge_remote_subscriptions.html)**

**Updated Modules**
* **[solace_gather_facts](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_gather_facts.html)**
  - added an argument: `use_sempv1_also: [true|false]`. defaults to `true`. if `true`, module uses sempv1 to get the virtual router name for a self-hosted service.

**Framework**
* **new: SolaceBrokerCRUDListTask**
  - manage lists of names (topics) as a 'transaction'

**Devel**
* **README, devel.requirements.txt**
  - remove install of ansible to allow for choice of version

**Misc**
* adapted import statements for new pylint version throughout

**Documentation**
- added a note that modules do not support check-mode


## Version: 1.4.4
Maintenance: Support for Ansible 2.11.x

**Fixes**
* **[solace_get_available](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_available.html)**
  - fixed using SSL with python >3.8
* **[solace_authorization_group](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_authorization_group.html)**
  - fixed url encoding of name. handles names containing ',' and '=' correctly, for example `cn=asct_auth_group_1,ou=Users,o=orgId,dc=domain,dc=com`

## Version: 1.4.3
Enhancements & New Features.

**Module Enhancements:**
* **[solace_service_authentication_ldap_profile](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_service_authentication_ldap_profile.html)**
  - added support for Solace Cloud API
* **[solace_get_service_authentication_ldap_profiles](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_service_authentication_ldap_profiles.html)**
  - added support for Solace Cloud API
* **[solace_vpn](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_vpn.html)**
  - added support for Solace Cloud API

**New Features:**
* **[support for reverse-proxy](https://solace-iot-team.github.io/ansible-solace-collection//tips-tricks-content/reverse-proxy.html)**
  - reverse proxy settings for self-hosted brokers
  - status: **Experimental**

## Version: 1.4.2
Enhancements of SEMP V1 Framework.

Added support for writing get list modules that use the SEMP V1 API.

**_Note: EXPERIMENTAL_**

New modules:

* **[solace_get_service_authentication_ldap_profiles](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_service_authentication_ldap_profiles.html)**
  - module uses the SEMP V1 API
  - Solace Cloud API not implemented

## Version: 1.4.1
Introduction of SEMP V1 Task Framework.

Added support for writing modules that use the SEMP V1 API.

**_Note: EXPERIMENTAL_**

New modules:

* **[solace_service_authentication_ldap_profile](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_service_authentication_ldap_profile.html)**
  - module uses the SEMP V1 API
  - Solace Cloud API not implemented

## Version: 1.4.0
New modules.

* [**solace_get_authorization_groups**](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_authorization_groups.html)
* [**solace_authorization_group**](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_authorization_group.html)
* [**solace_get_authentication_oauth_providers**](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_authentication_oauth_providers.html)
* [**solace_authentication_oauth_provider**](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_authentication_oauth_provider.html)

## Version: 1.3.3
Maintenance

* **tests**
  - fixed tests for new broker release, sempv2 version 2.21
* **[Tips&Tricks:Setting & Retrieving Ansible-Solace Log Files](https://solace-iot-team.github.io/ansible-solace-collection/tips-tricks-content/logfile.html)**
  - fixed example playbook

## Version: 1.3.2
Examples for using Ansible Jump Host & Minor Module Enhancements/Maintenance.

Documentation:

* **[Tips&Tricks:Setting & Retrieving Ansible-Solace Log Files](https://solace-iot-team.github.io/ansible-solace-collection/tips-tricks-content/logfile.html)**
  - new.
* **[Tips&Tricks:Working through a Remote ‘Bastion’ or ‘Jump’ Host](https://solace-iot-team.github.io/ansible-solace-collection/tips-tricks-content/bastion.html)**
  - new.

Enhancements:
* **solace_cloud_get_facts**
  - added function: `get_remoteFormattedHostInventory` - retrieve service inventory for remote  bastion host

Maintenance:
* **solace_cloud_get_facts**
  - graceful handling of services in state=failed
* **solace_cloud_service**
  - handling of retry on service creation failed: added wait between re-tries
  - added idempotent handling of eventBrokerVersion
* **solace_api.SolaceCloudApi**
  - handling return settings as list and dict


## Version: 1.3.1
Maintenance.

* **roles/solace_broker_service**
  - additional tests for correct passing of variables and extended error messages

## Version: 1.3.0
Feature Updates.

_**Note: this release contains breaking changes.**_

* **Roles:**
  - [solace_broker_service](https://solace-iot-team.github.io/ansible-solace-collection/roles/solace_broker_service.html)
    - _note: breaking change: input & output arguments/variables changed._
    - added example for secure SEMP setup
    - re-vamp of input vars & merging with defaults
    - changed output to include final inventory, docker compose settings, and docker logs
* **Modules:**
  - [solace_get_available](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_available.html)
    - added functionality to a) check if broker is reachable, b) check if spool initialized
    - loops/waits until both are available (no loop required around module any more)
* **Documentation**
  - New: [Working with Self-Signed Certificates](https://solace-iot-team.github.io/ansible-solace-collection/tips-tricks-content/certs.html)
* **Framework**
  - added explicit exception handling for SSLErrors
  - added detailed traceback of Exceptions to log file
  - handling of `502:Bad Gateway` and `504:Gateway Timeout` for REST calls (retry: every 30 secs, 20 times max)

## Version: 1.2.1
Maintenance release.

* **roles:**
  - [solace_broker_service](https://solace-iot-team.github.io/ansible-solace-collection/roles/solace_broker_service.html)
    - fixed remote vm support
* **documentation**
  - [added bridges to tips & tricks](https://solace-iot-team.github.io/ansible-solace-collection/tips-tricks.html)
* **tests**
  - dmr: fixed timing issues and host name mismatch
  - docs: added linkcheck to tests

## Version: 1.2.0
Addition of modules to manage replay of messages.

_**Note: this release contains minor breaking changes.**_

#### New Modules
  * config:
    - [solace_replay_log](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_replay_log.html)
  * action:
    - [solace_replay_log_trim_logged_msgs](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_replay_log_trim_logged_msgs.html)
    - [solace_queue_start_replay](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_queue_start_replay.html)
    - [solace_queue_cancel_replay](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_queue_cancel_replay.html)
  * get list
    - [solace_get_replay_logs](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_replay_logs.html)

#### Updated Modules
  * facts:
    - [solace_get_facts](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_facts.html)
      - standardized the output for Solace Cloud and self-hosted brokers
      - _note: breaking change: may require minor adjustment of playbooks evaluating response._
  * get list:
    - _note: breaking change: requires minor adjustment of playbooks evaluating response._
    - all get object list modules
      - config & monitor apis:
          - contains new dictionary: data {}
      - monitor api:
        - contains additional dictionary: collections {}

#### Known Issues

  * Api calls fail on response 504: Bad Gateway
  * module: solace_get_available - does not check if spool is available for self-hosted brokers
  * ansible checkmode not implemented

## Version: 1.1.0
Refactor framework to streamline module interfaces and development.

_**Note: the release breaks existing playbooks. some module args have changed.**_

#### Documentation
  * detailed description of inventory files and their use in playbooks

#### New / Updated Modules
  * [solace_cloud_get_services](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_cloud_get_services.html)
  * [solace_acl_subscribe_share_name_exception](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_acl_subscribe_share_name_exception.html)
  * [solace_cert_authority](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_cert_authority.html)
  * [solace_get_acl_profiles](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_acl_profiles.html)
  * [solace_get_cert_authorities](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_cert_authorities.html)
  * [solace_get_dmr_bridges](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_dmr_bridges.html)
  * [solace_get_dmr_cluster_link_remote_addresses](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_dmr_cluster_link_remote_addresses.html)
  * [solace_get_dmr_cluster_link_trusted_cns](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_dmr_cluster_link_trusted_cns.html)
  * [solace_get_dmr_cluster_links](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_dmr_cluster_links.html)
  * [solace_get_dmr_clusters](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_dmr_clusters.html)
  * [solace_get_queue_subscriptions](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_queue_subscriptions.html)
  * [solace_get_rdp_queue_bindings](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_rdp_queue_bindings.html)
  * [solace_get_rdp_rest_consumer_trusted_cns](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_rdp_rest_consumer_trusted_cns.html)
  * [solace_get_rdp_rest_consumers](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_rdp_rest_consumers.html)
  * [solace_get_topic_endpoints](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_topic_endpoints.html)
  * [solace_get_vpn_clients](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_vpn_clients.html)
  * [solace_get_vpns](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_vpns.html)
  * [solace_get_facts](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_get_facts.html)

#### Removed Modules

  * **solace_bridge_tls_cn** - renamed to [solace_bridge_trusted_cn](https://solace-iot-team.github.io/ansible-solace-collection/modules/solace_bridge_trusted_cn.html)

#### Refactored Framework

* separated tasks & apis
  - allows for a task to use one or more apis as required
  - specialized task classes (crud, get list, solace cloud account, solace cloud, ...)
  - specialized api classes (sempv2 config, sempv2 paging, sempv1, solace_cloud, ...)
* streamlined result set for modules
  - each module returns rc=0,1, msg='error message'
  - crud modules return response
  - list modules return result_list and result_list_count
* streamlined error handling
  - specialized exception classes
  - {task-class}.execute(): wraps do_task() with exception handling
  - ensures consistent approach to exceptions
  - allows tasks to raise exception at any point
* module update handling changed
  - existing settings are still compared to target settings to determine if a patch request should happen
  - if that is the case, now ALL settings configured in the playbook are sent, not just the delta
  - overcomes the issue of attributes not returned by the API (e.g. passwords, inconsistencies in solace cloud api)
  - overcomes the 'required_together' issue for some APIs - no need to treat them explicitly

## Version: 1.0.0
Initial Release.

Based on previous project [ansible-solace-modules](https://github.com/solace-iot-team/ansible-solace-modules).

Refactored as Ansible Collection.

---
