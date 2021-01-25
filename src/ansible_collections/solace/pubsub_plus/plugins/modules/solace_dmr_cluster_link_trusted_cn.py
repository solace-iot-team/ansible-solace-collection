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
module: solace_dmr_cluster_link_trusted_cn
TODO: re-work doc
short_description: trusted common name for dmr cluster link

description:
  - "Allows addition, removal and configuration of trusted common name objects on DMR cluster links."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/dmrCluster/createDmrClusterLinkTlsTrustedCommonName."

options:
  name:
    description: The expected trusted common name of the remote certificate. Maps to 'tlsTrustedCommonName' in the API.
    required: true
    type: str
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
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.settings
- solace.pubsub_plus.solace.state

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
  solace_dmr_cluster_link_trusted_cn:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: remove
    solace_dmr_cluster_link_trusted_cn:
      name: "*.messaging.solace.cloud"
      remote_node_name: remoteNode
      dmr_cluster_name: foo
      state: absent

  - name: add
    solace_dmr_cluster_link_trusted_cn:
      name: "*.messaging.solace.cloud"
      remote_node_name: remoteNode
      dmr_cluster_name: foo
      state: present
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceDmrClusterLinkTrustedCommonNameTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'tlsTrustedCommonName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['dmr_cluster_name'], params['remote_node_name'], params['name']]

    def get_func(self, dmr_cluster_name, remote_node_name, tls_trusted_cn):
        # GET /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters', dmr_cluster_name, 'links', remote_node_name, 'tlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, dmr_cluster_name, remote_node_name, tls_trusted_cn, settings=None):
        # POST /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/tlsTrustedCommonNames
        data = {
            'dmrClusterName': dmr_cluster_name,
            'remoteNodeName': remote_node_name,
            self.OBJECT_KEY: tls_trusted_cn
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters', dmr_cluster_name, 'links', remote_node_name, 'tlsTrustedCommonNames']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, dmr_cluster_name, remote_node_name, tls_trusted_cn):
        # DELETE /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters', dmr_cluster_name, 'links', remote_node_name, 'tlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['tls_trusted_common_name']),
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

    solace_task = SolaceDmrClusterLinkTrustedCommonNameTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
