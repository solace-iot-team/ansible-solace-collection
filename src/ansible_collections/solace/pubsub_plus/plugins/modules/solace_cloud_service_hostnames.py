#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_cloud_service_hostnames
short_description: list of hostnames on a service
description:
- "Manage a list of additional hostnames on a service in a single transaction."
- "Allows addition and removal of a list of additional hostnames as well as replacement of all existing additional hostnames on a service."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates hostname list."
- "Reports which hostnames were added, deleted and omitted (duplicates). In case of an error, reports the invalid hostname."
- "To delete all Subscription objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "This module only supports solace broker services < 9.13."
options:
  hostnames:
    description: The list of additional hostnames to manage on the service.
    required: true
    type: list
    elements: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
- solace.pubsub_plus.solace.solace_cloud_service_config_service_id_mandatory
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace_cloud_get_service_hostnames
- module: solace_cloud_service_hostname
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
    solace.pubsub_plus.solace_cloud_service_hostnames:
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
  tasks:

    - name: exit if not solace cloud
      meta: end_play
      when: broker_type != 'solace_cloud'

    - set_fact:
        additionalHostnames:
        - manage-list-hostname-1
        - manage-list-hostname-2

    - name: ensure all hostnames in list are absent
      solace_cloud_service_hostnames:
        hostnames: "{{ additionalHostnames }}"
        state: absent

    - name: add all hostnames in list
      solace_cloud_service_hostnames:
        hostnames: "{{ additionalHostnames }}"
        state: exactly

    - name: ensure all hostnames in list are absent
      solace_cloud_service_hostnames:
        hostnames: null
        state: exactly

###
# The End.
'''

RETURN = '''
response:
    description: The response of the operation.
    type: dict
    returned: always
    sample:
      success:
        response:
          - added: manage-list-hostname-1.messaging.solace.cloud
          - added: manage-list-hostname-2.messaging.solace.cloud
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudCRUDListTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudServiceHostnamesTask(SolaceCloudCRUDListTask):

    HOSTNAME_SUFFIX = ".messaging.solace.cloud"

    def __init__(self, module):
        super().__init__(module)

    def get_objects_result_data_object_key(self) -> str:
        return self.get_module().params['solace_cloud_service_id']

    def get_object_key_list(self, object_key) -> list:
        # object_key = service_id
        additionalHostnames = self.solace_cloud_api.get_service_additional_hostnames_prior_9_13(
            self.get_config(), object_key)
        return additionalHostnames

    def get_param_names(self) -> list:
        names = self.get_config().get_params()['hostnames']
        hostnames = []
        if isinstance(names, list):
            for name in names:
                hostnames += [name + self.HOSTNAME_SUFFIX]
        return hostnames

    def get_original_hostname(self, hostname_with_suffix) -> str:
        split_list = hostname_with_suffix.split(".", 1)
        return split_list[0]

    def get_new_settings(self) -> dict:
        return None

    # def get_objects_path_array(self) -> list:
    #     # GET /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions
    #     params = self.get_config().get_params()
    #     return ['msgVpns', params['msg_vpn'], 'queues', params['queue_name'], 'subscriptions']

    def get_crud_args(self, object_key) -> list:
        # object_key = hostname_with_suffix
        params = self.get_module().params
        return [params['solace_cloud_service_id'], object_key]

    def create_func(self, object_key, hostname_with_suffix, settings=None):
        # object_key = service_id
        # POST: Request URL: https://api.solace.cloud/api/v0/services/{service_id}/serviceHostNames
        # {
        #   "serviceHostName": "testtest",
        #   "operation": "create"
        # }
        module_op = SolaceTaskOps.OP_CREATE_OBJECT
        # get rid of the suffix again

        data = {
            "serviceHostName": self.get_original_hostname(hostname_with_suffix),
            "operation": "create"
        }
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()),
                      SolaceCloudApi.API_SERVICES,
                      object_key,
                      'serviceHostNames']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, object_key, json_body=data, module_op=module_op)

    def delete_func(self, service_id, hostname_with_suffix):
        # POST: Request URL: https://api.solace.cloud/api/v0/services/{service_id}/serviceHostNames
        # {
        #   "serviceHostName": "test-hostnames",
        #   "operation": "delete"
        # }
        module_op = SolaceTaskOps.OP_DELETE_OBJECT
        data = {
            "serviceHostName": self.get_original_hostname(hostname_with_suffix),
            "operation": "delete"
        }
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()),
                      SolaceCloudApi.API_SERVICES,
                      service_id,
                      'serviceHostNames']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=data, module_op=module_op)


def run_module():
    module_args = dict(
        hostnames=dict(type='list',
                       required=True,
                       elements='str'
                       ),
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id_mandatory())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_state_crud_list())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceCloudServiceHostnamesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
