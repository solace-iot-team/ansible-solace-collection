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
module: solace_client_profile
short_description: client profile for sempv2
description:
- "Configure a Client Profile object using the SEMPV2 API. Allows addition, removal and configuration of Client Profile objects on Solace Brokers in an idempotent manner."
- "Supports only Solace Standalone Brokers - i.e. the SEMPV2 API."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile"
options:
  name:
    description: Name of the client profile. Maps to 'clientProfileName' in the API.
    type: str
    required: true
    aliases: [client_profile, client_profile_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_get_client_profiles
- module: solace_cloud_client_profile
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
    solace_client_profile:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
  tasks:

  - name: exit if solace cloud
    meta: end_play
    when: broker_type == 'solace_cloud'

  - name: create default profile
    solace_client_profile:
      name: foo
      state: present

  - name: update
    solace_client_profile:
      name: foo
      settings:
        allowGuaranteedEndpointCreateEnabled: false
        allowGuaranteedMsgSendEnabled: false
      state: present

  - name: delete
    solace_client_profile:
      name: foo
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceClientProfileTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'clientProfileName'
    OPERATION = 'clientProfile'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['name']]

    def get_func(self, vpn_name, client_profile_name):
        # GET /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, client_profile_name, settings=None):
        # POST /msgVpns/{msgVpnName}/clientProfiles
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, client_profile_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, client_profile_name):
        # DELETE /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str',
                  aliases=['client_profile', 'client_profile_name'],
                  required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceClientProfileTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
