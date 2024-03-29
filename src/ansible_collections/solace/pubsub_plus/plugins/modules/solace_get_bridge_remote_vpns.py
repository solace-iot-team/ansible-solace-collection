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
module: solace_get_bridge_remote_vpns
short_description: get list of remote vpns of a bridge
description:
- "Get a list of Remote Message VPN objects of a Bridge."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/getMsgVpnBridgeRemoteMsgVpns"
- "Module Sempv2 Monitor: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/bridge/getMsgVpnBridgeRemoteMsgVpns"
options:
  bridge_name:
    description: The bridge. Maps to 'bridgeName' in the API.
    required: true
    type: str
  bridge_virtual_router:
    description: The bridge virtual router. Maps to 'bridgeVirtualRouter' in the API.
    required: false
    type: str
    default: auto
    choices:
      - primary
      - backup
      - auto
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
seealso:
- module: solace_bridge_remote_vpn
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
  solace_bridge:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
  solace_bridge_remote_vpn:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
  solace_get_bridge_remote_vpns:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: create a bridge
  solace_bridge:
    name: the_bridge
    state: present

- name: add remote vpn
  solace_bridge_remote_vpn:
    remote_msg_vpn_name: the_remote_msg_vpn
    bridge_name: the_bridge
    remote_vpn_location: "xxx.messaging.solace.cloud:55555"
    settings:
      enabled: true
    state: present

- name: get list config
  solace_get_bridge_remote_vpns:
    bridge_name: the_bridge
    api: confing
    query_params:
      where:
      select:
      - bridgeName
      - remoteMsgVpnLocation
      - enabled
  register: result

- name: print result
  debug:
    msg:
      - "{{ result.result_list }}"
      - "{{ result.result_list_count }}"

- name: get list monitor
  solace_get_bridge_remote_vpns:
    bridge_name: the_bridge
    api: monitor
    query_params:
      select:
      - bridgeName
      - remoteMsgVpnLocation
      - enabled
      - up
      - lastConnectionFailureReason
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

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetBridgeRemoteVpnsTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def is_supports_paging(self):
        return False

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteMsgVpns
        bridge_uri = ','.join(
            [params['bridge_name'], params['bridge_virtual_router']])
        return ['msgVpns', params['msg_vpn'], 'bridges', bridge_uri, 'remoteMsgVpns']


def run_module():
    module_args = dict(
        bridge_name=dict(type='str', required=True),
        bridge_virtual_router=dict(type='str', default='auto', choices=[
                                   'primary', 'backup', 'auto'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceGetBridgeRemoteVpnsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
