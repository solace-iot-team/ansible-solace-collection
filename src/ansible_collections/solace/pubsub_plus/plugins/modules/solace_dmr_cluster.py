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
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/dmrCluster)."

options:
  name:
    description: Name of the DMR cluster. Maps to 'dmrClusterName' in the API.
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
  solace_dmr_cluster:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: create
  solace_dmr_cluster:
    name: foo

- name: update
  solace_dmr_cluster:
    name: foo
    settings:
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
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceDMRClusterTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'dmrClusterName'
    WHITELIST_KEYS = ['authenticationBasicPassword',
                      'authenticationClientCertPassword']
    REQUIRED_TOGETHER_KEYS = [
        ['authenticationClientCertPassword', 'authenticationClientCertContent']
    ]

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return []

    def get_func(self, solace_config, lookup_item_value):
        # GET /dmrClusters/{dmrClusterName}
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, dmr, settings=None):
        defaults = {
            'enabled': True,
            'authenticationBasicPassword': solace_config.vmr_auth[1]
        }
        mandatory = {
            'dmrClusterName': dmr
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, lookup_item_value, settings):
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, lookup_item_value):
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True)
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

    solace_task = SolaceDMRClusterTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
