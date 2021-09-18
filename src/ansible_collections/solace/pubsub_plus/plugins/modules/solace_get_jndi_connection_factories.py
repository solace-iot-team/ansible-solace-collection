#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Ulrich Herbst <ulrich.herbst@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_get_jndi_connection_factories
short_description: get list of JNDI Connection Factories
description:
- "Get a list of JNDI Connection Factory objects."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/jndi/getMsgVpnJndiConnectionFactories"
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
seealso:
- module: solace_jndi_connection_factory
author:
- Ulrich Herbst (@uherbstsolace)
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace_jndi_connection_factory:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace_get_jndi_connection_factories:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
  - name: add JNDI connection factory
    solace_jndi_connection_factory:
      name: bar
      state: present

  - name: update JNDI connection factory
    solace_jndi_connection_factory:
      name: bar
      settings:
        guaranteedReceiveWindowSize: 193
      state: present

  - name: get list config
    solace_get_jndi_connection_factories:
      query_params:
        where:
        - "connectionFactoryName==bar*"
    register: result

  - name: get list monitor
    solace_get_jndi_connection_factories:
      api: monitor
      query_params:
        where:
        - "connectionFactoryName==bar*"
    register: result

  - name: remove JNDI connection factory
    solace_jndi_connection_factory:
      name: bar
      state: absent
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

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible.module_utils.basic import AnsibleModule


class SolaceGetJndiConnectionFactoriesTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def get_monitor_api_base(self) -> str:
        return SolaceSempV2Api.API_BASE_SEMPV2_MONITOR

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/jndiConnectionFactories
        return ['msgVpns', params['msg_vpn'], 'jndiConnectionFactories']


def run_module():
    module_args = {}
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceGetJndiConnectionFactoriesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
