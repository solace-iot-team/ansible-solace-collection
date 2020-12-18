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
module: solace_bridge

short_description: bridge

description:
  - "Configure a Bridge object. Allows addition, removal and update of a Bridge Object in an idempotent manner."

notes:
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge)."

options:
  name:
    description: The bridge name. Maps to 'bridgeName' in the API.
    required: true
    type: str
  virtual_router:
    description: The virtual router.
    required: false
    type: str
    default: auto
    choices:
      - primary
      - backup
      - auto

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
tasks:
  - name: add
    solace_bridge:
      name: foo
      virtual_router: auto
      settings:
        enabled: false
        remoteAuthenticationBasicClientUsername: default
        remoteAuthenticationBasicPassword: password
        remoteAuthenticationScheme: basic

  - name: update
    solace_bridge:
      name: foo
      virtual_router: auto
      settings:
        enabled: true

  - name: remove
    solace_bridge:
      name: foo
      virtual_router: auto
      state: absent
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


class SolaceBridgeTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'bridgeName'
    WHITELIST_KEYS = ['remoteAuthenticationBasicPassword',
                      'remoteAuthenticationClientCertPassword']
    REQUIRED_TOGETHER_KEYS = [
        ['remoteAuthenticationBasicClientUsername', 'remoteAuthenticationBasicPassword'],
        ['remoteAuthenticationClientCertPassword', 'remoteAuthenticationClientCertContent']
    ]

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['virtual_router']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, virtual_router, bridge_name, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges
        defaults = {
            'msgVpnName': vpn,
            'bridgeVirtualRouter': virtual_router
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: bridge_name
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, virtual_router, lookup_item_value, settings=None):
        # PATCH /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        virtual_router=dict(type='str', default='auto', choices=['primary', 'backup', 'auto'])
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

    solace_task = SolaceBridgeTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
