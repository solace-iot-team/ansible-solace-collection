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

short_description: trusted common name for rest consumer

description:
  - "Allows addition, removal and configuration of trusted common name objects for a rest consumer of an RDP."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonNames."

seealso:
- module: solace_rdp_rest_consumer

options:
  name:
    description: The expected trusted common name of the remote certificate. Maps to 'tlsTrustedCommonName' in the API.
    required: true
    type: str
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
  - name: Create RDP
    solace_rdp:
      name: "rdp"
      state: present

  - name: Create RDP RestConsumer
    solace_rdp_restConsumer:
      name: "rest-consumer"
      rdp_name: "rdp"
      settings:
        remoteHost: "{{ host }}"
        remotePort: "{{ port }}"
      state: present

  - name: Add the TLS Trusted Common Name
    solace_rdp_restConsumer_trusted_cn:
      rdp_name: "rdp"
      rest_consumer_name: "rest-consumer"
      name: "cn"
      state: present
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceRdpRestConsumerTrustedCommonNameTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'tlsTrustedCommonName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['rdp_name'], self.module.params['rest_consumer_name']]

    def get_func(self, solace_config, vpn, rdp_name, rest_consumer_name, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_REST_CONSUMERS, rest_consumer_name, su.RDP_TLS_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, rdp_name, rest_consumer_name, name, settings=None):
        # POST /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames
        defaults = {}
        mandatory = {
            'msgVpnName': vpn,
            'restConsumerName': rest_consumer_name,
            'restDeliveryPointName': rdp_name,
            'tlsTrustedCommonName': name
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_REST_CONSUMERS, rest_consumer_name, su.RDP_TLS_TRUSTED_COMMON_NAMES]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, rdp_name, rest_consumer_name, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_REST_CONSUMERS, rest_consumer_name, su.RDP_TLS_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    module_args = dict(
        rdp_name=dict(type='str', required=True),
        rest_consumer_name=dict(type='str', required=True),
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceRdpRestConsumerTrustedCommonNameTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
