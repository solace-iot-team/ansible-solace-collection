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
module: solace_get_queue_subscriptions
TODO: rework docs
short_description: get list of rdps

description:
- "Get a list of Rest Delivery Point objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPoints)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPoints)"

seealso:
- module: solace_rdp

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
  solace_rdp:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
  solace_get_rdps:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Create RDP - Disabled
    solace_rdp:
      name: "rdp-test-ansible-solace"
      settings:
        enabled: false
      state: present

  - name: Get List of RDPs - Config
    solace_get_rdps:
      query_params:
        where:
          - "restDeliveryPointName==rdp-test-ansible*"

    register: result

  - name: Result Config API
    debug:
      msg:
        - "{{ result.result_list }}"
        - "{{ result.result_list_count }}"

  - name: Get List of RDPs - Monitor
    solace_get_rdps:
      api: monitor
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
              - clientProfileName: default
                enabled: false
                msgVpnName: default
                restDeliveryPointName: rdp-test-ansible-solace
        monitor_api:
            result_list:
              - clientName: #rdp/rdp-test-ansible-solace
                clientProfileName: default
                enabled: false
                lastFailureReason: RDP Shutdown
                lastFailureTime: 1609233281
                msgVpnName: default
                restDeliveryPointName: rdp-test-ansible-solace
                timeConnectionsBlocked: 0
                up: false
result_list_count:
    description: Number of items in result_list.
    returned: success
    type: int
    sample:
        result_list_count: 1
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetQueueSubscriptionsTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions
        return ['msgVpns', params['msg_vpn'], 'queues', params['queue_name'], 'subscriptions']


def run_module():
    module_args = dict(
        queue_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGetQueueSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
