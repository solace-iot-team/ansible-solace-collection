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
short_description: gather account services facts
description:
- "Retrieves service info (facts) about all services available in the Solace Cloud Account."
- "For example, use to retrieve the SEMP endpoints for a Solace Cloud service as inputs for other modules."
notes:
- "Module Solace Cloud API: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm"
seealso:
  - module: solace_cloud_get_facts
  - module: solace_get_facts
options:
  account_name:
    description:
      - The host specified in the inventory. Represents the Solace Cloud Account.
      - "Note: Only used internally in the playbooks, so you can choose whichever name makes sense in your case."
    required: true
    type: str
    aliases: [name]
  return_format:
    description:
      - The format of the returned JSON. Either as a JSON object or a JSON array.
      - "Note: Use 'dict' when you want to access the facts in a playbook by account_name (i.e. 'inventory_hostname') directly."
      - "Note: Use 'list' when you want to iterate over each service in your playbook."
    required: true
    type: str
    choices: [dict, list]
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
tasks:
- name: "Solace Cloud Account: Gather Facts as Dict"
  solace_cloud_account_gather_facts:
    api_token: "{{ api_token }}"
    account_name: "{{ inventory_hostname }}"
    return_format: dict
  register: result

- name: "Save Facts dict: Solace Cloud Account"
  copy:
    content: "{{ result | to_nice_json }}"
    dest: "./tmp/facts.dict.solace_cloud_account.{{ inventory_hostname }}.json"
  delegate_to: localhost

- name: "Set Fact as Dict: Solace Cloud Account Services"
  set_fact:
    dict_facts: "{{ result.ansible_facts.solace_cloud_accounts[inventory_hostname].services }}"

- name: "Solace Cloud Account: Gather Facts as List"
  solace_cloud_account_gather_facts:
    api_token: "{{ api_token }}"
    account_name: "{{ inventory_hostname }}"
    return_format: list
  register: result

- name: "Save Facts List: Solace Cloud Account"
  copy:
    content: "{{ result | to_nice_json }}"
    dest: "./tmp/facts.list.solace_cloud_account.{{ inventory_hostname }}.json"
  delegate_to: localhost

- name: "Set Fact as List: Solace Cloud Account Services"
  set_fact:
    list_facts: "{{ result.ansible_facts.solace_cloud_accounts[inventory_hostname].services }}"

- name: "Loop: Get Service Info for all Services By serviceId"
  solace_cloud_get_service:
    api_token: "{{ api_token }}"
    service_id: "{{ sc_service.serviceId }}"
  loop: "{{ list_facts }}"
  loop_control:
    loop_var: service
    label: "[by serviceId] Service: name={{ service.name }}, id={{ service.serviceId }}"
'''

RETURN = '''
solace_cloud_account:
    description: Contains the info from the Solace Cloud account by {_account_name_}.
    type: dict
    returned: success
    sample:
      solace_cloud_account:
        _account_name_:
          data_centers:
            _data_center_id_1_: "... data center info ..."
            _data_center_id_2_: "... data center info ..."
          services:
            _service_name_1_: "... service info  ..."
            _service_name_2_: "... service info  ..."
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError
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
            raise SolaceInternalError(
                f"arg 'return_format={return_format}' invalid")

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
            solace_cloud_account={account_name: facts}
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
        supports_check_mode=False
    )

    solace_task = SolaceCloudAccountGatherFactsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
