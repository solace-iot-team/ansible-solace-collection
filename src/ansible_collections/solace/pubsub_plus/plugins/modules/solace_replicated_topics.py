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
module: solace_replicated_topics
short_description: list of replicated topics on a MessageVpn's replication
description:
- "Configure a list of replicatedTopics object on a MessageVpn in a single transaction."
- "Allows addition and removal of a list of topics as well as replacement of all existing topics on a MessageVpn's replication."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates topics list."
- "Reports which topics were added, deleted and omitted (duplicates). In case of an error, reports the invalid replicated topics."
- "To delete all replicated topics objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/replicatedTopic"
options:
  names:
    description: Maps to 'replicatedTopic' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics, replicated_topics]
    elements: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace_get_replicated_topics
- module: solace_replicated_topic
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
    solace_replicated_topics:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
  tasks:
  - name: add list of replicated topics
    solace_replicated_topics:
      topics:
        - topic-1
        - topic-2
      state: present

  - name: replace replicated topics
    solace_replicated_topics:
      topics:
        - new-topic-1
        - new-topic-2
      state: exactly

  - name: delete all replicated topics
    solace_replicated_topics:
      replicated_topics: []
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


class SolaceReplicatedTopicsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'replicatedTopic'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/replicatedTopics
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'replicatedTopics']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], object_key]

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
        names=dict(type='list',
                   required=True,
                   aliases=['topics', 'replicated_topics'],
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

    solace_task = SolaceReplicatedTopicsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
