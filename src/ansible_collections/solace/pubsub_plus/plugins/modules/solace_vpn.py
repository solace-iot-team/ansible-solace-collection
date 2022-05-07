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
module: solace_vpn
short_description: vpn
description:
- "Allows addition, removal and configuration of VPN objects in an idempotent manner."
- "Supports Solace Cloud and self-hosted brokers. Splits the settings into two calls, the Solace Cloud API and the SEMP V2 API."
- "Use B(settings) arguments and values from the SEMP V2 documentation."
notes:
- "You cannot create or delete a VPN on a Solace Cloud Service."
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn"
- "Module Solace Cloud API: no documentation available"
options:
  name:
    description: Name of the vpn. Maps to 'msgVpnName' in the API.
    required: true
    type: str
    aliases: [msg_vpn_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_get_vpns
- module: solace_get_vpn_clients
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
  solace_vpn:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
  solace_get_vpns:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
tasks:
- name: get 1 vpn config
  solace_get_vpns:
  register: result

- set_fact:
    msg_vpn_name: "{{ result.result_list[0].data.msgVpnName  }}"
    current_settings: "{{ result.result_list[0].data }}"

- name: self-hosted broker only
  block:
    - name: create new vpn if not solace cloud
      solace_vpn:
        name: foo
        state: present

    - name: delete new vpn if not solace cloud
      solace_vpn:
        name: foo
        state: absent
  when: broker_type != 'solace_cloud'

- name: update vpn
  solace_vpn:
    name: "{{ msg_vpn_name }}"
    settings:
      authenticationBasicType: internal
      eventLargeMsgThreshold: 100
    state: present
'''

RETURN = '''
response:
    description: The responses from the Solace Cloud and/or Sempv2 requests.
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError, SolaceModuleUsageError
from ansible.module_utils.basic import AnsibleModule


class SolaceVpnTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'msgVpnName'
    SOLACE_CLOUD_SETTINGS = {
        'authenticationBasicEnabled': False,
        'authenticationBasicType': ['LDAP', 'INTERNAL', 'NONE'],
        'authenticationClientCertEnabled': False,
        'authenticationClientCertValidateDateEnabled': False,
        'authenticationOauthEnabled': False,
        'authenticationClientCertAllowApiProvidedUsernameEnabled': False,
        'authenticationClientCertUsernameSource': ['COMMON_NAME', 'SUBJECT_ALTERNATE_NAME_MSUPN']
    }

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        self.solace_cloud_api = SolaceCloudApi(module)
        self.current_settings = None

    def validate_params(self):
        pass

    def get_args(self):
        params = self.get_module().params
        return [params['name']]

    def get_settings_arg_name(self) -> str:
        return 'sempv2_settings'

    def normalize_current_settings(self, current_settings: dict, new_settings: dict) -> dict:
        if self.get_config().is_solace_cloud():
            # remember current_settings for update call: it needs it
            self.current_settings = current_settings
        return current_settings

    def _remove_solace_cloud_keys(self, settings):
        _settings = SolaceUtils.deep_copy(settings)
        for key in self.SOLACE_CLOUD_SETTINGS.keys():
            _settings.pop(key, None)
        return _settings

    def _convert_new_settings_to_solace_cloud_api(self, new_settings):
        val = new_settings.get('authenticationBasicType', None)
        if val:
            new_val = val.upper().replace('-', '_')
            new_settings['authenticationBasicType'] = new_val
        val = new_settings.get('authenticationClientCertUsernameSource', None)
        if val:
            new_val = val.upper().replace('-', '_')
            new_settings['authenticationClientCertUsernameSource'] = new_val
        return new_settings

    def _normalize_new_settings_solace_cloud(self, new_settings):
        val = new_settings.get('authenticationBasicType', None)
        if val:
            new_val = val.lower().replace('_', '-')
            new_settings['authenticationBasicType'] = new_val
        val = new_settings.get('authenticationClientCertUsernameSource', None)
        if val:
            new_val = val.lower().replace('_', '-')
            new_settings['authenticationClientCertUsernameSource'] = new_val
        return new_settings

    def normalize_new_settings(self, new_settings) -> dict:
        # solace cloud and self-hosted broker return the same types
        if new_settings:
            SolaceUtils.type_conversion(new_settings, False)
            if self.get_config().is_solace_cloud():
                new_settings = self._normalize_new_settings_solace_cloud(
                    new_settings)
        return new_settings

    def get_func(self, vpn_name):
        # notes:
        # - solace-cloud: could get the settings via: GET the service: msgVpnAttributes. but looks like they are the same
        # GET /msgVpns/{msgVpnName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, settings=None):
        if self.get_config().is_solace_cloud():
            raise SolaceModuleUsageError(
                self.get_module()._name,
                self.get_module().params['state'],
                "cannot create a new message vpn on a Solace Cloud service"
            )
        # POST /msgVpns
        data = {
            self.OBJECT_KEY: vpn_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def _update_func_solace_cloud(self, vpn_name, settings, delta_settings):
        # extract solace cloud api settings from settings -> send via solace cloud api
        # rest: send via sempv2 api
        _solace_cloud_api_settings = {}
        for key in self.SOLACE_CLOUD_SETTINGS.keys():
            _solace_cloud_api_settings.update({
                key: settings[key] if key in settings else self.current_settings[key]
            })
        _solace_cloud_api_settings = self._convert_new_settings_to_solace_cloud_api(
            _solace_cloud_api_settings)
        # POST: services/{service-id}}/requests/updateAuthenticationRequests
        module_op = SolaceTaskOps.OP_UPDATE_OBJECT
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()), SolaceCloudApi.API_SERVICES,
                      service_id, SolaceCloudApi.API_REQUESTS, 'updateAuthenticationRequests']
        solace_cloud_resp = self.solace_cloud_api.make_service_post_request(
            self.get_config(),
            path_array,
            service_id,
            json_body=_solace_cloud_api_settings,
            module_op=module_op
        )
        # check for sempv2 settings, extract and send
        _sempv2_api_settings = self._remove_solace_cloud_keys(settings)
        sempv2_resp = {}
        if _sempv2_api_settings:
            sempv2_resp = self._update_func_sempv2(
                vpn_name, _sempv2_api_settings)
        resp = {
            'solace-cloud': solace_cloud_resp,
            'semp-v2': sempv2_resp
        }
        return resp

    def _update_func_sempv2(self, vpn_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def update_func(self, vpn_name, settings=None, delta_settings=None):
        if self.get_config().is_solace_cloud():
            return self._update_func_solace_cloud(vpn_name, settings, delta_settings)
        return self._update_func_sempv2(vpn_name, settings, delta_settings)

    def delete_func(self, vpn_name):
        if self.get_config().is_solace_cloud():
            raise SolaceModuleUsageError(self.get_module()._name, self.get_module(
            ).params['state'], "cannot delete a message vpn on a Solace Cloud service")
        # DELETE /msgVpns/{msgVpnName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['msg_vpn_name'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceVpnTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
