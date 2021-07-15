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
short_description: client profile
description:
- "Configure a Client Profile object. Allows addition, removal and configuration of Client Profile objects on Solace Brokers in an idempotent manner."
- "Supports Solace Cloud Brokers as well as Solace Standalone Brokers."
- "Solace Cloud: Polls periodically until Client Profile created and only then returns."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile"
- "Module Solace Cloud API: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_client_profiles.htm"
options:
  name:
    description: Name of the client profile. Maps to 'clientProfileName' in the API.
    type: str
    required: true
    aliases: [client_profile, client_profile_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_get_client_profiles
author:
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
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:
  - name: Delete Client Profile
    solace_client_profile:
        name: foo
        state: absent

  - name: Create Client Profile
    solace_client_profile:
        name: foo
        state: present

  - name: Update Client Profile
    solace_client_profile:
        name: foo
        settings:
          allowGuaranteedMsgSendEnabled: true
          allowGuaranteedMsgReceiveEnabled: true
          allowGuaranteedEndpointCreateEnabled: true
        state: present
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceClientProfileTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'clientProfileName'
    OPERATION = 'clientProfile'

    # TODO: check these defaults
    # and are they bools or strings?

    # # similar settings to solace cloud console
    # SOLACE_CLOUD_DEFAULTS = {
    #     'allowBridgeConnectionsEnabled': True,
    #     'allowGuaranteedEndpointCreateEnabled': True,
    #     'allowGuaranteedMsgReceiveEnabled': True,
    #     'allowGuaranteedMsgSendEnabled': True,
    #     'allowSharedSubscriptionsEnabled': True,
    #     'allowTransactedSessionsEnabled': True,
    #     'allowUseCompression': True,
    #     'elidingEnabled': True,
    #     'replicationAllowClientConnectWhenStandbyEnabled': False,
    #     # 'tlsAllowDowngradeToPlainTextEnabled': True
    # }

    SOLACE_CLOUD_DEFAULTS = {
        "allowGuaranteedMsgSendEnabled": "true",
        "allowGuaranteedMsgReceiveEnabled": "true",
        "allowUseCompression": "true",
        "replicationAllowClientConnectWhenStandbyEnabled": "false",
        "allowTransactedSessionsEnabled": "true",
        "allowBridgeConnectionsEnabled": "true",
        "allowGuaranteedEndpointCreateEnabled": "true",
        "allowSharedSubscriptionsEnabled": True,
        "apiQueueManagementCopyFromOnCreateName": "",
        "apiTopicEndpointManagementCopyFromOnCreateName": "",
        "serviceWebInactiveTimeout": "30",
        "serviceWebMaxPayload": "1000000",
        "maxConnectionCountPerClientUsername": "100",
        "serviceSmfMaxConnectionCountPerClientUsername": "1000",
        "serviceWebMaxConnectionCountPerClientUsername": "1000",
        "maxEndpointCountPerClientUsername": "100",
        "maxEgressFlowCount": "100",
        "maxIngressFlowCount": "100",
        "maxSubscriptionCount": "1000",
        "maxTransactedSessionCount": "100",
        "maxTransactionCount": "500",
        "queueGuaranteed1MaxDepth": "20000",
        "queueGuaranteed1MinMsgBurst": 66000,
        "queueDirect1MaxDepth": "20000",
        "queueDirect1MinMsgBurst": "4",
        "queueDirect2MaxDepth": "20000",
        "queueDirect2MinMsgBurst": "4",
        "queueDirect3MaxDepth": "20000",
        "queueDirect3MinMsgBurst": "4",
        "queueControl1MaxDepth": "20000",
        "queueControl1MinMsgBurst": "4",
        "tcpCongestionWindowSize": "2",
        "tcpKeepaliveCount": "5",
        "tcpKeepaliveIdleTime": "3",
        "tcpKeepaliveInterval": "1",
        "tcpMaxSegmentSize": "1460",
        "tcpMaxWindowSize": "256",
        "elidingDelay": 0,
        "elidingEnabled": True,
        "elidingMaxTopicCount": 256,
        "rejectMsgToSenderOnNoSubscriptionMatchEnabled": False,
        "tlsAllowDowngradeToPlainTextEnabled": True,
        "eventClientProvisionedEndpointSpoolUsageThreshold": {
            "setPercent": "80",
            "clearPercent": "60"
        }
    }

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def _type_conversion(self, d):
        for k, i in d.items():
            t = type(i)
            if t == int or t == float:
                d[k] = str(i)
            elif t == bool:
                # False is not a string, only True
                if not i:
                    pass
                # if k == 'allowSharedSubscriptionsEnabled' or k == 'elidingEnabled':
                #     pass
                else:
                    d[k] = str(i).lower()
        return d

    def normalize_new_settings(self, new_settings) -> dict:
        if new_settings:
            self._type_conversion(new_settings)
        return new_settings

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['name']]

    def _compose_request_body(self, operation: str, operation_type: str, settings: dict) -> dict:
        return {
            'operation': operation,
            operation_type: settings
        }

    def _get_func_solace_cloud(self, vpn_name, client_profile_name):
        # GET services/{paste-your-serviceId-here}/clientProfiles/{{clientProfileName}}
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES,
                      service_id, 'clientProfiles', client_profile_name]
        return self.solace_cloud_api.get_object_settings(self.get_config(), path_array)

    def get_func(self, vpn_name, client_profile_name):
        if self.get_config().is_solace_cloud():
            return self._get_func_solace_cloud(vpn_name, client_profile_name)
        # GET /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def _create_func_solace_cloud(self, vpn_name, client_profile_name, settings):
        module_op = SolaceTaskOps.OP_CREATE_OBJECT
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        data.update(self.SOLACE_CLOUD_DEFAULTS)
        data.update(settings if settings else {})

        # import logging
        # import json
        # logging.debug(f">>>>>data=\n{json.dumps(data, indent=2)}")

        # data = {
        #     self.OBJECT_KEY: client_profile_name
        # }
        # data.update(self.TEST_SETTINGS)

        body = self._compose_request_body(operation='create',
                                          operation_type=self.OPERATION, settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES,
                      service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=body, module_op=module_op)

    def create_func(self, vpn_name, client_profile_name, settings=None):
        if self.get_config().is_solace_cloud():
            return self._create_func_solace_cloud(vpn_name, client_profile_name, settings)
        # POST /msgVpns/{msgVpnName}/clientProfiles
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def _update_func_solace_cloud(self, vpn_name, client_profile_name, settings, delta_settings):
        module_op = SolaceTaskOps.OP_UPDATE_OBJECT
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        # for POST: add the current_settings, override with delta_settings
        current_settings = self._get_func_solace_cloud(vpn_name,
                                                       client_profile_name)
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
        body = self._compose_request_body(operation='update',
                                          operation_type=self.OPERATION, settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES,
                      service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=body, module_op=module_op)

    def update_func(self, vpn_name, client_profile_name, settings=None, delta_settings=None):
        if self.get_config().is_solace_cloud():
            return self._update_func_solace_cloud(vpn_name, client_profile_name, settings, delta_settings)
        # PATCH /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def _delete_func_solace_cloud(self, vpn_name, client_profile_name):
        module_op = SolaceTaskOps.OP_UPDATE_OBJECT
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        body = self._compose_request_body(operation='delete',
                                          operation_type=self.OPERATION, settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES,
                      service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=body, module_op=module_op)

    def delete_func(self, vpn_name, client_profile_name):
        if self.get_config().is_solace_cloud():
            return self._delete_func_solace_cloud(vpn_name, client_profile_name)
        # DELETE /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'clientProfiles', client_profile_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', aliases=[
                  'client_profile', 'client_profile_name'], required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceClientProfileTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
