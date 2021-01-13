#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Mike O'Brien, <mike.obrien@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_distributed_cache_cluster

short_description: Configure Distributed Cache cluster on a message vpn.

description:
- "Configure solCache cluster on a message vpn. Allows addition, removal and configuration of clusters in an idempotent manner."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/distributedCache)."

options:
  name:
    description: Name of the cluster. Maps to 'clusterName' in the API.
    required: true
    type: str
    aliases: [cluster, cluster_name]

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.settings
- solace.state

author:
  - Mike O'Brien (mike.obrien@solace.com)

'''

EXAMPLES = '''
- name: Playbook to add a cache cluster named 'someCluster'
  hosts: localhost
  tasks:
  - name: Remove 'someCluster' cluster from 'someCache' cache
    solace_distributed_cache_cluster:
      name: someCluster
      cacheName: someCache
      msg_vpn: foo
      state: absent

  - name: Add 'someCluster' cluster to 'someCache' cache
    solace_distributed_cache_cluster:
      name: someCluster
      cacheName: someCache
      msg_vpn: foo
      state: present
    register: testout

  - name: dump output
    debug:
      msg: '{{ testout }}'
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

class SolaceDistributedCacheClusterTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'clusterName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['cache']]

    def get_func(self, solace_config, vpn, cache, lookup_item_value):
        """Pull configuration for all cache clusters associated with a given cache"""
        # GET /msgVpns​/{msgVpnName}​/distributedCaches/{cacheName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, cache, cluster, settings=None):
        """Create a cache cluster"""
        defaults = {}
        mandatory = {
            'msgVpnName': vpn,
            'cacheName': cache,
            'clusterName': cluster
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, cache, lookup_item_value, settings):
        """Update an existing cluster"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, cache, lookup_item_value):
        """Delete a cluster"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
        cache=dict(type='str', aliases=['cache', 'cache_name'], required=True),
        name=dict(type='str', aliases=['cluster', 'clusterName'], required=True)
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

    solace_task = SolaceDistributedCacheClusterTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
