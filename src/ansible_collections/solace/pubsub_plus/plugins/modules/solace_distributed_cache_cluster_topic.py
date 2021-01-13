#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Mike O'Brien, <mike.obrien@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_distributed_cache_cluster_topic

short_description: Configure a topic on a Distributed Cache cluster.

description:
- "Configure a topic on a distributed Cache cluster. Allows addition, removal and configuration of topics in an idempotent manner."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/distributedCache)."

options:
  name:
    description: The topic. 
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
- name: Playbook to add a topic 'a/b' to cache cluster named 'someCluster'
  hosts: localhost
  tasks:
  - name: Remove 'a/b' topic from 'someCluster'
    solace_distributed_cache_cluster_topic:
      name: a/b
      cache: someCache
      cluster: someCluster
      msg_vpn: somevpn
      state: absent

  - name: Add 'bar' cache to 'someCluster' 
    solace_distributed_cache_cluster_topic:
      name: a/b
      cache: someCache
      cluster: someCluster
      msg_vpn: somevpn
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

class SolaceDistributedCacheClusterTopicTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'topic'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['cache'], self.module.params['cluster']]

    def get_func(self, solace_config, vpn, cache, cluster, lookup_item_value):
        """Pull configuration for all topics associated with a given VPN/cache/cluster"""
        # GET /msgVpns​/{msgVpnName}​/distributedCaches/{cacheName}/clusters/{clusterName}/topics
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS, cluster, su.DISTRIBUTED_CACHE_CLUSTER_TOPICS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, cache, cluster, topic, settings=None):
        """Create a topic"""
        defaults = {}
        mandatory = {
            'msgVpnName': vpn,
            'cacheName': cache,
            'clusterName': cluster,
            'topic': topic
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS, cluster, su.DISTRIBUTED_CACHE_CLUSTER_TOPICS]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, cache, cluster, lookup_item_value, settings):
        """Update an existing topic"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS, cluster, su.DISTRIBUTED_CACHE_CLUSTER_TOPICS, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, cache, cluster, lookup_item_value):
        """Delete a topic"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.DISTRIBUTED_CACHES, cache, su.DISTRIBUTED_CACHE_CLUSTERS, cluster, su.DISTRIBUTED_CACHE_CLUSTER_TOPICS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
        cache=dict(type='str', aliases=['cache', 'cache_name'], required=True),
        cluster=dict(type='str', aliases=['cluster_name', 'clusterName'], required=True),
        name=dict(type='str', aliases=['topic', 'topicName'], required=True)
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

    solace_task = SolaceDistributedCacheClusterTopicTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
