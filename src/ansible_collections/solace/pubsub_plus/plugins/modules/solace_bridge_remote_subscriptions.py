#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_bridge_remote_subscriptions
short_description: list of remote subscriptions on a bridge
description:
- "Configure a list of Remote Subscription objects on a Bridge in a single transaction."
- "Allows addition and removal of a list of Remote Subscription objects as well as replacement of all existing Remote Subscription objects on a bridge."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates Remote Subscription object list."
- "Reports which topics were added, deleted and omitted (duplicates). In case of an error, reports the invalid Remote Subscription object."
- "To delete all Remote Subscription objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/createMsgVpnBridgeRemoteSubscription"
options:
  names:
    description: The remote subscription topic. Maps to 'remoteSubscriptionTopic' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics, remote_subscription_topics]
    elements: str
  bridge_name:
    description: The bridge. Maps to 'bridgeName' in the API.
    required: true
    type: str
  bridge_virtual_router:
    description: The bridge virtual router. Maps to 'bridgeVirtualRouter' in the API.
    required: false
    type: str
    default: auto
    choices:
      - primary
      - backup
      - auto
    aliases: [virtual_router]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace_bridge
- module: solace_bridge_remote_subscription
- module: solace_get_bridge_remote_subscriptions
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
  # ##########################################################################################
  # sample_topology_file: bridges.topology.yml
  #   bridges:
  #     bridge_1:
  #       # Notes:
  #       # - the hosts and remote_hosts
  #       #   must be the same name as in the main inventory
  #       # - bridges always come in pairs and reference each other
  #       broker_1:
  #         remote_host: broker_2
  #         remote_vpn: broker_2_vpn
  #       broker_2:
  #         remote_host: broker_1
  #         remote_vpn: broker_1_vpn

  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace_gather_facts:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_bridge:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_bridge_remote_vpn:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_bridge_remote_subscriptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_get_bridge_remote_subscriptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
  pre_tasks:
  - include_vars:
      file: "bridges.topology.yml"
      name: bridges_topology
  vars:
      bridge_name: "bridge_1"
  tasks:
    - name: "main: solace_gather_facts"
      solace_gather_facts:

    - name: create bridge
      solace_bridge:
        name: "{{ bridge_name }}"
        state: present

    - name: extract correct parameters based on inventory_hostname
      set_fact:
        remote_inventory_hostname: "{{ bridges_topology.bridges[bridge_name][inventory_hostname].remote_host }}"
        remote_vpn: "{{ bridges_topology.bridges[bridge_name][inventory_hostname].remote_vpn }}"

    - name: get the remote bridge details from gathered facts
      solace_get_facts:
        hostvars: "{{ hostvars }}"
        hostvars_inventory_hostname: "{{ remote_inventory_hostname }}"
        msg_vpn: "{{ remote_vpn }}"
        get_functions:
          - get_vpnBridgeRemoteMsgVpnLocations
      register: remote_host_bridge

    - name: add the remove vpn
      solace_bridge_remote_vpn:
        name: "{{ remote_vpn }}"
        bridge_name: "{{ bridge_name }}"
        bridge_virtual_router: auto
        # choose the correct remote location depending on the settings.tlsEnabled, settings.compressedDataEnabled
        remote_vpn_location: "{{ remote_host_bridge.facts.vpnBridgeRemoteMsgVpnLocations.plain }}"
        settings:
          enabled: false
          tlsEnabled: false
          compressedDataEnabled: false
        state: present

    - name: delete all remote subscriptions
      solace_bridge_remote_subscriptions:
        bridge_name: "{{ bridge_name }}"
        bridge_virtual_router: auto
        remote_subscription_topics: null
        state: exactly

    - name: add remote subscriptions
      solace_bridge_remote_subscriptions:
        bridge_name: "{{ bridge_name }}"
        bridge_virtual_router: auto
        remote_subscription_topics:
          - topic_1
          - topic_2
          - topic_3
        settings:
          deliverAlwaysEnabled: true
        state: present

    - name: delete remote subscriptions
      solace_bridge_remote_subscriptions:
        bridge_name: "{{ bridge_name }}"
        bridge_virtual_router: auto
        remote_subscription_topics:
          - topic_3
        state: absent

    - name: set exactly remote subscriptions
      solace_bridge_remote_subscriptions:
        bridge_name: "{{ bridge_name }}"
        bridge_virtual_router: auto
        remote_subscription_topics:
          - topic_4
          - topic_5
          - topic_6
        settings:
          deliverAlwaysEnabled: true
        state: exactly

    - name: get list of remote subscriptions
      solace_get_bridge_remote_subscriptions:
        bridge_name: "{{ bridge_name }}"
        bridge_virtual_router: auto

    - name: delete bridge
      solace_bridge:
        name: "{{ bridge_name }}"
        virtual_router: auto
        state: absent
'''

RETURN = '''
response:
    description: The response of the operation.
    type: dict
    returned: always
    sample:
      success:
        response:
          -   added: topic-6
          -   added: topic-7
          -   added: duplicate-topic
          -   deleted: topic-1
          -   deleted: topic-2
          -   deleted: topic-3
          -   deleted: topic-4
          -   deleted: topic-5
          -   duplicate: duplicate-topic
      error:
        response:
          -   error: /invalid-topic
msg:
    description: The response from the HTTP call in case of error.
    type: dict
    returned: error
rc:
    description: Return code. rc=0 on success, rc=1 on error.
    type: int
    returned: always
    sample:
        success:
            rc: 0
        error:
            rc: 1
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDListTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceBridgeRemoteSubscriptionsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'remoteSubscriptionTopic'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions
        params = self.get_config().get_params()
        ex_uri = ','.join([params['bridge_name'],
                           params['bridge_virtual_router']])
        return ['msgVpns', params['msg_vpn'], 'bridges', ex_uri, 'remoteSubscriptions']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], params['bridge_virtual_router'], params['bridge_name'], object_key]

    def create_func(self, vpn_name, bridge_virtual_router, bridge_name, remote_subscription_topic, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions
        data = {
            self.OBJECT_KEY: remote_subscription_topic
        }
        data.update(settings if settings else {})
        ex_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns',
                      vpn_name,
                      'bridges',
                      ex_uri,
                      'remoteSubscriptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, bridge_virtual_router, bridge_name, remote_subscription_topic):
        #  DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions/{remoteSubscriptionTopic}
        ex_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'bridges', ex_uri, 'remoteSubscriptions', remote_subscription_topic]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        bridge_name=dict(type='str', required=True),
        bridge_virtual_router=dict(type='str', default='auto', choices=[
                                   'primary', 'backup', 'auto'], aliases=['virtual_router']),
        names=dict(type='list',
                   required=True,
                   aliases=['topics', 'remote_subscription_topics'],
                   elements='str'
                   ),
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud_list())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceBridgeRemoteSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
