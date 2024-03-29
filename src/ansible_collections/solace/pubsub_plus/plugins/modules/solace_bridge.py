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
  - >
    Before configuring a Bridge object, consider deleting it first.
    This ensures that the set-up starts completely fresh.
    For example, adding a new remote vpn to a bridge will not result in any existing remote vpns to be deleted.
    This could mean that invalid remote vpns are 'hanging around', causing the bridge to be not operational.
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge"
seealso:
- module: solace_get_bridges
options:
  name:
    description: The bridge name. Maps to 'bridgeName' in the API.
    required: true
    type: str
  bridge_virtual_router:
    description: The virtual router. Maps to 'bridgeVirtualRouter' in the API.
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
tasks:
- name: delete the bridge first  - starting fresh
  solace_bridge:
    name: foo
    state: absent

- name: add
  solace_bridge:
    name: foo
    bridge_virtual_router: auto
    settings:
      enabled: false
      remoteAuthenticationBasicClientUsername: default
      remoteAuthenticationBasicPassword: password
      remoteAuthenticationScheme: basic

- name: update
  solace_bridge:
    name: foo
    bridge_virtual_router: auto
    settings:
      enabled: true

- name: remove
  solace_bridge:
    name: foo
    bridge_virtual_router: auto
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

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceBridgeTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'bridgeName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['bridge_virtual_router'], params['name']]

    def get_func(self, vpn_name, virtual_router, bridge_name):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'bridges', bridge_uri]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, virtual_router, bridge_name, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges
        data = {
            'bridgeVirtualRouter': virtual_router,
            self.OBJECT_KEY: bridge_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'bridges']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, virtual_router, bridge_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'bridges', bridge_uri]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, virtual_router, bridge_name):
        # DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'bridges', bridge_uri]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
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

    solace_task = SolaceBridgeTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
