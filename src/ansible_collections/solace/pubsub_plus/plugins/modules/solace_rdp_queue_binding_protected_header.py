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
module: solace_rdp_queue_binding_protected_header
short_description: protected header on queue bindining on rdp
description:
- "Allows addition, removal and configuration of Protected Header objects on a Queue Binding object for a Rest Delivery Point(RDP). "
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/software-broker/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointQueueBindingProtectedRequestHeader"
options:
  name:
    description: Name of the protected request header. Maps to 'headerName' in the API.
    required: true
    type: str
    aliases: [header_name]
  queue_name:
    description: Name of the queue. Maps to 'queueBindingName' in the API.
    required: true
    type: str
  rdp_name:
    description: Name of the RDP. Maps to 'restDeliveryPointName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_rdp
- module: solace_queue
- module: solace_rdp_queue_binding
- module: solace_rdp_queue_binding_header
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceRdpQueueBindingProtectedHeaderTask(SolaceBrokerCRUDTask):

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['rdp_name'], params['queue_name'], params['header_name']]

    def get_func(self, vpn_name, rdp_name, queue_name, header_name):
        # GET /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}/protectedRequestHeaders/{headerName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'restDeliveryPoints', rdp_name, 'queueBindings',
                      queue_name, 'protectedRequestHeaders', header_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, rdp_name, queue_name, header_name, settings=None):
        # POST /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}/protectedRequestHeaders
        data = {
            'msgVpnName': vpn_name,
            'restDeliveryPointName': rdp_name,
            'queueBindingName': queue_name,
            'headerName': header_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'restDeliveryPoints', rdp_name,
                      'queueBindings', queue_name,
                      'protectedRequestHeaders']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, rdp_name, queue_name, header_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}/protectedRequestHeaders/{headerName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'restDeliveryPoints', rdp_name,
                      'queueBindings', queue_name,
                      'protectedRequestHeaders', header_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, rdp_name, queue_name, header_name):
        # DELETE /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}/protectedRequestHeaders/{headerName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'restDeliveryPoints', rdp_name,
                      'queueBindings', queue_name,
                      'protectedRequestHeaders', header_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        rdp_name=dict(type='str', required=True),
        queue_name=dict(type='str', required=True),
        name=dict(type='str', required=True, aliases=[
                  'header_name'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceRdpQueueBindingProtectedHeaderTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
