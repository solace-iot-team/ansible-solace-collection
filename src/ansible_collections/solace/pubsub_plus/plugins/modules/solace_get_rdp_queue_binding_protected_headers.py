#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_get_rdp_queue_binding_protected_headers
short_description: get list of protected headers on rdp queue binding
description:
- "Get a list of Protected Headers on a Queue Binding object on a Rest Delivery Point object."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/software-broker/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointQueueBindingProtectedRequestHeaders"
- "Module Sempv2 Monitor: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/software-broker/monitor/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointQueueBindingProtectedRequestHeaders"
options:
  rdp_name:
    description: The name of the Rest Delivery Point. Maps to 'restDeliveryPointName' in the API.
    type: str
    required: true
  queue_name:
    description: The name of the Queue Binding. Maps to 'queueBindingName' in the API.
    type: str
    required: true
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
seealso:
- module: solace_rdp
- module: solace_queue
- module: solace_rdp_queue_binding
- module: solace_rdp_queue_binding_protected_header
- module: solace_get_rdp_queue_binding_headers
- module: solace_get_rdp_queue_binding_protected_headers
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
    - name: "Create protected header"
      solace_rdp_queue_binding_protected_header:
        rdp_name: "rdp-test-ansible-solace"
        queue_name: "rdp-test-ansible-solace"
        header_name: "protected-header"
        settings:
          headerValue: 'protected header value'
        state: present

    - name: "list protected headers: config"
      solace_get_rdp_queue_binding_protected_headers:
        rdp_name: "rdp-test-ansible-solace"
        queue_name: "rdp-test-ansible-solace"
        query_params:
          where:
            - "headerName==protected*"

    - name: "list protected headers: monitor"
      solace_get_rdp_queue_binding_protected_headers:
        rdp_name: "rdp-test-ansible-solace"
        queue_name: "rdp-test-ansible-solace"
        api: monitor
        query_params:
          where:
            - "headerName==protected*"

    - name: "remove protected header"
      solace_rdp_queue_binding_protected_header:
        rdp_name: "rdp-test-ansible-solace"
        queue_name: "rdp-test-ansible-solace"
        header_name: "protected-header"
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
from ansible.module_utils.basic import AnsibleModule


class SolaceGetRdpQueueBindingProtectedHeadersTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}/protectedRequestHeaders
        return ['msgVpns', params['msg_vpn'], 'restDeliveryPoints', params['rdp_name'], 'queueBindings', params['queue_name'], 'protectedRequestHeaders']


def run_module():
    module_args = dict(
        rdp_name=dict(type='str', required=True),
        queue_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceGetRdpQueueBindingProtectedHeadersTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
