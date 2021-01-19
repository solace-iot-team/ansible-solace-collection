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
module: solace_mqtt_session_subscription
TODO: rework doc
short_description: subscription for mqtt session

description:
- "Configure a MQTT Session Subscription object. Allows addition, removal and update of a MQTT Session Subscription object in an idempotent manner."
notes:
- >
    Depending on the Broker version, a QoS=1 subscription results in the 'magic queue' ('#mqtt/{client_id}/{number}') to
    have ingress / egress ON or OFF. Module uses SEMP v1 <no><shutdown><full/> to ensure they are ON.
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/mqttSession/createMsgVpnMqttSessionSubscription)."

options:
  name:
    description: The subscription topic. Maps to 'subscriptionTopic' in the API.
    type: str
    required: true
    aliases: [mqtt_session_subscription_topic, topic]
  mqtt_session_client_id:
    description: The MQTT session client id. Maps to 'mqttSessionClientId' in the API.
    type: str
    required: true
    aliases: [client_id, client]

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.settings
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.virtual_router

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
    solace_mqtt_session:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
    solace_mqtt_session_subscription:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
tasks:
  - name: create session
    solace_mqtt_session:
        name: foo
        state: present

  - name: add subscription
    solace_mqtt_session_subscription:
        virtual_router: "{{ virtual_router }}"
        client_id: foo-client
        topic: "test/v1/event/+"
        state: present

  - name: update subscription
    solace_mqtt_session_subscription:
        virtual_router: "{{ virtual_router }}"
        client_id: foo-client
        topic: "test/+/#"
        settings:
          subscriptionQos: 1
        state: present

  - name: delete subscription
    solace_mqtt_session_subscription:
        virtual_router: "{{ virtual_router }}"
        client_id: "{{ mqtt_session_item.mqttSessionClientId }}"
        topic: "test/v1/#"
        state: absent

  - name: delete session
    solace_mqtt_session:
        name: foo
        state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceMqttSessionSubscriptionTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'subscriptionTopic'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['virtual_router'], params['mqtt_session_client_id'], params['name']]

    def get_func(self, vpn_name, virtual_router, mqtt_session_client_id, subscription_topic):
        # GET /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([mqtt_session_client_id, virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'mqttSessions', uri_ext, 'subscriptions', subscription_topic]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, virtual_router, mqtt_session_client_id, subscription_topic, settings=None):
        # POST  /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions
        data = {
            self.OBJECT_KEY: subscription_topic,
            'mqttSessionVirtualRouter': virtual_router,
            'mqttSessionClientId': mqtt_session_client_id
        }
        data.update(settings if settings else {})
        uri_ext = ','.join([mqtt_session_client_id, virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'mqttSessions', uri_ext, 'subscriptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, virtual_router, mqtt_session_client_id, subscription_topic, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([mqtt_session_client_id, virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'mqttSessions', uri_ext, 'subscriptions', subscription_topic]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, virtual_router, mqtt_session_client_id, subscription_topic):
        # DELETE /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([mqtt_session_client_id, virtual_router])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'mqttSessions', uri_ext, 'subscriptions', subscription_topic]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', aliases=['topic'], required=True),
        mqtt_session_client_id=dict(type='str', aliases=['client_id'], required=True),
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_virtual_router())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceMqttSessionSubscriptionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
