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
module: solace_acl_client_connect_exception

short_description: client connect exception for acl profile

description:
- "Configure client connect exception objects for an ACL Profile."
- "Allows addition and removal of client connect exception objects for ACL Profiles."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/getMsgVpnAclProfileClientConnectExceptions)."

options:
  name:
    description: Name of the client connect exception address. Maps to 'clientConnectExceptionAddress' in the API.
    required: true
    type: str
  acl_profile_name:
    description: The ACL Profile.
    required: true
    type: str

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.settings

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
solace_acl_client_connect_exception:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: Remove ACL Client Connect Exception
    solace_acl_client_connect_exception:
        name: "{{client_address}}"
        acl_profile_name: "{{ acl_profile }}"
        msg_vpn: "{{ msg_vpn }}"
        state: absent

  - name: Add ACL Client Connect Exception
    solace_acl_client_connect_exception:
        name: "{{client_address}}"
        acl_profile_name: "{{ acl_profile }}"
        msg_vpn: "{{ msg_vpn }}"
        state: present
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
    sample:
        aclProfileName: test_ansible_solace
        clientConnectExceptionAddress: 192.168.1.64/26
        msgVpnName: default
'''


import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceACLClientConnectExceptionTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'clientConnectExceptionAddress'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['acl_profile_name']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, acl_profile_name, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/clientConnectExceptions/{clientConnectExceptionAddress}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, acl_profile_name, client_connect_exception_address, settings=None):
        defaults = {
            'msgVpnName': vpn,
            'aclProfileName': acl_profile_name
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: client_connect_exception_address
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, acl_profile_name, lookup_item_value):
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
        acl_profile_name=dict(type='str', required=True)
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

    solace_task = SolaceACLClientConnectExceptionTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
