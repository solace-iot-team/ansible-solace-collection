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
module: solace_rdp_rest_consumer_trusted_cn
short_description: trusted common name on rdp rest consumer
description:
- "Allows addition, removal and configuration of Trusted Common Name objects on a Rest Consumer object on a Rest Delivery Point object."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonNames"
options:
  name:
    description: The expected trusted common name of the remote certificate. Maps to 'tlsTrustedCommonName' in the API.
    required: true
    type: str
    aliases: [tls_trusted_common_name]
  rdp_name:
    description: The RDP name. Maps to 'restDeliveryPointName' in the API.
    required: true
    type: str
  rest_consumer_name:
    description: The Rest consumer name. Maps to 'restConsumerName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_rdp
- module: solace_rdp_rest_consumer
- module: solace_get_rdp_rest_consumer_trusted_cns
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
  solace_rdp_rest_consumer:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
  solace_rdp_rest_consumer_trusted_cn:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: create rdp
  solace_rdp:
    name: foo
    state: present

- name: create rdp rest consumer
  solace_rdp_rest_consumer:
    name: bar
    rdp_name: foo
    state: present

- name: add trusted common name
  solace_rdp_rest_consumer_trusted_cn:
    rdp_name: foo
    rest_consumer_name: bar
    name: "*.my.domain.com"
    state: present

- name: delete trusted common name
  solace_rdp_rest_consumer_trusted_cn:
    rdp_name: foo
    rest_consumer_name: bar
    name: "*.my.domain.com"
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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceRdpRestConsumerTrustedCommonNameTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'tlsTrustedCommonName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['rdp_name'], params['rest_consumer_name'], params['name']]

    def get_func(self, vpn_name, rdp_name, rest_consumer_name, tls_trusted_cn):
        # GET /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'restDeliveryPoints', rdp_name, 'restConsumers', rest_consumer_name, 'tlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, rdp_name, rest_consumer_name, tls_trusted_cn, settings=None):
        # POST /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames
        data = {
            'msgVpnName': vpn_name,
            'restDeliveryPointName': rdp_name,
            'restConsumerName': rest_consumer_name,
            self.OBJECT_KEY: tls_trusted_cn
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'restDeliveryPoints', rdp_name, 'restConsumers', rest_consumer_name, 'tlsTrustedCommonNames']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, rdp_name, rest_consumer_name, tls_trusted_cn):
        # DELETE /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'restDeliveryPoints', rdp_name, 'restConsumers', rest_consumer_name, 'tlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['tls_trusted_common_name']),
        rdp_name=dict(type='str', required=True),
        rest_consumer_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceRdpRestConsumerTrustedCommonNameTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
