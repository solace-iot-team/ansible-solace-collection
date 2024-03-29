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
module: solace_queue_start_replay
short_description: start replay on queue
description:
- "Start replay on a Queue object."
notes:
- "Module Sempv2 Action: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/action/index.html#/queue/doMsgVpnQueueStartReplay"
options:
  queue_name:
    description: Name of the queue. Maps to 'queueName' in the API.
    required: true
    type: str
    aliases: [queue]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
seealso:
- module: solace_queue
- module: solace_queue_cancel_replay
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
    solace_queue:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace_queue_subscription:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace_queue_start_replay:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace_queue_cancel_replay:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
tasks:
- name: create queue
  solace_queue:
    name: bar
    state: present

- name: add queue subscription
  solace_queue_subscription:
    name: "hello/world"
    queue_name: bar
    state: present

- name: start replay
  solace_queue_start_replay:
    queue_name: bar
    settings:
        fromTime: 1

- name: cancel replay
  solace_queue_cancel_replay:
    queue_name: bar
    settings:
        forceComplete: true
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerActionTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceQueueStartReplayTask(SolaceBrokerActionTask):

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['queue_name']]

    def do_task(self):
        args = self.get_args()
        result = self.create_result(rc=0, changed=True)
        result['response'] = self.put_func(*args)
        return None, result

    def put_func(self, vpn_name, queue_name, settings=None):
        # PUT /msgVpns/{msgVpnName}/queues/{queueName}/startReplay
        data = {
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_ACTION,
                      'msgVpns', vpn_name, 'queues', queue_name, 'startReplay']
        return self.sempv2_api.make_put_request(self.get_config(), path_array, data)


def run_module():
    module_args = dict(
        queue_name=dict(type='str', required=True, aliases=['queue'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_sempv2_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceQueueStartReplayTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
