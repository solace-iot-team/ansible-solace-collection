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
module: solace_dmr_cluster_link_remote_address
short_description: remote address for dmr cluster link
description:
- "Allows addition, removal and configuration of Remote Address Objects on a DRM Cluster Link."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/dmrCluster/createDmrClusterLinkRemoteAddress"
options:
  name:
    description: The FQDN or IP address (and optional port) of the remote node. Maps to 'remoteAddress' in the API.
    required: true
    type: str
    aliases: [remote_address]
  dmr_cluster_name:
    description: The name of the DMR cluster. Maps to 'dmrClusterName' in the API.
    required: true
    type: str
  remote_node_name:
    description: The name of the remote node. Maps to 'remoteNodeName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_dmr_cluster
- module: solace_dmr_cluster_link
- module: solace_get_dmr_cluster_link_remote_addresses
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
  solace_dmr_cluster_link_remote_address:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
tasks:
  - name: Remove 'remoteNode' DMR Link Remote address
    solace_dmr_cluster_link_remote_address:
      name: 192.168.0.34
      remote_node_name: remoteNode
      dmr_cluster_name: foo
      state: absent

  - name: Add 'remoteNode' DMR Link Remote address
    solace_dmr_cluster_link_remote_address:
      name: 192.168.0.34
      remote_node_name: remoteNode
      dmr_cluster_name: foo
      state: present
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


class SolaceDmrClusterLinkRemoteAddressTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'remoteAddress'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['dmr_cluster_name'], params['remote_node_name'], params['name']]

    def get_func(self, dmr_cluster_name, remote_node_name, remote_address):
        # GET /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/remoteAddresses/{remoteAddress}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters',
                      dmr_cluster_name, 'links', remote_node_name, 'remoteAddresses', remote_address]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, dmr_cluster_name, remote_node_name, remote_address, settings=None):
        # POST dmrClusters/{dmrClusterName}/links/{remoteNodeName}/remoteAddresses
        data = {
            'dmrClusterName': dmr_cluster_name,
            'remoteNodeName': remote_node_name,
            self.OBJECT_KEY: remote_address
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters',
                      dmr_cluster_name, 'links', remote_node_name, 'remoteAddresses']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, dmr_cluster_name, remote_node_name, remote_address):
        #  DELETE /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/remoteAddresses/{remoteAddress}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters',
                      dmr_cluster_name, 'links', remote_node_name, 'remoteAddresses', remote_address]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['remote_address']),
        dmr_cluster_name=dict(type='str', required=True),
        remote_node_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceDmrClusterLinkRemoteAddressTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
