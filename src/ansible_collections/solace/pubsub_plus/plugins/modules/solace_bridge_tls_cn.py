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
module: solace_bridge_tls_cn

short_description: trusted common name for bridge

description:
  - "Allows addition and removal of trusted commonn name objects on a bridge in an idempotent manner."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/createMsgVpnBridgeTlsTrustedCommonName."

options:
  name:
    description: The trusted common name. Maps to 'tlsTrustedCommonName' in the API.
    required: true
    type: str
  bridge_name:
    description: The bridge.
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
  solace_bridge_tls_cn:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Remove Trusted Common Name
    solace_bridge_tls_cn:
      name: foo
      bridge_name: bar
      virtual_router: auto
      state: absent

  - name: Add Trusted Common Name
    solace_bridge_tls_cn:
      name: foo
      bridge_name: bar
      virtual_router: auto
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


class SolaceBridgeTrustedCommonNamesTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'tlsTrustedCommonName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['virtual_router'], self.module.params['bridge_name']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, virtual_router, bridge_name, lookup_item_value):
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, virtual_router, bridge_name, trusted_common_name, settings=None):
        """Create a Bridge"""
        defaults = {
            'msgVpnName': vpn,
            'bridgeVirtualRouter': virtual_router
        }
        mandatory = {
            'bridgeName': bridge_name,
            'tlsTrustedCommonName': trusted_common_name
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_TRUSTED_COMMON_NAMES]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, virtual_router, bridge_name, lookup_item_value):
        """Delete a Bridge"""
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        bridge_name=dict(type='str', required=True),
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

    solace_task = SolaceBridgeTrustedCommonNamesTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
