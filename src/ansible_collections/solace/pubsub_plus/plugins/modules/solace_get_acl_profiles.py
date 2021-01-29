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
module: solace_get_acl_profiles
short_description: get list of acl profiles
description:
- "Get a list of ACL Profile Objects."
- "Reference (Sempv2 Config): https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/getMsgVpnAclProfiles."
- "Reference (Sempv2 Monitor): https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/aclProfile/getMsgVpnAclProfiles."
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
seealso:
- module: solace_acl_profile
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
  solace_acl_profile:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
  solace_get_acl_profiles:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: create acl profile
  solace_acl_profile:
    name: foo
    state: present

- name: get acl profiles config
  solace_get_acl_profiles:
    api: config
    query_params:
      where:
        - "aclProfileName==foo"
      select:
        - "aclProfileName"
  register: result

- name: print result
  debug:
    msg:
      - "{{ result.result_list }}"
      - "{{ result.result_list_count }}"

- name: get acl profiles monitor
  solace_get_acl_profiles:
    api: monitor
    query_params:
      where:
        - "aclProfileName==foo"
      select:
        - "aclProfileName"
  register: result

- name: print result
  debug:
    msg:
      - "{{ result.result_list }}"
      - "{{ result.result_list_count }}"
'''

RETURN = '''
result_list:
  description: The list of objects found containing requested fields. Payload depends on API called.
  returned: success
  type: list
  elements: dict
result_list_count:
  description: Number of items in result_list.
  returned: success
  type: int
rc:
  description: Return code. rc=0 on success, rc=1 on error.
  type: int
  returned: always
  sample:
      success:
          rc: 0
      error:
          rc: 1
msg:
  description: The response from the HTTP call in case of error.
  type: dict
  returned: error
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetAclProfilesTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/aclProfiles
        return ['msgVpns', params['msg_vpn'], 'aclProfiles']


def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGetAclProfilesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
