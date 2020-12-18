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
module: solace_get_vpn_clients

short_description: list of vpn clients

description:
- "Get a list of VPN Client objects."

notes:
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/client/getMsgVpnClients)."

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list_monitor

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
  solace_get_vpn_clients:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Get a list of all VPN Client Objects
    solace_get_vpn_clients:
    register: result

  - name: Print
    debug:
      msg:
        - "{{ result.result_list }}"
        - "{{ result.result_list_count }}"
'''

RETURN = '''
result_list:
    description: The list of objects found containing requested fields.
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


class SolaceGetVpnClientsTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list(self):
        # GET monitor/msgVpns/{msgVpnName}/clients
        # only exists on monitor
        self.module.params['api'] = 'monitor'
        vpn = self.module.params['msg_vpn']
        path_array = [su.MSG_VPNS, vpn, su.CLIENTS]
        return self.execute_get_list(path_array)


def run_module():
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_get_list_monitor())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False
    )

    solace_task = SolaceGetVpnClientsTask(module)
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
