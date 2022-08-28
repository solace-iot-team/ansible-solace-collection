#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Solace Corporation, Paulus Gunadi, <paulus.gunadi@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_replicated_topic
short_description: replicated topic on a MessageVpn's replication
description:
- "Configure a replicatedTopic object on a MessageVpn. Allows addition, removal and configuration of replicatedTopic objects on a MessageVpn."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/replicatedTopic"
options:
  name:
    description: The replicated topic. Maps to 'replicatedTopic' in the API.
    required: true
    type: str
    aliases: [topic, replicated_topic]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_get_replicated_topics
- module: solace_replicated_topics
author:
- Paulus Gunadi (@pjgunadi)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
    solace_replicated_topic:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
tasks:
- name: add vpn replicated topic
  solace_replicated_topic:
    topic: "foo/bar"
    state: present

- name: remove vpn replicated topic
  solace_replicated_topic:
    topic: "foo/bar"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceReplicatedTopicTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'replicatedTopic'

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
        return [params['msg_vpn'], params['name']]

    def get_func(self, vpn_name, replicated_topic):
        # GET /msgVpns/{msgVpnName}/replicatedTopics/{replicatedTopic}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'replicatedTopics', replicated_topic]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, replicated_topic, settings=None):
        # POST /msgVpns/{msgVpnName}/replicatedTopics
        data = {
            self.OBJECT_KEY: replicated_topic
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'replicatedTopics']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, replicated_topic):
        # DELETE /msgVpns/{msgVpnName}/replicatedTopics/{replicatedTopic}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'replicatedTopics', replicated_topic]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=[
                  'topic', 'replicated_topic'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceReplicatedTopicTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
