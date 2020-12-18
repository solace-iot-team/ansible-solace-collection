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
module: solace_queue_subscription

short_description: subscription on a queue

description:
- "Configure a Subscription Object on a Queue.. Allows addition, removal and configuration of subscription objects on a queue."

notes:
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue/createMsgVpnQueueSubscription)."

options:
  name:
    description: The subscription topic. Maps to 'subscriptionTopic' in the API.
    required: true
    type: str
    aliases: [topic, subscription_topic]
  queue:
    description: The queue. Maps to 'queueName' in the API.
    required: true
    type: str
    aliases: [queue_name]

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
    solace_queue:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
    solace_queue_subscription:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
tasks:
  - name: create queue
    solace_queue:
        name: foo
        state: present

  - name: add subscription
    solace_queue_subscription:
        queue: foo
        name: "foo/bar"
        state: present

  - name: remove subscription
    solace_queue_subscription:
        queue: foo
        name: "foo/bar"
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


class SolaceSubscriptionTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'subscriptionTopic'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['queue']]

    def get_func(self, solace_config, vpn, queue, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions/{subscriptionTopic}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.QUEUES, queue, su.SUBSCRIPTIONS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, queue, topic, settings=None):
        # POST /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions
        defaults = {}
        mandatory = {
            self.LOOKUP_ITEM_KEY: topic
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.QUEUES, queue, su.SUBSCRIPTIONS]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, queue, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions/{subscriptionTopic}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.QUEUES, queue, su.SUBSCRIPTIONS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['topic', 'subscription_topic']),
        queue=dict(type='str', required=True, aliases=['queue_name']),
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

    solace_topic_task = SolaceSubscriptionTask(module)
    result = solace_topic_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
