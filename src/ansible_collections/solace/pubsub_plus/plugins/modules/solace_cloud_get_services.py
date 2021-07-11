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
module: solace_cloud_get_services
short_description: get all services in Solace Cloud
description:
- "Get a list of all services' details in the Solace Cloud account."
notes:
- "Module Solace Cloud API: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm"
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
seealso:
- module: solace_cloud_get_service
- module: solace_cloud_service
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
  - name: "solace_cloud_get_services"
    solace_cloud_get_services:
      api_token: "{{ api_token }}"
    register: result

  - set_fact:
      service_list: "{{ result.result_list }}"

  - name: "Loop: Get Service for all Services By serviceId"
    solace_cloud_get_service:
      api_token: "{{ api_token }}"
      service_id: "{{ service.serviceId }}"
    loop: "{{ service_list }}"
    loop_control:
      loop_var: service
'''

RETURN = '''
result_list:
  description: The list of objects found containing requested fields. Results differ based on the api called.
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudConfig
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
    arg_spec = SolaceTaskSolaceCloudConfig.arg_spec_solace_cloud()
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
