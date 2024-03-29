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
module: solace_acl_publish_topic_exception
short_description: publish topic exception for acl profile
description:
- "Configure a publish topic exception object for an ACL Profile."
- "Allows addition and removal of a publish topic exception object for an ACL Profile."
notes:
- "Module Sempv2 Config (>=2.14): https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfilePublishTopicException"
- "Module Sempv2 Config (<=2.13): https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfilePublishException"
options:
  name:
    description: The name (topic) of the publish topic exception. Maps to 'publishTopicException' in the SEMP v2 API.
    required: true
    type: str
    aliases: [topic]
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
- solace.pubsub_plus.solace.sempv2_settings
seealso:
- module: solace_acl_profile
- module: solace_acl_publish_topic_exceptions
- module: solace_get_acl_publish_topic_exceptions
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
 solace_acl_publish_topic_exception:
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
        name: "test_ansible_solace"
        settings:
            clientConnectDefaultAction: "disallow"
            publishTopicDefaultAction: "disallow"
            subscribeTopicDefaultAction: "disallow"
        state: present

  - name: Add Publish Topic Exceptions to ACL Profile
    solace_acl_publish_topic_exception:
        acl_profile_name: "test_ansible_solace"
        name: "test/ansible/solace"
        state: present

  - name: Delete Publish Topic Exceptions from ACL Profile
    solace_acl_publish_topic_exception:
        acl_profile_name: "test_ansible_solace"
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
        publishTopicException: test/ansible/solace
        publishTopicExceptionSyntax: smf
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError, SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceACLPublishTopicExceptionTask(SolaceBrokerCRUDTask):

    SEMP_VERSION_KEY_MAP = {
        '<=2.13': {
            'OBJECT_KEY': 'publishExceptionTopic',
            'URI_SUBSCR_EX': 'publishExceptions',
            'TOPIC_SYNTAX': 'topicSyntax'
        },
        '>=2.14': {
            'OBJECT_KEY': 'publishTopicException',
            'URI_SUBSCR_EX': 'publishTopicExceptions',
            'TOPIC_SYNTAX': 'publishTopicExceptionSyntax'
        }
    }

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        _raw_api_version, self.sempv2_version = self.sempv2_api.get_sempv2_version(
            self.get_config())
        self.sempv2_version_map_key = self.get_sempv2_version_map_key(
            self.sempv2_version)

    def validate_params(self):
        topic = self.get_module().params['name']
        if SolaceUtils.doesStringContainAnyWhitespaces(topic):
            raise SolaceParamsValidationError('topic',
                                              topic, "must not contain any whitespace")
        return super().validate_params()

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['acl_profile_name'], params['topic_syntax'], params['name']]

    def get_sempv2_version_map_key(self, semp_version: float) -> str:
        if semp_version <= SolaceUtils.create_version("2.13"):
            return '<=2.13'
        elif semp_version >= SolaceUtils.create_version("2.14"):
            return '>=2.14'
        raise SolaceInternalError(
            f"sempv2_version: {semp_version} not supported")

    def get_func(self, vpn_name, acl_profile_name, topic_syntax, publish_topic_exception):
        # sempVersion <= "2.13" : GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishExceptions/{topicSyntax},{publishExceptionTopic}
        # sempVersion >= "2.14": GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishTopicExceptions/{publishTopicExceptionSyntax},{publishTopicException}
        uri_subscr_ex = self.SEMP_VERSION_KEY_MAP[self.sempv2_version_map_key]['URI_SUBSCR_EX']
        ex_uri = ','.join([topic_syntax, publish_topic_exception])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'aclProfiles', acl_profile_name, uri_subscr_ex, ex_uri]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, acl_profile_name, topic_syntax, publish_topic_exception, settings=None):
        # sempVersion: <=2.13 : POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishExceptions
        # sempVersion: >=2.14: POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishTopicExceptions
        data = {
            'msgVpnName': vpn_name,
            'aclProfileName': acl_profile_name,
            self.SEMP_VERSION_KEY_MAP[self.sempv2_version_map_key]['TOPIC_SYNTAX']: topic_syntax,
            self.SEMP_VERSION_KEY_MAP[self.sempv2_version_map_key]['OBJECT_KEY']: publish_topic_exception
        }
        data.update(settings if settings else {})
        uri_subscr_ex = self.SEMP_VERSION_KEY_MAP[self.sempv2_version_map_key]['URI_SUBSCR_EX']
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'aclProfiles', acl_profile_name, uri_subscr_ex]
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, acl_profile_name, topic_syntax, publish_topic_exception):
        # sempVersion: <=2.13 : DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishExceptions/{topicSyntax},{publishExceptionTopic}
        # sempVersion: >=2.14: DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishTopicExceptions/{publishTopicExceptionSyntax},{publishTopicException}
        uri_subscr_ex = self.SEMP_VERSION_KEY_MAP[self.sempv2_version_map_key]['URI_SUBSCR_EX']
        ex_uri = ','.join([topic_syntax, publish_topic_exception])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'aclProfiles', acl_profile_name, uri_subscr_ex, ex_uri]
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

    solace_task = SolaceACLPublishTopicExceptionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
