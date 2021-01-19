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
module: solace_get_topic_endpoints

TODO: rework doc

short_description: get list of queues

description:
- "Get a list of Queue objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue/getMsgVpnQueues)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/queue/getMsgVpnQueues)"

seealso:
- module: solace_queue

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list

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
  solace_get_queues:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Create Queue
    solace_queue:
      name: foo
      state: present

  - name: Get queues
    solace_get_queues:
      api: config
      query_params:
        where:
          - "queueName==foo*"
      select:
          - "queueName"
          - "eventMsgSpoolUsageThreshold"
    register: result

  - name: Result Config API
    debug:
        msg:
          - "{{ result.result_list }}"
          - "{{ result.result_list_count }}"

  - name: Get queues
    solace_get_queues:
      api: monitor
      query_params:
        where:
          - "queueName==foo*"
      select:
          - "queueName"
          - "eventMsgSpoolUsageThreshold"
    register: result

  - name: Result Monitor API
    debug:
        msg:
          - "{{ result.result_list }}"
          - "{{ result.result_list_count }}"

'''

RETURN = '''
result_list:
    description: The list of objects found containing requested fields. Results differ based on the api called.
    returned: success
    type: list
    elements: dict
    sample:
        config_api:
            result_list:
              - eventMsgSpoolUsageThreshold:
                    clearPercent: 50
                    setPercent: 60
                queueName: foo
        monitor_api:
            result_list:
              - accessType: exclusive
                alreadyBoundBindFailureCount: 0
                averageRxByteRate: 0
                averageRxMsgRate: 0
                averageTxByteRate: 0
                averageTxMsgRate: 0
                bindRequestCount: 0
                bindSuccessCount: 0
                bindTimeForwardingMode: store-and-forward
                clientProfileDeniedDiscardedMsgCount: 0
                consumerAckPropagationEnabled: true
                createdByManagement: true
                deadMsgQueue: "#DEAD_MSG_QUEUE"
                deletedMsgCount: 0
                destinationGroupErrorDiscardedMsgCount: 0
                disabledBindFailureCount: 0
                disabledDiscardedMsgCount: 0
                durable: true
                egressEnabled: true
                eventBindCountThreshold:
                    clearPercent: 60
                    setPercent: 80

result_list_count:
    description: Number of items in result_list.
    returned: success
    type: int
    sample:
        result_list_count: 2
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetQueuesTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/topicEndpoints
        return ['msgVpns', params['msg_vpn'], 'topicEndpoints']
        

def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGetQueuesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
