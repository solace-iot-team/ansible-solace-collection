# Release Notes

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
