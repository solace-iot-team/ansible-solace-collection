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
module: solace_cloud_service_hostname
short_description: manage service hostnames
description: "Add & delete additional hostnames on a Solace Cloud service."
options:
  hostname:
    description:
    - The additional hostname on the service to manage.
    type: str
    required: true
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
- solace.pubsub_plus.solace.solace_cloud_service_config_service_id_mandatory
- solace.pubsub_plus.solace.state
seealso:
- module: solace_cloud_get_service_hostnames
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
response:
    description: response from the Api call.
    type: dict
    returned: success
    sample:
      msg: null
      rc: 0
      response:
        adminProgress: completed
        creationTimestamp: 0
        id: "3icn47vcsgg"
        operation: "create"
        serviceHostName: "hostname-1"
        type: "serviceHostNameRequest"
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
    description: error message if not ok
    type: str
    returned: error
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudServiceHostnameTask(SolaceCloudCRUDTask):

    HOSTNAME_SUFFIX = ".messaging.solace.cloud"

    def __init__(self, module):
        super().__init__(module)
        self.solace_cloud_api = SolaceCloudApi(module)
        module.params[self.get_settings_arg_name()] = {
            "additionalHostname": module.params['hostname'] + self.HOSTNAME_SUFFIX
        }

    def get_args(self):
        params = self.get_module().params
        service_id = params.get(self.get_config().PARAM_SERVICE_ID, None)
        return [service_id, params['hostname']]

    def get_func(self, service_id, hostname):
        additionalHostnames = self.solace_cloud_api.get_service_additional_hostnames(
            self.get_config(), service_id)
        # find hostname in list
        _hostname = hostname + self.HOSTNAME_SUFFIX
        if(_hostname in additionalHostnames):
            return {
                "additionalHostname": _hostname
            }
        else:
            return None

    def create_func(self, service_id, hostname, settings=None):
        # POST: Request URL: https://api.solace.cloud/api/v0/services/{service_id}/serviceHostNames
        # {
        #   "serviceHostName": "testtest",
        #   "operation": "create"
        # }
        module_op = SolaceTaskOps.OP_CREATE_OBJECT
        data = {
            "serviceHostName": hostname,
            "operation": "create"
        }
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()),
                      SolaceCloudApi.API_SERVICES,
                      service_id,
                      'serviceHostNames']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=data, module_op=module_op)

    def update_func(self, service_id, hostname, settings=None, delta_settings=None):
        msg = [
            f"Solace Cloud Service {service_id} additional hostname '{hostname}' already exists.",
            "You cannot update an existing hostname. Only option: delete & create.",
            "changes requested: see 'delta'"
        ]
        raise SolaceError(msg, dict(delta=delta_settings))

    def delete_func(self, service_id, hostname):
        # POST: Request URL: https://api.solace.cloud/api/v0/services/{service_id}/serviceHostNames
        # {
        #   "serviceHostName": "test-hostnames",
        #   "operation": "delete"
        # }
        module_op = SolaceTaskOps.OP_DELETE_OBJECT
        data = {
            "serviceHostName": hostname,
            "operation": "delete"
        }
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()),
                      SolaceCloudApi.API_SERVICES,
                      service_id,
                      'serviceHostNames']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=data, module_op=module_op)


def run_module():
    module_args = dict(
        hostname=dict(type='str', required=True),
        # wait_timeout_minutes=dict(type='int', required=False, default=30)
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id_mandatory())
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_state())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceCloudServiceHostnameTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
