#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_bridge_remote_subscription
short_description: remote subscription on a bridge
description:
- "Configure a Remote Subscription Object on a bridge. Allows addition and removal of remote subscription objects on a bridge in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/createMsgVpnBridgeRemoteSubscription"
options:
  name:
    description: The subscription topic. Maps to 'remoteSubscriptionTopic' in the API.
    required: true
    type: str
    aliases: [topic, remote_subscription_topic]
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
- solace.pubsub_plus.solace.settings
- solace.pubsub_plus.solace.state
author:
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
  solace_bridge:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
  solace_bridge_remote_subscription:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: create a bridge - disabled
    solace_bridge:
      name: the_bridge
      settings:
        enabled: false
      state: present

  - name: add a remote subscription
    solace_bridge_remote_subscription:
      bridge_name: the_bridge
      remote_subscription_topic: "ansible/solace/test/bridge/da/>"
      settings:
        deliverAlwaysEnabled: true
      state: present

  - name: remove remote subscription
    solace_bridge_remote_subscription:
      bridge_name: the_bridge
      remote_subscription_topic: "ansible/solace/test/bridge/da/>"
      state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceBridgeRemoteSubscriptionsTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'remoteSubscriptionTopic'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['bridge_virtual_router'], params['bridge_name'], params['name']]

    def get_func(self, vpn_name, bridge_virtual_router, bridge_name, remote_subscription_topic):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions/{remoteSubscriptionTopic}
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'bridges', bridge_uri, 'remoteSubscriptions', remote_subscription_topic]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, bridge_virtual_router, bridge_name, remote_subscription_topic, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions
        data = {
            'bridgeName': bridge_name,
            'bridgeVirtualRouter': bridge_virtual_router,
            self.OBJECT_KEY: remote_subscription_topic
        }
        data.update(settings if settings else {})
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'bridges', bridge_uri, 'remoteSubscriptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, bridge_virtual_router, bridge_name, remote_subscription_topic):
        #  DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions/{remoteSubscriptionTopic}
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'bridges', bridge_uri, 'remoteSubscriptions', remote_subscription_topic]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['topic', 'remote_subscription_topic']),
        bridge_name=dict(type='str', required=True),
        bridge_virtual_router=dict(type='str', default='auto', choices=['primary', 'backup', 'auto'], aliases=['virtual_router'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceBridgeRemoteSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
