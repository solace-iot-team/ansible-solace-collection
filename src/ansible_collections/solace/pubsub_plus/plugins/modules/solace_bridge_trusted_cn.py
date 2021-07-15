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
module: solace_bridge_trusted_cn
short_description: trusted common name for bridge
description:
  - "Allows addition and removal of trusted commonn name objects on a bridge in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/createMsgVpnBridgeTlsTrustedCommonName"
options:
  name:
    description: The trusted common name. Maps to 'tlsTrustedCommonName' in the API.
    required: true
    type: str
    aliases: [tls_trusted_common_name]
  bridge_name:
    description: The bridge.
    required: true
    type: str
  bridge_virtual_router:
    description: The virtual router.
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
  solace_bridge_trusted_cn:
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

  - name: Remove Trusted Common Name
    solace_bridge_trusted_cn:
      name: "*.my.domain.com"
      bridge_name: the_bridge
      state: absent

  - name: Add Trusted Common Name
    solace_bridge_trusted_cn:
      name: "*.my.domain.com"
      bridge_name: bar
      state: present
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

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceBridgeTrustedCommonNameTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'tlsTrustedCommonName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['bridge_virtual_router'], params['bridge_name'], params['name']]

    def get_func(self, vpn_name, bridge_virtual_router, bridge_name, tls_trusted_cn):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'bridges', bridge_uri, 'tlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, bridge_virtual_router, bridge_name, tls_trusted_cn, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/tlsTrustedCommonNames
        data = {
            'bridgeVirtualRouter': bridge_virtual_router,
            'bridgeName': bridge_name,
            self.OBJECT_KEY: tls_trusted_cn
        }
        data.update(settings if settings else {})
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'bridges', bridge_uri, 'tlsTrustedCommonNames']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, bridge_virtual_router, bridge_name, tls_trusted_cn):
        #  DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'bridges', bridge_uri, 'tlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=[
                  'tls_trusted_common_name']),
        bridge_name=dict(type='str', required=True),
        bridge_virtual_router=dict(type='str', default='auto', choices=[
                                   'primary', 'backup', 'auto'], aliases=['virtual_router'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceBridgeTrustedCommonNameTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
