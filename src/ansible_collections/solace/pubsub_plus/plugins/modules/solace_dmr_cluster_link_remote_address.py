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
  - "Allows addition, removal and configuration of remote address objects on a DRM cluster link."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/dmrCluster/createDmrClusterLinkRemoteAddress."

options:
  name:
    description: The FQDN or IP address (and optional port) of the remote node. Maps to 'remoteAddress' in the API.
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
  solace_dmr_cluster_link_remote_address:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
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
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceLinkRemoteAddressTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'remoteAddress'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['dmr_cluster_name'], self.module.params['remote_node_name']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, dmr_cluster_name, link, lookup_item_value):
        # GET /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/remoteAddresses/{remoteAddress}
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, dmr_cluster_name, su.LINKS, link, su.REMOTE_ADDRESSES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, dmr_cluster_name, link, address, settings=None):
        # POST /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/remoteAddresses
        defaults = {
            'dmrClusterName': dmr_cluster_name,
            'remoteNodeName': link
        }
        mandatory = {
            'remoteAddress': address
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, dmr_cluster_name, su.LINKS, link, su.REMOTE_ADDRESSES]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, dmr_cluster_name, link, lookup_item_value):
        # DELETE /dmrClusters/{dmrClusterName}/links/{remoteNodeName}/remoteAddresses/{remoteAddress}
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, dmr_cluster_name, su.LINKS, link, su.REMOTE_ADDRESSES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        dmr_cluster_name=dict(type='str', required=True),
        remote_node_name=dict(type='str', required=True)
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceLinkRemoteAddressTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
