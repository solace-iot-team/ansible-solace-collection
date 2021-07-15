#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Mike O'Brien, <mike.obrien@solace.com>
# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_replay_log
short_description: replay log
description:
- "Configure a Replay Log object on a Message Vpn. Allows addition, removal and configuration of Replay Log objects in an idempotent manner."
- "Note: Solace Cloud currently does not support creating, deleting, updating Replay Log objects. Module will return an error."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/replayLog"
options:
  name:
    description: Name of the replayLog. Maps to 'replayLogName' in the API.
    required: true
    type: str
    aliases: [replay_log_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_get_replay_logs
- module: solace_replay_log_trim_logged_msgs
author:
- Mike O'Brien (@mikeo)
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
  solace_replay_log:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:
- name: add replay log
  solace_replay:
    name: bar
    state: present

- name: update replay log
  solace_replay:
    name: bar
    settings:
      egressEnabled: true
      ingressEnabled: true
      maxSpoolUsage: 10
    state: present

- name: remove replay log
  solace_replay:
    name: bar
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

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible.module_utils.basic import AnsibleModule


class SolaceReplayLogTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'replayLogName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['name']]

    def get_func(self, vpn_name, replay_log_name):
        # GET /msgVpns/{msgVpnName}/replayLogs/{replayLogName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'replayLogs', replay_log_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def _create_func_solace_cloud(self, vpn_name, replay_log_name, settings=None):
        raise SolaceError("creating replayLog in Solace Cloud not supported")

    def create_func(self, vpn_name, replay_log_name, settings=None):
        if self.get_config().is_solace_cloud():
            return self._create_func_solace_cloud(vpn_name, replay_log_name, settings)
        # POST /msgVpns/{msgVpnName}/replayLogs
        data = {
            'msgVpnName': vpn_name,
            self.OBJECT_KEY: replay_log_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'replayLogs']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, replay_log_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/replayLogs/{replayLogName}
        # solace cloud complains about using the exact types
        converted_settings = SolaceUtils.deep_dict_convert_strs_to_types(
            settings)
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'replayLogs', replay_log_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, converted_settings)

    def _delete_func_solace_cloud(self, vpn_name, replay_log_name):
        raise SolaceError("deleting replayLog in Solace Cloud not supported")

    def delete_func(self, vpn_name, replay_log_name):
        if self.get_config().is_solace_cloud():
            return self._delete_func_solace_cloud(vpn_name, replay_log_name)
        # DELETE /msgVpns/{msgVpnName}/replayLogs/{replayLogName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'replayLogs', replay_log_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['replay_log_name'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceReplayLogTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
