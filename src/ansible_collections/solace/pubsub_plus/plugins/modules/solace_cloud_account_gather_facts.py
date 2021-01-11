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
module: solace_cloud_account_gather_facts

TODO: re-work documentation

short_description: Facts from all services in Solace Cloud Account.

description: >
  Retrieves service info (facts) about all services available in the Solace Cloud Account.
  Stores the facts in: ['ansible_facts']['solace_cloud_accounts'][{service-name}].
  Use to retrieve the SEMP endpoints for a Solace Cloud service as inputs for other modules.

seealso:
  - module: solace_cloud_get_facts
  - module: solace_get_facts

notes:
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm)."

options:
    account_name:
        description:
            - The host specified in the inventory. Represents the Solace Cloud Account.
            - "Note: Only used internally in the playbooks, so you can choose whichever name makes sense in your case."
        required: true
        type: str
        aliases:
            - name
    return_format:
        description:
            - The format of the returned JSON. Either as a JSON object or a JSON array.
            - "Note: Use 'dict' when you want to access the facts in a playbook by account_name (i.e. 'inventory_hostname') directly."
            - "Note: Use 'list' when you want to iterate over each service in your playbook."
        required: true
        type: str
        choices:
            - dict
            - list

extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_service_config

author: Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
- name: "Solace Cloud Account: Gather Facts as Dict"
  solace_cloud_account_gather_facts:
    api_token: "{{ api_token_all_permissions }}"
    account_name: "{{ inventory_hostname }}"
    return_format: dict
  register: sca_facts_dict_result

- name: "Save Facts Dict: Solace Cloud Account"
  local_action:
    module: copy
    content: "{{ sca_facts_dict_result | to_nice_json }}"
    dest: "./tmp/facts.dict.solace_cloud_account.{{ inventory_hostname }}.json"

- name: "Set Fact as Dict: Solace Cloud Account Services"
  set_fact:
    sca_services_dict_facts: "{{ sca_facts_dict_result.ansible_facts.solace_cloud_accounts[inventory_hostname].services }}"
  no_log: true

- name: "Solace Cloud Account: Gather Facts as List"
  solace_cloud_account_gather_facts:
    api_token: "{{ api_token_all_permissions }}"
    account_name: "{{ inventory_hostname }}"
    return_format: list
  register: sca_facts_list_result

- name: "Save Facts List: Solace Cloud Account"
  local_action:
    module: copy
    content: "{{ sca_facts_list_result | to_nice_json }}"
    dest: "./tmp/facts.list.solace_cloud_account.{{ inventory_hostname }}.json"

- name: "Set Fact: Solace Cloud Account Services"
  set_fact:
    sca_services_list_facts: "{{ sca_facts_list_result.ansible_facts.solace_cloud_accounts[inventory_hostname].services }}"
  no_log: true

- name: "Loop: Get Service for all Services By serviceId"
  solace_cloud_get_service:
    api_token: "{{ api_token_all_permissions }}"
    service_id: "{{ sc_service.serviceId }}"
  loop: "{{ sca_services_list_facts }}"
  loop_control:
    loop_var: sc_service
    index_var: sc_service_i
    label: "[by serviceId] Service: name={{ sc_service.name }}, id={{ sc_service.serviceId }}"


'''

RETURN = '''
    rc:
        description: return code, either 0 (ok), 1 (not ok)
        type: int
        returned: always
        sample:
            rc: 0
    msg:
        description: error message if not ok
        type: str
        returned: error
    
    response: - not correct
        description: The response from the GET {serviceId} call. Differs depending on state of service.
        type: dict
        returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError, SolaceInternalError
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudAccountGatherFactsTask(SolaceCloudGetTask):

    def __init__(self, module):
        super().__init__(module)

    def validate_params(self):
        return

    def do_task(self):
        self.validate_params()
        account_name = self.get_module().params['account_name']
        return_format = self.module.params['return_format']
        facts = dict()
        if return_format == 'dict':
            facts = dict(
                data_centers=dict(),
                services=dict()
            )
        elif return_format == 'list':
            facts = dict(
                data_centers=[],
                services=[]
            )
        else:
            raise SolaceInternalError(f"arg 'return_format={return_format}' invalid")

        services = self.get_solace_cloud_api().get_services_with_details(self.get_config())
        data_centers = self.get_solace_cloud_api().get_data_centers(self.get_config())
        
        if return_format == 'dict':
            for service in services:
                    name = service['name']
                    facts['services'][name] = service
            for data_center in data_centers:
                    id = data_center['id']
                    facts['data_centers'][id] = data_center
        else:
            facts['services'] = services
            facts['data_centers'] = data_centers

        result = self.create_result()
        result.update(dict(
            solace_cloud_account = { account_name: facts }
        ))
        return None, result


def run_module():
    module_args = dict(
        account_name=dict(type='str', required=True, aliases=['name']),
        return_format=dict(type='str', required=True, choices=['dict', 'list'])
    )
    arg_spec = SolaceTaskSolaceCloudConfig.arg_spec_solace_cloud()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceCloudAccountGatherFactsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
