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

short_description: Retrieves service info (facts) about all services available in the Solace Cloud Account.

description: >
  Retrieves service info (facts) about all services available in the Solace Cloud Account.
  Stores the facts in: ['ansible_facts']['solace_cloud_accounts'][{service-name}].
  Use to retrieve the SEMP endpoints for a Solace Cloud service as inputs for other modules.

seealso:
- solace_cloud_get_facts

notes:
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm)."

options:
    account_name:
        description: The host specified in the inventory. Represents the Solace Cloud Account.
        required: true
        type: str
        notes:
            - Only used internally in the playbooks, so you can choose whichever name makes sense in your case.
    return_format:
        description: >
            The format of the returned JSON. Either as a JSON object or a JSON array.
        required: true
        choices:
            - dict
            - list
        notes:
            - Use 'dict' when you want to access the facts in a playbook by account_name (i.e. 'inventory_hostname') directly.
            - Use 'list' when you want to iterate over each service in your playbook.

extends_documentation_fragment:
- solace.solace_cloud_service_config

seealso:
- module: solace_get_facts

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
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
    msg:
        description: error message if not ok
        type: str
    response:
        description: The response from the GET {serviceId} call. Differs depending on state of service.
        type: complex
'''

MODULE_HAS_IMPORT_ERROR = False
MODULE_IMPORT_ERR_TRACEBACK = None
import traceback
try:
    import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
    from ansible.module_utils.basic import AnsibleModule
    import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_cloud_utils as scu
except ImportError:
    MODULE_HAS_IMPORT_ERROR = True
    MODULE_IMPORT_ERR_TRACEBACK = traceback.format_exc()

class SolaceCloudAccountGatherFactsTask(scu.SolaceCloudTask):

    def __init__(self, module):
        sc.module_fail_on_import_error(module, MODULE_HAS_IMPORT_ERROR, MODULE_IMPORT_ERR_TRACEBACK)
        scu.SolaceCloudTask.__init__(self, module)
        return

    def get_services(self):
        # GET https://api.solace.cloud/api/v0/services
        path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH]
        ok, resp = scu.make_get_request(self.sc_config, path_array)
        if not ok:
            return False, resp
        # get full config for all services
        # if creationState == 'completed'
        # return error, if any found that are not completed yet
        ac_services = resp

        return_format = self.module.params['return_format']
        if return_format == 'dict':
            services = dict()
        else:
            services = []

        for ac_service in ac_services:
            service_id = ac_service['serviceId']
            name = ac_service['name']
            if ac_service['creationState'] != "completed":
                resp = dict(
                    error="Service not fully started yet.",
                    name=ac_service['name'],
                    serviceId=ac_service['serviceId'],
                    creationState=ac_service['creationState']
                )
                return False, resp
            else:
                # GET https://api.solace.cloud/api/v0/services/{{serviceId}}
                path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH, service_id]
                ok, resp = scu.make_get_request(self.sc_config, path_array)
                if not ok:
                    return False, resp
            if return_format == 'dict':
                services[name] = resp
            else:
                services.append(resp)
        return True, services

    # Note: current API does not allow this, fix expected soon (2020-08-11)
    def get_data_centers(self):
        # GET /api/v0/datacenters
        path_array = [scu.SOLACE_CLOUD_API_DATA_CENTERS]
        return scu.make_get_request(self.sc_config, path_array)

    def gather_facts(self):
        account_name = self.module.params['account_name']
        return_format = self.module.params['return_format']
        facts = dict()
        if return_format == 'dict':
            facts[account_name] = dict(
                data_centers=dict(),
                services=dict()
            )
        elif return_format == 'list':
            facts[account_name] = dict(
                data_centers=[],
                services=[]
            )
        else:
            raise ValueError("unknown return_format='{}'. pls raise an issue.".format(return_format))

        # waiting for Solace Cloud to enable the call...
        # ok, resp = self.get_data_centers()
        # if not ok:
        #     return False, resp
        # ...

        ok, resp = self.get_services()
        if not ok:
            return False, resp
        facts[account_name]['services'] = resp
        # if return_format == 'dict':
        #     facts[account_name]['services'] = resp
        # else:
        #     facts[account_name]['services'] = resp

        return True, facts


def run_module():
    module_args = dict(
        account_name=dict(type='str', required=True, aliases=['name']),
        return_format=dict(type='str', required=True, choices=['dict', 'list'])
    )
    arg_spec = scu.arg_spec_solace_cloud()
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        ansible_facts=dict()
    )

    solace_task = SolaceCloudAccountGatherFactsTask(module)
    ok, resp = solace_task.gather_facts()
    if not ok:
        result['rc'] = 1
        module.fail_json(msg=resp, **result)

    result['ansible_facts']['solace_cloud_accounts'] = resp
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
