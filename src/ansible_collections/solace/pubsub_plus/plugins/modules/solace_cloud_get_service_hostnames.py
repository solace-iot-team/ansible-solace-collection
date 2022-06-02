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
module: solace_cloud_get_service_hostnames
short_description: get all service hostnames
description:
- "Get a list of additional hostnames configured on the service."
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
- solace.pubsub_plus.solace.solace_cloud_service_config_service_id_mandatory
seealso:
- module: solace_cloud_service_hostname
- module: solace_cloud_service_hostnames
- module: solace_cloud_get_service
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

-
  name: solace_cloud_service_hostnames doc example
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace.pubsub_plus.solace_cloud_get_service_hostnames:
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
    solace.pubsub_plus.solace_cloud_service_hostname:
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
  tasks:

    - name: exit if not solace cloud
      meta: end_play
      when: broker_type != 'solace_cloud'

    - set_fact:
        additionalHostnames:
        - hostname-1
        - hostname-2

    - name: ensure all hostnames in list are absent
      solace_cloud_service_hostname:
        hostname: "{{ item }}"
        state: absent
      loop: "{{ additionalHostnames }}"

    - name: add all hostnames in list
      solace_cloud_service_hostname:
        hostname: "{{ item }}"
        state: present
      loop: "{{ additionalHostnames }}"

    - name: get list of existing hostnames
      solace_cloud_get_service_hostnames:

    - name: ensure all hostnames in list are absent
      solace_cloud_service_hostname:
        hostname: "{{ item }}"
        state: absent
      loop: "{{ additionalHostnames }}"

###
# The End.
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudConfig, SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudGetServiceHostNamesTask(SolaceCloudGetTask):

    def __init__(self, module):
        super().__init__(module)

    def do_task(self):
        service_id = self.get_module().params['solace_cloud_service_id']
        additionalHostnames = self.get_solace_cloud_api(
        ).get_service_additional_hostnames(self.get_config(), service_id)
        result = self.create_result_with_list(additionalHostnames)
        return None, result


def run_module():

    module_args = {}
    arg_spec = SolaceTaskSolaceCloudConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id_mandatory())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceCloudGetServiceHostNamesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
