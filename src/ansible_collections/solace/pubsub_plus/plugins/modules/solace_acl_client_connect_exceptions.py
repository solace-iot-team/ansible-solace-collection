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
module: solace_acl_client_connect_exceptions
short_description: list of client connect address exceptions on an acl profile
description:
- "Configure a list of Client Connect Address Exception objects on an ACL Profile in a single transaction."
- "Allows addition and removal of a list of Client Connect Address Exception objects as well as replacement of all existing Client Connect Address Exception objects on an ACL Profile."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates Client Connect Address Exception object list."
- "Reports which addresses were added, deleted and omitted (duplicates). In case of an error, reports the invalid Client Connect Address Exception object."
- "To delete all Client Connect Address Exception objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfileClientConnectException"
options:
  names:
    description: The client addresses. Maps to 'clientConnectExceptionAddress' in the SEMP v2 API.
    required: true
    type: list
    aliases: [addresses]
    elements: str
  acl_profile_name:
    description: The ACL Profile. Maps to 'aclProfileName' in the SEMP v2 API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace_acl_profile
- module: solace_acl_client_connect_exception
- module: solace_get_acl_client_connect_exceptions
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
    solace_acl_profile:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_acl_client_connect_exceptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_get_acl_client_connect_exceptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
  tasks:
    - name: create acl profile
      solace_acl_profile:
        name: foo
        state: present

    - name: add list of exceptions
      solace_acl_client_connect_exceptions:
        acl_profile_name: foo
        addresses:
        - 10.2.3.11/1
        - 10.2.3.11/2
        state: present

    - name: get list of exceptions
      solace_get_acl_client_connect_exceptions:
        acl_profile_name: foo

    - name: add second list of exceptions
      solace_acl_client_connect_exceptions:
        acl_profile_name: foo
        addresses:
        - 10.2.3.11/3
        - 10.2.3.11/4
        state: present

    - name: get list of exceptions
      solace_get_acl_client_connect_exceptions:
        acl_profile_name: foo

    - name: replace list of exceptions
      solace_acl_client_connect_exceptions:
        acl_profile_name: foo
        addresses:
        - 10.2.3.11/5
        - 10.2.3.11/6
        state: exactly

    - name: get list of exceptions
      solace_get_acl_client_connect_exceptions:
        acl_profile_name: foo

    - name: delete all exceptions
      solace_acl_client_connect_exceptions:
        acl_profile_name: foo
        addresses: null
        state: exactly

    - name: get list of exceptions
      solace_get_acl_client_connect_exceptions:
        acl_profile_name: foo

    - name: delete acl profile
      solace_acl_profile:
        name: foo
        state: absent
'''

RETURN = '''
response:
    description: The response of the operation.
    type: dict
    returned: always
    sample:
      success:
        response:
          -   added: topic-6
          -   added: topic-7
          -   added: duplicate-topic
          -   deleted: topic-1
          -   deleted: topic-2
          -   deleted: topic-3
          -   deleted: topic-4
          -   deleted: topic-5
          -   duplicate: duplicate-topic
      error:
        response:
          -   error: /invalid-topic
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDListTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceACLClientConnectExceptionsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'clientConnectExceptionAddress'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/clientConnectExceptions
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'aclProfiles', params['acl_profile_name'], 'clientConnectExceptions']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], params['acl_profile_name'], object_key]

    def create_func(self, vpn_name, acl_profile_name, address, settings=None):
        # POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/clientConnectExceptions
        data = {
            'msgVpnName': vpn_name,
            'aclProfileName': acl_profile_name,
            self.OBJECT_KEY: address
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name,
                      'aclProfiles', acl_profile_name, 'clientConnectExceptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, acl_profile_name, address):
        # DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/clientConnectExceptions/{clientConnectExceptionAddress}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name,
                      'aclProfiles', acl_profile_name,
                      'clientConnectExceptions',
                      address]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        acl_profile_name=dict(type='str', required=True),
        names=dict(type='list',
                   required=True,
                   aliases=['addresses'],
                   elements='str'
                   ),
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud_list())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceACLClientConnectExceptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
