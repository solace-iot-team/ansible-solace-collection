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
module: solace_dmr_cluster
short_description: dmr cluster
description:
- "Configure DMR Cluster Objects. Allows addition, removal and configuration of DMR cluster objects in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/dmrCluster"
options:
  name:
    description: Name of the DMR cluster. Maps to 'dmrClusterName' in the API.
    required: true
    type: str
    aliases: [dmr_cluster_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_get_dmr_clusters
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
  solace_dmr_cluster:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
tasks:

- name: create
  solace_dmr_cluster:
    name: foo

- name: update
  solace_dmr_cluster:
    name: foo
    settings:
        authenticationBasicEnabled: true
        authenticationBasicType: internal
        tlsServerCertMaxChainDepth: 5

- name: remove
  solace_dmr_cluster:
    name: foo
    state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceDMRClusterTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'dmrClusterName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['name']]

    def get_func(self, dmr_cluster_name):
        # GET /dmrClusters/{dmrClusterName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'dmrClusters', dmr_cluster_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, dmr_cluster_name, settings=None):
        # POST /dmrClusters
        data = {
            self.OBJECT_KEY: dmr_cluster_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, dmr_cluster_name, settings=None, delta_settings=None):
        # PATCH /dmrClusters/{dmrClusterName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'dmrClusters', dmr_cluster_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, dmr_cluster_name):
        # DELETE /dmrClusters/{dmrClusterName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'dmrClusters', dmr_cluster_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['dmr_cluster_name'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceDMRClusterTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
