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
module: solace_jndi_topics
short_description: manage a list of jndi topics
description:
- "Configure a list of JNDI Topic objects in a single transaction."
- "Allows addition and removal of a list of JNDI Topic objects as well as replacement of all existing JNDI Topic objects."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates JNDI Topic object list."
- "Reports which topics were added, deleted and omitted (duplicates). In case of an error, reports the invalid JNDI Topic object."
- "To delete all JNDI Topic objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/jndi/createMsgVpnJndiTopic"
options:
  names:
    description: The JNDI topic. Maps to 'topicName' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics, jndi_topics]
    elements: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace_jndi_topic
- module: solace_get_jndi_topics
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
    solace_jndi_topics:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
  - name: add
    solace_jndi_topics:
      names:
      - bar_1
      - bar_2
      - bar_3
      settings:
        physicalName: foo
      state: present

  - name: replace old list with new list
    solace_jndi_topics:
      names:
      - bar_2
      - bar_3
      - bar_4
      settings:
        physicalName: foo
      state: exactly

  - name: delete one
    solace_jndi_topics:
      names:
      - bar_2
      state: absent

  - name: delete all
    solace_jndi_topics:
      names: null
      state: exactly
'''

RETURN = '''
response:
    description: The response of the operation.
    type: dict
    returned: always
    sample:
      success:
        response:
          -   added: topic-1
          -   added: topic-2
          -   added: duplicate-topic
          -   deleted: topic-3
          -   deleted: topic-4
          -   duplicate: duplicate-topic
      error:
        response:
          -   error: "{the invalid jndi topic name (could be an invalid physicalName)...}"
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


class SolaceJNDITopicsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'topicName'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/jndiTopics
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'jndiTopics']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], object_key]

    def create_func(self, vpn_name, jndi_topic_name, settings=None):
        # POST /msgVpns/{msgVpnName}/jndiTopics
        data = {
            self.OBJECT_KEY: jndi_topic_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns',
                      vpn_name,
                      'jndiTopics']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, jndi_topic_name):
        # DELETE /msgVpns/{msgVpnName}/jndiTopics/{topicName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'jndiTopics', jndi_topic_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        names=dict(type='list',
                   required=True,
                   aliases=['jndi_topics', 'topics'],
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

    solace_task = SolaceJNDITopicsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
