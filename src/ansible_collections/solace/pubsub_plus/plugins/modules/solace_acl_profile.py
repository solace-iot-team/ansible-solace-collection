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
module: solace_acl_profile

short_description: configure acl profile

description:
- "Configure an ACL Profile on a message vpn. Allows addition, removal and configuration of ACL Profile(s) on Solace Brokers in an idempotent manner."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile)."

options:
    name:
        description: Name of the ACL Profile. Maps to 'aclProfileName' in the API.
        type: str
        required: true

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.settings
- solace.pubsub_plus.solace.state

author:
  - Mark Street (@mkst)
  - Swen-Helge Huber (@ssh)
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
    solace_acl_profile:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
tasks:
  - name: Remove ACL Profile
    solace_acl_profile:
      name: "{{ acl_profile }}"
      msg_vpn: "{{ msg_vpn }}"
      state: absent

  - name: Add ACL Profile
    solace_acl_profile:
      name: "{{ acl_profile }}"
      msg_vpn: "{{ msg_vpn }}"
      settings:
        clientConnectDefaultAction: allow

  - name: Update ACL Profile
    solace_acl_profile:
      name: "{{ acl_profile }}"
      msg_vpn: "{{ msg_vpn }}"
      settings:
        publishTopicDefaultAction: allow
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
    sample:
        aclProfileName: test_ansible_solace
        clientConnectDefaultAction: disallow
        msgVpnName: default
        publishTopicDefaultAction: disallow
        subscribeShareNameDefaultAction: allow
        subscribeTopicDefaultAction: disallow
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceACLProfileTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'aclProfileName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn']]

    def lookup_item(self):
        # aclProfileName <= 32 chars; create a 'nicer' hint here
        lookup_item = self.module.params['name']
        if len(lookup_item) > 32:
            raise ValueError(f"argument 'name' ({self.LOOKUP_ITEM_KEY}) longer than 32 chars:'{lookup_item}'")
        return lookup_item

    def get_func(self, solace_config, vpn, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, acl_profile, settings=None):
        defaults = {
            'msgVpnName': vpn,
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: acl_profile
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, lookup_item_value, settings=None):
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, lookup_item_value):
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module."""
    """Compose module arguments"""
    module_args = dict(
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

    solace_task = SolaceACLProfileTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
