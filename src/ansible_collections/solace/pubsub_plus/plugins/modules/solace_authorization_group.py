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
module: solace_authorization_group
short_description: authorization group
description:
- "Configure a Authorization Group object on a Message Vpn. Allows addition, removal and configuration of objects in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/authorizationGroup"
options:
  name:
    description: Name of the Authorization Group. Maps to 'authorizationGroupName' in the API.
    required: true
    type: str
    aliases: [authorization_group, authorization_group_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_get_authorization_groups
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
  solace_authorization_group:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: add
  solace_authorization_group:
    name: bar
    setttings:
      enabled: false
      aclProfileName: foo
    state: present

- name: update
  solace_authorization_group:
    name: bar
    setttings:
      enabled: true
    state: present

- name: remove
  solace_authorization_group:
    name: bar
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
import urllib


class SolaceAuthorizationGroupTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'authorizationGroupName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        # authorization group names contain ',' and '='
        # '=' must not be encoded, ',' instead must be encoded
        self.sempv2_api.set_safe_for_path_array('=')

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['name']]

    def get_func(self, vpn_name, authorization_group_name):
        # GET /msgVpns/{msgVpnName}/authorizationGroups/{authorizationGroupName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'authorizationGroups', authorization_group_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array, )

    def create_func(self, vpn_name, authorization_group_name, settings=None):
        # POST /msgVpns/{msgVpnName}/authorizationGroups
        data = {
            'msgVpnName': vpn_name,
            self.OBJECT_KEY: authorization_group_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'authorizationGroups']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, authorization_group_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/authorizationGroups/{authorizationGroupName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'authorizationGroups', authorization_group_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, authorization_group_name):
        # DELETE /msgVpns/{msgVpnName}/authorizationGroups/{authorizationGroupName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'authorizationGroups', authorization_group_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=[
                  'authorization_group', 'authorization_group_name'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceAuthorizationGroupTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
