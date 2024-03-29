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
module: solace_acl_subscribe_share_name_exception
short_description: subscribe share name exception for acl profile
description:
- "Configure Subscribe Share Name Exeption objects for an ACL Profile."
- "Allows addition and removal of Subscribe Share Name Exception objects for ACL Profiles."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/getMsgVpnAclProfileSubscribeShareNameExceptions"
options:
  name:
    description: Name of the subscribe share name exception topic. Maps to 'subscribeShareNameException' in the API.
    required: true
    type: str
    aliases: [topic]
  acl_profile_name:
    description: The ACL Profile.
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
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.sempv2_settings
seealso:
- module: solace_acl_profile
- module: solace_acl_subscribe_share_name_exceptions
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
  solace_acl_subscribe_share_name_exception:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Create ACL Profile
    solace_acl_profile:
      name: foo
      settings:
        subscribeShareNameDefaultAction: "disallow"
      state: present

  - name: Remove
    solace_acl_subscribe_share_name_exception:
      name: "bar"
      acl_profile_name: foo
      state: absent

  - name: Add
    solace_acl_subscribe_share_name_exception:
      name: "bar"
      acl_profile_name: foo
      state: present
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
    sample:
        aclProfileName: foo
        subscribeShareNameException: bar
        msgVpnName: default
        subscribeShareNameExceptionSyntax: smf
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceACLSubscribeShareNameExceptionTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'subscribeShareNameException'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def validate_params(self):
        topic = self.get_module().params['name']
        if SolaceUtils.doesStringContainAnyWhitespaces(topic):
            raise SolaceParamsValidationError('topic',
                                              topic, "must not contain any whitespace")
        return super().validate_params()

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['acl_profile_name'], params['topic_syntax'], params['name']]

    def get_func(self, vpn_name, acl_profile_name, topic_syntax, subscribe_share_name_exception):
        # GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeShareNameExceptions/{subscribeShareNameExceptionSyntax},{subscribeShareNameException}
        ex_uri = ','.join([topic_syntax, subscribe_share_name_exception])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'aclProfiles', acl_profile_name, 'subscribeShareNameExceptions', ex_uri]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, acl_profile_name, topic_syntax, subscribe_share_name_exception, settings=None):
        # POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeShareNameExceptions
        data = {
            'msgVpnName': vpn_name,
            'aclProfileName': acl_profile_name,
            self.OBJECT_KEY: subscribe_share_name_exception,
            'subscribeShareNameExceptionSyntax': topic_syntax
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'aclProfiles', acl_profile_name, 'subscribeShareNameExceptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, acl_profile_name, topic_syntax, subscribe_share_name_exception):
        # DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeShareNameExceptions/{subscribeShareNameExceptionSyntax},{subscribeShareNameException}
        ex_uri = ','.join([topic_syntax, subscribe_share_name_exception])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'aclProfiles', acl_profile_name, 'subscribeShareNameExceptions', ex_uri]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        acl_profile_name=dict(type='str', required=True),
        topic_syntax=dict(type='str', default='smf', choices=['smf', 'mqtt']),
        name=dict(type='str', required=True, aliases=['topic'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceACLSubscribeShareNameExceptionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
