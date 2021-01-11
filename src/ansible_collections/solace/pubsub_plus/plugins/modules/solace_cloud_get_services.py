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
module: solace_cloud_get_service

TODO: rework documentation

short_description: Get the Solace Cloud Service details.

description: Get the Solace Cloud Service details by name or serviceId.

notes:
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm)."

options:
  name:
    description:
        - The name of the service.
        - "Note: If name is not provided, service_id must."
    required: false
    type: str
  service_id:
    description:
        - The service id.
        - "Note: If service_id is not provided, name must."
    required: false
    type: str

extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_service_config

seealso:
- module: solace_cloud_service

author: Ricardo Gomez-Ulmke (@rjgu)

'''

EXAMPLES = '''
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  tasks:
    - name: "Get service details"
      solace_cloud_get_service:
        api_token: "{{ api_token_all_permissions }}"
        service_id: "{{ sc_service_created_id }}"
      register: get_service_result

    - set_fact:
        sc_service_created_info: "{{ result.response }}"

    - name: "Save Solace Cloud Service Facts to File"
      copy:
        content: "{{ sc_service_created_info | to_nice_json }}"
        dest: "./tmp/facts.solace_cloud_service.{{ sc_service.name }}.json"
      delegate_to: localhost
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
response:
    description: The response from the get call. Differs depending on state of service.
    type: complex
    returned: success
    contains:
        serviceId:
            description: The service Id of the created service
            returned: if service exists
            type: str
        adminState:
            description: The state of the service
            returned: if service exists
            type: str
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudConfig, SolaceTaskSolaceCloudServiceConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudGetServiceTask(SolaceCloudGetTask):

    def __init__(self, module):
        super().__init__(module)

    def do_task(self):
        services = self.get_solace_cloud_api().get_services(self.get_config())
        result = self.create_result_with_list(services)
        return None, result


def run_module():

    module_args = dict(
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceCloudGetServiceTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
