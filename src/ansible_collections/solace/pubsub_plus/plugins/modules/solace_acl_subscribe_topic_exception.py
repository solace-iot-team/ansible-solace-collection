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
module: solace_acl_subscribe_topic_exception
short_description: subscribe topic exception for acl profile
description:
- "Configure a subscribe topic exception object for an ACL Profile."
- "Allows addition and removal of a subscribe topic exception object for an ACL Profile."
- "Reference (>=2.14): https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfileSubscribeTopicException."
- "Reference (<=2.13): https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfileSubscribeException."
options:
  name:
    description: The name (topic) of the subscribe topic exception. Maps to 'subscribeTopicException' in the SEMP v2 API.
    required: true
    type: str
  acl_profile_name:
    description: The ACL Profile.
    required: true
    type: str
  topic_syntax:
    description: The topic syntax.
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
- solace.pubsub_plus.solace.settings
seealso:
- module: solace_acl_profile
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
  solace_acl_subscribe_topic_exception:
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
        subscribeTopicDefaultAction: "disallow"
      state: present

  - name: Add Subscribe Topic Exceptions to ACL Profile
    solace_acl_subscribe_topic_exception:
      acl_profile_name: foo
      name: "test/ansible/solace"
      state: present

  - name: Delete Subscribe Topic Exceptions from ACL Profile
    solace_acl_subscribe_topic_exception:
      acl_profile_name: foo
      name: "test/ansible/solace"
      state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
    sample:
        aclProfileName: test_ansible_solace
        msgVpnName: default
        subscribeTopicException: test/ansible/solace
        subscribeTopicExceptionSyntax: smf
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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError
from ansible.module_utils.basic import AnsibleModule


class SolaceACLSubscribeTopicExceptionTask(SolaceBrokerCRUDTask):

    SEMP_VERSION_KEY_MAP = {
        '<=2.13': {
            'OBJECT_KEY': 'subscribeExceptionTopic',
            'URI_SUBSCR_EX': 'subscribeExceptions',
            'TOPIC_SYNTAX': 'topicSyntax'
        },
        '>=2.14': {
            'OBJECT_KEY': 'subscribeTopicException',
            'URI_SUBSCR_EX': 'subscribeTopicExceptions',
            'TOPIC_SYNTAX': 'subscribeTopicExceptionSyntax'
        }
    }

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['acl_profile_name'], params['topic_syntax'], params['name']]

    def get_sempv2_version_map_key(self, semp_version: float) -> str:
        if semp_version <= 2.13:
            return '<=2.13'
        elif semp_version >= 2.14:
            return '>=2.14'
        raise SolaceInternalError(f"sempv2_version: {semp_version} not supported")

    def get_func(self, vpn_name, acl_profile_name, topic_syntax, subscribe_topic_exception):
        # sempVersion <= "2.13" : GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeExceptions/{topicSyntax},{subscribeExceptionTopic}
        # sempVersion >= "2.14": GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions/{subscribeTopicExceptionSyntax},{subscribeTopicException}
        sempv2_version_float = self.get_sempv2_version_as_float()
        sempv2_version_map_key = self.get_sempv2_version_map_key(sempv2_version_float)

        uri_subscr_ex = self.SEMP_VERSION_KEY_MAP[sempv2_version_map_key]['URI_SUBSCR_EX']

        ex_uri = ','.join([topic_syntax, subscribe_topic_exception])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'aclProfiles', acl_profile_name, uri_subscr_ex, ex_uri]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, acl_profile_name, topic_syntax, subscribe_topic_exception, settings=None):
        # sempVersion: <=2.13 : POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeExceptions
        # sempVersion: >=2.14: POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions
        sempv2_version_float = self.get_sempv2_version_as_float()
        sempv2_version_map_key = self.get_sempv2_version_map_key(sempv2_version_float)
        data = {
            'msgVpnName': vpn_name,
            'aclProfileName': acl_profile_name,
            self.SEMP_VERSION_KEY_MAP[sempv2_version_map_key]['TOPIC_SYNTAX']: topic_syntax,
            self.SEMP_VERSION_KEY_MAP[sempv2_version_map_key]['OBJECT_KEY']: subscribe_topic_exception
        }
        data.update(settings if settings else {})
        uri_subscr_ex = self.SEMP_VERSION_KEY_MAP[sempv2_version_map_key]['URI_SUBSCR_EX']
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'aclProfiles', acl_profile_name, uri_subscr_ex]
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, acl_profile_name, topic_syntax, subscribe_topic_exception):
        # sempVersion: <=2.13 : DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeExceptions/{topicSyntax},{subscribeExceptionTopic}
        # sempVersion: >=2.14: DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions/{subscribeTopicExceptionSyntax},{subscribeTopicException}
        sempv2_version_float = self.get_sempv2_version_as_float()
        sempv2_version_map_key = self.get_sempv2_version_map_key(sempv2_version_float)

        uri_subscr_ex = self.SEMP_VERSION_KEY_MAP[sempv2_version_map_key]['URI_SUBSCR_EX']
        ex_uri = ','.join([topic_syntax, subscribe_topic_exception])

        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'aclProfiles', acl_profile_name, uri_subscr_ex, ex_uri]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        acl_profile_name=dict(type='str', required=True),
        topic_syntax=dict(type='str', default='smf', choices=['smf', 'mqtt'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceACLSubscribeTopicExceptionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
