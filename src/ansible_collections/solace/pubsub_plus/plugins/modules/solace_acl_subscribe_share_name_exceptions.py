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
module: solace_acl_subscribe_share_name_exceptions
short_description: list of subscribe share name exceptions on an acl profile
description:
- "Configure a list of Subscription Share Name Exception objects on an ACL Profile in a single transaction."
- "Allows addition and removal of a list of Subscription Share Name Exception objects as well as replacement of all existing Subscription Share Name Exception objects on an ACL Profile."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates Subscription Share Name Exception object list."
- "Reports which topics were added, deleted and omitted (duplicates). In case of an error, reports the invalid Subscription Share Name Exception object."
- "To delete all Subscription Share Name Exception objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfileSubscribeShareNameException"
options:
  names:
    description: The share name topic. Maps to 'subscribeShareNameException' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics]
    elements: str
  acl_profile_name:
    description: The ACL Profile. Maps to 'aclProfileName' in the SEMP v2 API.
    required: true
    type: str
  topic_syntax:
    description: The topic syntax. Maps to 'subscribeShareNameExceptionSyntax' in the SEMP v2 API.
    required: false
    default: "smf"
    type: str
    choices:
      - smf
      - mqtt
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace_acl_profile
- module: solace_acl_subscribe_share_name_exception
- module: solace_get_acl_subscribe_share_name_exceptions
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
    solace_acl_subscribe_share_name_exceptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_get_acl_subscribe_share_name_exceptions:
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
      solace_acl_subscribe_share_name_exceptions:
        acl_profile_name: foo
        topics:
          - topic_1
          - topic_2
        state: present

    - name: get list of exceptions
      solace_get_acl_subscribe_share_name_exceptions:
        acl_profile_name: foo

    - name: add second list of exceptions
      solace_acl_subscribe_share_name_exceptions:
        acl_profile_name: foo
        topics:
          - topic_3
          - topic_4
        state: present

    - name: get list of exceptions
      solace_get_acl_subscribe_share_name_exceptions:
        acl_profile_name: foo

    - name: replace list of exceptions
      solace_acl_subscribe_share_name_exceptions:
        acl_profile_name: foo
        topics:
          - new_topic_1
          - new_topic_2
        state: exactly

    - name: get list of exceptions
      solace_get_acl_subscribe_share_name_exceptions:
        acl_profile_name: foo

    - name: delete all exceptions
      solace_acl_subscribe_share_name_exceptions:
        acl_profile_name: foo
        topics: null
        state: exactly

    - name: get list of exceptions
      solace_get_acl_subscribe_share_name_exceptions:
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


class SolaceACLSubscribeShareNameExceptionsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'subscribeShareNameException'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeShareNameExceptions
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'aclProfiles', params['acl_profile_name'], 'subscribeShareNameExceptions']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], params['acl_profile_name'], params['topic_syntax'], object_key]

    def create_func(self, vpn_name, acl_profile_name, topic_syntax, topic, settings=None):
        # POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeShareNameExceptions
        data = {
            'msgVpnName': vpn_name,
            'aclProfileName': acl_profile_name,
            'subscribeShareNameExceptionSyntax': topic_syntax,
            self.OBJECT_KEY: topic
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name,
                      'aclProfiles', acl_profile_name, 'subscribeShareNameExceptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, acl_profile_name, topic_syntax, topic):
        # DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeShareNameExceptions/{subscribeShareNameExceptionSyntax},{subscribeShareNameException}
        ex_uri = ','.join([topic_syntax, topic])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name,
                      'aclProfiles', acl_profile_name,
                      'subscribeShareNameExceptions', ex_uri]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        acl_profile_name=dict(type='str', required=True),
        topic_syntax=dict(type='str', default='smf', choices=['smf', 'mqtt']),
        names=dict(type='list',
                   required=True,
                   aliases=['topics'],
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

    solace_task = SolaceACLSubscribeShareNameExceptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
