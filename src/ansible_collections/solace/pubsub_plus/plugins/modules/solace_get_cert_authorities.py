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
module: solace_get_cert_authorities
TODO: rework doc

short_description: get client profiles

description:
- "Get a list of Client Profile objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile/getMsgVpnClientProfiles)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/clientProfile/getMsgVpnClientProfiles)."

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list

seealso:
- module: solace_client_profile

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
  solace_client_profile:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
    solace_cloud_api_token: "{{ solace_cloud_api_token | default(omit) }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
  solace_get_client_profiles:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: create client profile
    solace_client_profile:
      name: "ansible-solace__test_1"
      state: present

  - name: get list - config
    solace_get_client_profiles:
      api: config
      query_params:
        where:
          - "clientProfileName==ansible-solace__test*"
    register: result
  - debug:
      msg:
        - "{{ result.result_list }}"
        - "{{ result.result_list_count }}"

  - name: get list - monitor
    solace_get_client_profiles:
      api: monitor
      query_params:
        where:
          - "clientProfileName==ansible-solace__test*"
    register: result
  - debug:
      msg:
        - "{{ result.result_list }}"
        - "{{ result.result_list_count }}"

  - name: remove client profile
    solace_client_profile:
      name: "ansible-solace__test_1"
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
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


# TODO:
# solace_cloud:
# - get_service ==> list of cert authority names
# - for each: get certauthrity

class SolaceGetCertAuthoritiesTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def do_task(self):
        # GET /certAuthorities
        path_array = ['certAuthorities']
        api = self.get_config().get_params()['api']
        query_params = self.get_config().get_params()['query_params']
        objects = self.get_sempv2_get_paging_api().get_objects(self.get_config(), api, path_array, query_params)
        result = self.create_result_with_list(objects)
        return None, result


def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGetCertAuthoritiesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
