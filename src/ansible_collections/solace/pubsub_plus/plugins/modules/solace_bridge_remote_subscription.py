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

short_description: remote subscription on a bridge.

description:
- "Configure a Remote Subscription Object on a bridge.. Allows addition and removal of remote subscription objects on a bridge in an idempotent manner."

notes:
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/createMsgVpnBridgeRemoteSubscription)."

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
  solace_topic_endpoint:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Remove Remote Subscription
    solace_bridge_remote_subscription:
      name: foo
      bridge_name: bar
      virtual_router: auto
      state: absent

  - name: Add Remote Subscription
    solace_bridge_remote_subscription:
      name: foo
      bridge_name: bar
      virtual_router: auto
      deliver_always: true
      state: present
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceBridgeRemoteSubscriptionsTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'remoteSubscriptionTopic'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'],
                self.module.params['bridge_virtual_router'],
                self.module.params['bridge_name']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, virtual_router, bridge_name, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions/{remoteSubscriptionTopic}
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_SUBSCRIPTIONS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, virtual_router, bridge_name, topic, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions
        defaults = {
        }
        mandatory = {
            'msgVpnName': vpn,
            'bridgeName': bridge_name,
            'bridgeVirtualRouter': virtual_router,
            self.LOOKUP_ITEM_KEY: topic
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_SUBSCRIPTIONS]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, virtual_router, bridge_name, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteSubscriptions/{remoteSubscriptionTopic}
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_SUBSCRIPTIONS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['topic', 'remote_subscription_topic']),
        bridge_name=dict(type='str', required=True),
        bridge_virtual_router=dict(type='str', default='auto', choices=['primary', 'backup', 'auto'], aliases=['virtual_router'])
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceBridgeRemoteSubscriptionsTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
