#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Solace Corporation, Ulrich Herbst, <ulrich.herbst@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_get_queue_templates
short_description: get list of queue-templates
description:
- "Get a list of Queue-template objects."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/software-broker/config/index.html#/queueTemplate/getMsgVpnQueueTemplates"
- "Module Sempv2 Monitor: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/queueTemmplate/getMsgVpnQueueTemplates"
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
seealso:
- module: solace_queue_template
author:
- Ulrich Herbst (@uherbstsolace)
'''

EXAMPLES = '''
  name: queue template example
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace.pubsub_plus.solace_queue_template:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace.pubsub_plus.solace_get_queue_templates:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"

  tasks:

  - name: create a queue template
    solace_queue_template:
      name: foo
      settings:
        accessType: non-exclusive
        maxMsgSpoolUsage: 1
        maxRedeliveryCount: 10
        maxTtl: 10
        respectTtlEnabled: true
        queueNameFilter: "foo/bar/>"
      state: present

  - name: update the queue template
    solace_queue_template:
      name: foo
      settings:
        accessType: exclusive
      state: present

  - name: get queue templates (config)
    solace_get_queue_templates:
      api: config
      query_params:
        where:
          - "queueTemplateName==foo"
    register: result

  - name: get queue templates (monitor)
    solace_get_queue_templates:
      api: monitor
      query_params:
        where:
          - "queueTemplateName==foo"
    register: result

  - name: delete queue template
    solace_queue_template:
      name: foo
      state: absent

'''

RETURN = '''
result_list:
  description: The list of objects found containing requested fields. Payload depends on API called.
  returned: success
  type: list
  elements: dict
result_list_count:
  description: Number of items in result_list.
  returned: success
  type: int
rc:
  description: Return code. rc=0 on success, rc=1 on error.
  type: int
  returned: always
  sample:
    success:
      rc: 0
    error:
      rc: 1
msg:
  description: The response from the HTTP call in case of error.
  type: dict
  returned: error
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible.module_utils.basic import AnsibleModule


class SolaceGetQueueTemplatesTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def get_monitor_api_base(self) -> str:
        return SolaceSempV2Api.API_BASE_SEMPV2_PRIVATE_MONITOR

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/queueTemplates
        # __private_monitor__
        return ['msgVpns', params['msg_vpn'], 'queueTemplates']


def run_module():
    module_args = {}
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceGetQueueTemplatesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
