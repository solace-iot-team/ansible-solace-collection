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
module: solace_get_mqtt_session_subscriptions
TODO: rework doc

short_description: list of mqtt session subscriptions

description:
- "Get a list of MQTT Session Subscription Objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/mqttSession/getMsgVpnMqttSessionSubscriptions)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/mqttSession/getMsgVpnMqttSessionSubscriptions)."

options:
  mqtt_session_client_id:
    description: The MQTT session client id. Maps to 'mqttSessionClientId' in the API.
    type: str
    required: true
    aliases: [client_id, client]

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
- solace.pubsub_plus.solace.virtual_router

seealso:
- module: solace_mqtt_session_subscription

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
  solace_get_mqtt_session_subscriptions:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:

  - name: get subscriptions
    solace_get_mqtt_session_subscriptions:
        api: config
        client_id: client-id
        query_params:
          where:
            - "subscriptionTopic==ansible-solace/test/*"
          select:
            - "mqttSessionClientId"
            - "mqttSessionVirtualRouter"
            - "subscriptionTopic"
            - "subscriptionQos"
    register: result

  - name: result config api
    debug:
        msg:
            - "{{ result.result_list }}"
            - "{{ result.result_list_count }}"

  - name: get subscriptions
    solace_get_mqtt_session_subscriptions:
        api: monitor
        client_id: client-id
        query_params:
          where:
            - "subscriptionTopic==ansible-solace/test/*"
          select:
            - "mqttSessionClientId"
            - "mqttSessionVirtualRouter"
            - "subscriptionTopic"
            - "subscriptionQos"
    register: result

  - name: result monitor api
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

'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetMqttSessionSubscritionsTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions
        client_id = params['mqtt_session_client_id']
        virtual_router = params['virtual_router']
        uri_ext = ','.join([client_id, virtual_router])
        return ['msgVpns', params['msg_vpn'], 'mqttSessions', uri_ext, 'subscriptions']


def run_module():
    module_args = dict(
        mqtt_session_client_id=dict(type='str', aliases=['client_id', 'client'], required=True),
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_virtual_router())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )
    solace_task = SolaceGetMqttSessionSubscritionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
