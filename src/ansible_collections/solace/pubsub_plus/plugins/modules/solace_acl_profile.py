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
module: solace_acl_profile
short_description: configure acl profile
description:
- "Configure an ACL Profile on a message vpn. Allows addition, removal and configuration of ACL Profile(s) on Solace Brokers in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile"
options:
    name:
        description: Name of the ACL Profile. Maps to 'aclProfileName' in the API.
        type: str
        required: true
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_get_acl_profiles
- module: solace_acl_subscribe_topic_exception
- module: solace_acl_subscribe_topic_exceptions
- module: solace_get_acl_subscribe_topic_exceptions
- module: solace_acl_client_connect_exception
- module: solace_acl_client_connect_exceptions
- module: solace_get_acl_client_connect_exceptions
- module: solace_acl_publish_topic_exception
- module: solace_acl_publish_topic_exceptions
- module: solace_get_acl_publish_topic_exceptions
- module: solace_acl_subscribe_share_name_exception
- module: solace_acl_subscribe_share_name_exceptions
- module: solace_get_acl_subscribe_share_name_exceptions
author:
  - Mark Street (@mkst)
  - Swen-Helge Huber (@ssh)
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
  solace_acl_profile:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Remove ACL Profile
    solace_acl_profile:
      name: foo
      state: absent

  - name: Add ACL Profile
    solace_acl_profile:
      name: foo
      settings:
        clientConnectDefaultAction: allow

  - name: Update ACL Profile
    solace_acl_profile:
      name: foo
      settings:
        publishTopicDefaultAction: allow
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
    sample:
        aclProfileName: test_ansible_solace
        clientConnectDefaultAction: disallow
        msgVpnName: default
        publishTopicDefaultAction: disallow
        subscribeShareNameDefaultAction: allow
        subscribeTopicDefaultAction: disallow
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceACLProfileTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'aclProfileName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def validate_params(self):
        name = self.get_module().params['name']
        if len(name) > 32:
            raise SolaceParamsValidationError(
                'name', name, f"length={len(name)}, must not be longer than 32 chars")

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['name']]

    def get_func(self, vpn_name, acl_profile_name):
        # GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'aclProfiles', acl_profile_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, acl_profile_name, settings=None):
        # POST /msgVpns/{msgVpnName}/aclProfiles
        data = {
            'msgVpnName': vpn_name,
            self.OBJECT_KEY: acl_profile_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'aclProfiles']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, acl_profile_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'aclProfiles', acl_profile_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, acl_profile_name):
        # DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'aclProfiles', acl_profile_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceACLProfileTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
