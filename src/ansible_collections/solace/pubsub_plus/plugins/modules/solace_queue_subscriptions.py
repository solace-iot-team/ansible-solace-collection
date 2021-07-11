#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_queue_subscriptions
short_description: list of subscriptions on a queue
description:
- "Configure a list of Subscription objects on a Queue in a single transaction."
- "Allows addition and removal of a list of Subscription objects as well as replacement of all existing Subscription objects on a queue."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates Subscription object list."
- "Reports which topics were added, deleted and omitted (duplicates). In case of an error, reports the invalid Subscription object."
- "To delete all Subscription objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue/createMsgVpnQueueSubscription"
options:
  names:
    description: The subscription topic. Maps to 'subscriptionTopic' in the API.
    required: true
    type: list
    aliases: [topics, subscription_topics]
    elements: str
  queue:
    description: The queue. Maps to 'queueName' in the API.
    required: true
    type: str
    aliases: [queue_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace_queue
- module: solace_queue_subscription
- module: solace_get_queue_subscriptions
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
    solace_queue:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_queue_subscriptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
    solace_get_queue_subscriptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      reverse_proxy: "{{ semp_reverse_proxy | default(omit) }}"
  tasks:
  - name: create queue
    solace_queue:
      name: q/foo
      state: present

  - name: add list of subscriptions
    solace_queue_subscriptions:
      queue_name: q/foo
      subscription_topics:
        - topic-1
        - topic-2
      state: present

  - name: get subscriptions
    solace_get_queue_subscriptions:
      queue_name: q/foo

  - name: add second list of subscriptions
    solace_queue_subscriptions:
      queue_name: q/foo
      subscription_topics:
        - topic-3
        - topic-4
      state: present

  - name: get subscriptions
    solace_get_queue_subscriptions:
      queue_name: q/foo

  - name: replace subscriptions
    solace_queue_subscriptions:
      queue_name: q/foo
      subscription_topics:
        - new-topic-1
        - new-topic-2
      state: exactly

  - name: get subscriptions
    solace_get_queue_subscriptions:
      queue_name: q/foo

  - name: handle duplicate subscriptions
    solace_queue_subscriptions:
      queue_name: q/foo
      subscription_topics:
        - duplicate-topic
        - duplicate-topic
      state: exactly

  - name: get subscriptions
    solace_get_queue_subscriptions:
      queue_name: q/foo

  - name: delete all subscriptions
    solace_queue_subscriptions:
      queue_name: q/foo
      subscription_topics: null
      state: exactly

  - name: get subscriptions
    solace_get_queue_subscriptions:
      queue_name: q/foo
'''

RETURN = '''
response:
    description: The response of the operation.
    type: dict
    returned: always
    sample:
      response:
      - added: duplicate-topic
      - deleted: new-topic-1
      - deleted: new-topic-2
      - duplicate: duplicate-topic
      - error: /error-topic
msg:
    description: The response from the HTTP call in case of error.
    type: dict
    returned: error
rc:
    description: Return code. rc=0 on success, rc=1 on error.
    type: int
    returned: always
    sample:
        success:
            rc: 0
        error:
            rc: 1
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDListTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceQueueSubscriptionsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'subscriptionTopic'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'queues', params['queue_name'], 'subscriptions']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], params['queue_name'], object_key]

    def create_func(self, vpn_name, queue_name, subscription_topic, settings=None):
        # POST /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions
        data = {
            self.OBJECT_KEY: subscription_topic
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'queues', queue_name, 'subscriptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, queue_name, subscription_topic):
        # DELETE /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions/{subscriptionTopic}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'queues', queue_name, 'subscriptions', subscription_topic]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        queue_name=dict(type='str', required=True, aliases=['queue']),
        names=dict(type='list',
                   required=True,
                   aliases=['topics', 'subscription_topics'],
                   elements='str'
                   ),
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud_list())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceQueueSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
