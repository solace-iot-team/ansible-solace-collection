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
module: solace_client_profile

TODO: rework doc

short_description: client profile

description:
- "Configure a Client Profile object. Allows addition, removal and configuration of Client Profile objects on Solace Brokers in an idempotent manner."
- "Supports Solace Cloud Brokers as well as Solace Standalone Brokers."

notes:
- "Solace Cloud: Polls periodically until Client Profile created and only then returns."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile)."
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_client_profiles.htm)."

seealso:
- module: solace_get_client_profiles

options:
  name:
    description: Name of the client profile. Maps to 'clientProfileName' in the API.
    type: str
    required: true
    aliases: [client_profile, client_profile_name]

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.settings
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.solace_cloud_config

author:
  - Mark Street (@mkst)
  - Swen-Helge Huber (@ssh)
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
    solace_client_profile:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
        solace_cloud_api_token: "{{ solace_cloud_api_token | default(omit) }}"
        solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:

  - name: Delete Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        state: absent

  - name: Create Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        state: present

  - name: Update Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        settings:
          allowGuaranteedMsgSendEnabled: true
          allowGuaranteedMsgReceiveEnabled: true
          allowGuaranteedEndpointCreateEnabled: true
        state: present

  - name: Delete Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 / Solace Cloud request.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceClientProfileTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'clientProfileName'
    OPERATION = 'clientProfile'
    SOLACE_CLOUD_DEFAULTS = {
        'allowTransactedSessionsEnabled': False,
        'allowBridgeConnectionsEnabled': False,
        'allowGuaranteedEndpointCreateEnabled': False,
        'allowSharedSubscriptionsEnabled': False,
        'allowGuaranteedMsgSendEnabled': False,
        'allowGuaranteedMsgReceiveEnabled': False,
        'elidingEnabled': False
    }

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['name']]

    def _get_func_solace_cloud(self, vpn_name, client_profile_name):
        # GET services/{paste-your-serviceId-here}/clientProfiles/{{clientProfileName}}
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, 'clientProfiles', client_profile_name]
        return self.solace_cloud_api.get_object_settings(self.get_config(), path_array)

    def get_func(self, vpn_name, client_profile_name):
        if self.get_config().is_solace_cloud():
            return self._get_func_solace_cloud(vpn_name, client_profile_name)
        # GET /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def _create_func_solace_cloud(self, vpn_name, client_profile_name, settings):
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        data.update(self.SOLACE_CLOUD_DEFAULTS)
        data.update(settings if settings else {})
        body = self.solace_cloud_api.compose_request_body(operation='create', operation_type=self.OPERATION, settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, body)

    def create_func(self, vpn_name, client_profile_name, settings=None):
        if self.get_config().is_solace_cloud():
            return self._create_func_solace_cloud(vpn_name, client_profile_name, settings)
        # POST /msgVpns/{msgVpnName}/clientProfiles
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'clientProfiles']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def _update_func_solace_cloud(self, vpn_name, client_profile_name, settings, delta_settings):
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        # for POST: add the current_settings, override with delta_settings
        current_settings = self._get_func_solace_cloud(vpn_name, client_profile_name)
        # inconsistency in Solace Cloud API:
        # boolean values:
        #   create: must be provided as boolean (true or false)
        #   get: returns it as null if it was false
        #   update: must be provided as true or false
        for key in self.SOLACE_CLOUD_DEFAULTS:
            if key in current_settings and current_settings[key] is None:
                current_settings[key] = False
        mandatory = {
            self.OBJECT_KEY: client_profile_name
        }
        data = current_settings        
        data.update(mandatory)
        data.update(settings if settings else {})
        body = self.solace_cloud_api.compose_request_body(operation='update', operation_type=self.OPERATION, settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, body)

    def update_func(self, vpn_name, client_profile_name, settings=None, delta_settings=None):
        if self.get_config().is_solace_cloud():
            return self._update_func_solace_cloud(vpn_name, client_profile_name, settings, delta_settings)
        # PATCH /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def _delete_func_solace_cloud(self, vpn_name, client_profile_name):
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        body = self.solace_cloud_api.compose_request_body(operation='delete', operation_type=self.OPERATION, settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, body)

    def delete_func(self, vpn_name, client_profile_name):
        if self.get_config().is_solace_cloud():
            return self._delete_func_solace_cloud(vpn_name, client_profile_name)
        # DELETE /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', aliases=['client_profile', 'client_profile_name'], required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceClientProfileTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
