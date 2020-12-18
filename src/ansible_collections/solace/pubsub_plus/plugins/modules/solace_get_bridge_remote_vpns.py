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
module: solace_get_bridge_remote_vpns

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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceGetBridgeRemoteVpnsTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list_default_query_params(self):
        return None

    def get_list(self):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteMsgVpns
        vpn = self.module.params['msg_vpn']
        bridge_name = self.module.params['bridge_name']
        bridge_virtual_router = self.module.params['bridge_virtual_router']

        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS]
        return self.execute_get_list(path_array)


def run_module():
    module_args = dict(
        bridge_name=dict(type='str', required=True),
        bridge_virtual_router=dict(type='str', default='auto', choices=['primary', 'backup', 'auto'], aliases=['virtual_router']),
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_get_list())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False
    )

    solace_task = SolaceGetBridgeRemoteVpnsTask(module)
    ok, resp_or_list = solace_task.get_list()
    if not ok:
        module.fail_json(msg=resp_or_list, **result)

    result['result_list'] = resp_or_list
    result['result_list_count'] = len(resp_or_list)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
