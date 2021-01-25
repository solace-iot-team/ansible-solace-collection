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
module: solace_get_dmr_cluster_link_remote_addresses
TODO: re-work doc
short_description: get remote vpns of bridge

description:
- "Get a list of Bridge Remote VPN objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/getMsgVpnBridgeRemoteMsgVpns)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/bridge/getMsgVpnBridgeRemoteMsgVpns)."

options:
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
- solace.pubsub_plus.solace.get_list

seealso:
- module: solace_bridge_remote_vpn

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
  solace_get_bridge_remote_vpns:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: "Check: Bridge Remote VPN is UP"
    solace_get_bridge_remote_vpns:
        bridge_name: foo
        api: monitor
        query_params:
            where:
            select:
            - bridgeName
            - remoteMsgVpnLocation
            - enabled
            - up
            - lastConnectionFailureReason
            - compressedDataEnabled
            - tlsEnabled
'''

RETURN = '''
result_list:
    description: The list of objects found containing requested fields. Results differ based on the api called.
    returned: success
    type: list
    elements: dict

result_list_count:
    description: Number of items in result_list.
    returned: success
    type: int
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetDmrClusterLinkRemoteAddressesTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def is_supports_paging(self):
        return False

    def get_path_array(self, params: dict) -> list:
        # GET /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/remoteAddresses
        return ['dmrClusters', params['dmr_cluster_name'], 'links', params['remote_node_name'], 'remoteAddresses']


def run_module():
    module_args = dict(
        dmr_cluster_name=dict(type='str', required=True),
        remote_node_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )
    solace_task = SolaceGetDmrClusterLinkRemoteAddressesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
