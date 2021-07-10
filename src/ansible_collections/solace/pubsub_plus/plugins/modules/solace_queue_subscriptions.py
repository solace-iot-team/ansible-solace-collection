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

TODO

module: solace_queue_subscription
short_description: subscription on a queue
description:
- "Configure a Subscription object on a Queue. Allows addition, removal and configuration of Subscription objects on a queue."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue/createMsgVpnQueueSubscription"
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
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace_queue
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
    topic: "foo/bar"
    state: present

- name: remove subscription
  solace_queue_subscription:
    queue: foo
    topic: "foo/bar"
    state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask, SolaceTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceSempV2PagingGetApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError, SolaceInternalErrorAbstractMethod, SolaceParamsValidationError, SolaceNoModuleStateSupportError
from ansible.module_utils.basic import AnsibleModule


class SolaceBrokerCRUDListTask(SolaceBrokerCRUDTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        self.sempv2_get_paging_api = SolaceSempV2PagingGetApi(
            module, self.is_supports_paging())
        self.existing_key_list = None
        self.response_list = []
        # self.changed = False

    def get_objects_path_array(self) -> list:
        raise SolaceInternalErrorAbstractMethod()

    def get_objects_result_data_object_key(self) -> str:
        raise SolaceInternalErrorAbstractMethod()

    def get_crud_args(self, object_key) -> list:
        raise SolaceInternalErrorAbstractMethod()

    def is_supports_paging(self):
        return True

    def get_objects(self) -> list:
        objects = self.sempv2_get_paging_api.get_all_objects_from_config_api(
            self.get_config(),
            self.get_objects_path_array())
        # import logging
        # import json
        # logging.debug(">>>>>>>> objects=\n%s", json.dumps(objects, indent=2))
        return objects

    def get_object_key_list(self, object_key) -> list:
        objects = self.get_objects()
        object_key_list = [d['data'][object_key] for d in objects]
        return object_key_list

    def do_task(self):
        self.validate_params()
        params = self.get_config().get_params()
        is_check_mode = self.get_module().check_mode
        self.existing_key_list = self.get_object_key_list(
            self.get_objects_result_data_object_key())
        import logging
        import json
        logging.debug(">>>>>>>> existing_object_key_list=\n%s",
                      json.dumps(self.existing_key_list, indent=2))

        # raise SolaceInternalError("continue here")

        target_key_list = params['names']
        import logging
        import json
        logging.debug(">>>>>>>> target_key_list=\n%s",
                      json.dumps(target_key_list, indent=2))

        # TODO: use states to:
        # TODO: compose create action list
        # TODO: compose delete action list
        # TODO: execute both ==> one execution code only

        state_object_combination_error = False
        new_state = params['state']
        for target_key in target_key_list:
            crud_args = self.get_crud_args(target_key)
            target_key_exists = target_key in self.existing_key_list
            import logging
            import json
            logging.debug(
                f">>>>>>>> target_key_exists={target_key_exists}, target_key={target_key}, self.existing_key_list={json.dumps(self.existing_key_list, indent=2)}")
            if new_state == 'present' and not target_key_exists:
                self.changed = True
                if not is_check_mode:
                    _response = self.create_func(*crud_args)
                    self.response_list.append({"added": target_key})
            elif new_state == 'present' and target_key_exists:
                pass
            elif new_state == 'absent' and target_key_exists:
                self.changed = True
                if not is_check_mode:
                    _response = self.delete_func(*crud_args)
                    response = _response if _response != {} else {"deleted": target_key}
                    self.response_list.append(response)
            elif new_state == 'absent' and not target_key_exists:
                pass
            elif new_state == 'present_only' and target_key_exists:
                pass
            elif new_state == 'present_only' and not target_key_exists:
                self.changed = True
                if not is_check_mode:
                    _response = self.create_func(*crud_args)
                    self.response_list.append({"added": target_key})
            elif new_state == 'present_only':
                pass
            else:
                state_object_combination_error = True

        if new_state == 'present_only':
            for existing_key in self.existing_key_list:
                crud_args = self.get_crud_args(existing_key)
                if new_state == 'present_only' and existing_key not in target_key_list:
                    self.changed = True
                    if not is_check_mode:
                        _response = self.delete_func(*crud_args)
                        response = _response if _response != {} else {"deleted": existing_key}
                        self.response_list.append(response)
                elif new_state == 'present_only' and existing_key in target_key_list:
                    pass
                else:
                    state_object_combination_error = True

        if state_object_combination_error:
            raise SolaceInternalError([
                "unsupported state / object combination",
                f"state={new_state}",
                f"target_key_list={target_key_list}",
                f"existing_key_list={self.existing_key_list}"
            ])

        result = self.create_result(rc=0, changed=self.changed)
        result['response'] = self.response_list
        return None, result


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

    def get_crud_args(self, subscription_topic):
        params = self.get_module().params
        return [params['msg_vpn'], params['queue_name'], subscription_topic]

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
        names=dict(type='list', required=True, aliases=[
            'topics', 'subscription_topics']),
        queue_name=dict(type='str', required=True, aliases=['queue']),
        state=dict(type='str', default='present', choices=[
                   'absent', 'present', 'present_only'])
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
