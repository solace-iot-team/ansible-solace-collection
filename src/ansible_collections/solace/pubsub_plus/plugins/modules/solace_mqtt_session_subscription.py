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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule
if not sc.HAS_IMPORT_ERROR:
    import xmltodict


class SolaceMqttSessionSubscriptionTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'subscriptionTopic'

    def __init__(self, module):
        sc.module_fail_on_import_error(module, sc.HAS_IMPORT_ERROR, sc.IMPORT_ERR_TRACEBACK)
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['mqtt_session_client_id'], self.module.params['virtual_router']]

    def lookup_item(self):
        return self.module.params['name']

    def get_magic_queue(self, where_name, vpn):
        request = {
            'rpc': {
                'show': {
                    'queue': {
                        'name': where_name,
                        'vpn-name': vpn,
                    }
                }
            }
        }
        list_path_array = ['rpc-reply', 'rpc', 'show', 'queue', 'queues', 'queue']
        return sc.execute_sempv1_get_list(self.solace_config, request, list_path_array)

    def execute_queue_no_shutdown(self, queue_name, vpn):
        request = {
            'rpc': {
                'message-spool': {
                    'vpn-name': vpn,
                    'queue': {
                        'name': queue_name,
                        'no': {
                            'shutdown': {
                                'full': None
                            }
                        }
                    }
                }
            }
        }
        xml_data = xmltodict.unparse(request)
        ok, semp_resp = sc.make_sempv1_post_request(self.solace_config, xml_data)
        if not ok:
            resp = dict(request=xml_data, response=semp_resp)
        else:
            resp = semp_resp
        return ok, resp

    def get_func(self, solace_config, vpn, client_id, virtual_router, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, client_id, virtual_router, topic, settings=None):
        # POST /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions
        defaults = {
            'msgVpnName': vpn,
            'mqttSessionClientId': client_id,
            'mqttSessionVirtualRouter': virtual_router
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: topic
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS]
        ok, resp = su.make_post_request(solace_config, path_array, data)
        if not ok:
            return False, resp
        # QoS==1? ==> ensure magic queue is ON/ON
        if settings and settings['subscriptionQos'] == 1:
            # search = "#mqtt/" + client_id + "/does-not-exist"
            search = "#mqtt/" + client_id + "/*"
            ok_gmq, resp_gmq = self.get_magic_queue(search, vpn)
            if not ok_gmq:
                resp['error'] = dict(
                    msg=f"error retrieving magic queue: {search}",
                    details=resp_gmq
                )
                return False, resp
            elif len(resp_gmq) != 1:
                resp['error'] = dict(
                    msg=f"could not find magic queue: {search}"
                )
                return False, resp
            # make sure magic queue is ON/ON
            # depending on Broker version, no-shutdown is allowed or not.
            # here: ignore error
            mq_name = resp_gmq[0]['name']
            _ok_no_shut, _resp_no_shut = self.execute_queue_no_shutdown(mq_name, vpn)
            # if not ok_no_shut:
            #     resp['error'] = dict(
            #         msg="error executing no-shutdown for magic queue: {}".format(mq_name),
            #         details=resp_no_shut
            #     )
            #     return False, resp
        return True, resp

    def update_func(self, solace_config, vpn, client_id, virtual_router, lookup_item_value, settings=None):
        # PATCH /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, client_id, virtual_router, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    module_args = dict(
        name=dict(type='str', aliases=['mqtt_session_subscription_topic', 'topic'], required=True),
        mqtt_session_client_id=dict(type='str', aliases=['client_id', 'client'], required=True),
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_virtual_router())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceMqttSessionSubscriptionTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
