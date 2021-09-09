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
short_description: get Solace Cloud service details
description:
- Get the Solace Cloud Service details by service id.
notes:
- "Module Solace Cloud API: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm"
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
- solace.pubsub_plus.solace.solace_cloud_service_config_service_id
seealso:
- module: solace_cloud_get_services
- module: solace_cloud_service
- module: solace_cloud_get_facts
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
    - set_fact:
        api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
        service_id: "the-service-id"

    - name: "Get service details"
      solace_cloud_get_service:
        api_token: "{{ api_token }}"
        service_id: "{{ service_id }}"
      register: result

    - set_fact:
        service_info: "{{ result.service }}"
        service_name: "{{ result.service.name }}"
        admin_state: "{{ result.service.adminState }}"

    - name: "Save Solace Cloud Service Info to File"
      copy:
        content: "{{ service_info | to_nice_json }}"
        dest: "./tmp/solace_cloud.service_info.{{ service_name }}.json"
      delegate_to: localhost
'''

RETURN = '''
service:
    description: The retrieved service details. Content differs depending on state of service.
    type: dict
    returned: success
    sample:
        name: "the-service-name"
        serviceId: "the-service-id"
        adminState: "the-admin-state"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudConfig, SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudGetServiceTask(SolaceCloudGetTask):

    def __init__(self, module):
        super().__init__(module)

    def do_task(self):
        service_id = self.get_module().params['solace_cloud_service_id']
        service = self.get_solace_cloud_api().get_service(self.get_config(), service_id)
        if not service:
            raise SolaceError(
                f"solace_cloud_service_id={service_id} not found")

        result = self.create_result()
        result.update(dict(
            service=service
        ))
        msg = None
        if not service:
            msg = f"solace cloud service id={service_id} not found"
            result.update(dict(
                rc=1
            ))
        return msg, result


def run_module():

    module_args = {}
    arg_spec = SolaceTaskSolaceCloudConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceCloudGetServiceTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
