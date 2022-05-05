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
module: solace_cloud_client_profile
short_description: client profile for Solace Cloud
description:
- "Configure a Client Profile object in Solace Cloud. Allows addition, removal and configuration of Client Profile objects in an idempotent manner."
- "The settings for the Solace Cloud API are the same as for the SEMPV2 API."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile"
- "Module Solace Cloud API: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_client_profiles.htm"
- "Known Issue: Solace Cloud API does not return values for 'eventClientProvisionedEndpointSpoolUsageThreshold'. To ensure correct settings, add them to the `settings` dict."
options:
  name:
    description: Name of the client profile. Maps to 'clientProfileName' in the API.
    type: str
    required: true
    aliases: [client_profile, client_profile_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.broker_config_solace_cloud_mandatory
- solace.pubsub_plus.solace.solace_cloud_settings
seealso:
- module: solace_client_profile
- module: solace_get_client_profiles
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
  solace_cloud_client_profile:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
  solace_get_client_profiles:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:

- name: exit if not solace cloud
  meta: end_play
  when: broker_type != 'solace_cloud'

- name: create default profile
  solace_cloud_client_profile:
    name: foo
    state: present

- name: update
  solace_cloud_client_profile:
    name: foo
    settings:
      allowGuaranteedEndpointCreateEnabled: false
      allowGuaranteedMsgSendEnabled: false
    state: present

- name: get profiles
  solace_get_client_profiles:
    query_params:
      where:
        - "clientProfileName==foo"
      select:
        - "clientProfileName"

- name: delete
  solace_cloud_client_profile:
    name: foo
    state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Cloud API request.
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig, SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError
from ansible.module_utils.basic import AnsibleModule
import re


class SolaceCloudClientProfileTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'clientProfileName'
    OPERATION = 'clientProfile'

    CREATE_DEFAULTS = {
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
        self.solace_cloud_api = SolaceCloudApi(module)

    def _adjust_settings_for_create(self, new_settings) -> dict:
        # placeholder in case customized data type transformation required for create operation
        return new_settings if new_settings else {}

    def _adjust_settings_for_update(self, new_settings, get_settings) -> dict:
        # add mandatory
        if 'eventClientProvisionedEndpointSpoolUsageThreshold' not in new_settings:
            new_settings['eventClientProvisionedEndpointSpoolUsageThreshold'] = get_settings['eventClientProvisionedEndpointSpoolUsageThreshold']
        return new_settings

    def get_settings_type_conversion(self, d):
        # everything is a string or null

        # import logging
        # import json
        # logging.debug(f"d={json.dumps(d, indent=2)}")

        for k, i in d.items():
            t = type(i)
            if t == dict:
                d[k] = self.get_settings_type_conversion(i)
            else:
                if i and t != str:
                    raise SolaceInternalError(
                        f"unhandled type, field={k}, value={i}, type={t}")
                if not i:
                    # placeholder, leave it for now
                    d[k] = None
                elif i == "":
                    # placeholder, leave it for now
                    d[k] = i
                elif i.lower() == 'false':
                    d[k] = False
                elif i.lower() == 'true':
                    d[k] = True
                elif re.search(r'^[0-9]+$', i):
                    d[k] = int(i)
                elif re.search(r'^[0-9]+\.[0-9]$', i):
                    d[k] = float(i)
                else:
                    # leave any other strings
                    d[k] = i
        return d

    def normalize_current_settings(self, current_settings: dict, new_settings: dict) -> dict:
        normalized_current_settings = self.get_settings_type_conversion(
            current_settings) if current_settings else None
        return normalized_current_settings

    def normalize_new_settings(self, new_settings) -> dict:
        if new_settings:
            SolaceUtils.type_conversion(new_settings, False)
        return new_settings

    def get_args(self):
        params = self.get_module().params
        return [params['name']]

    def get_settings_arg_name(self) -> str:
        return 'solace_cloud_settings'

    def _compose_request_body(self, operation: str, operation_type: str, settings: dict) -> dict:
        return {
            'operation': operation,
            operation_type: settings
        }

    def get_func(self, client_profile_name):
        # GET services/{paste-your-serviceId-here}/clientProfiles/{{clientProfileName}}
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()), SolaceCloudApi.API_SERVICES,
                      service_id, 'clientProfiles', client_profile_name]
        return self.solace_cloud_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, client_profile_name, settings=None):
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        module_op = SolaceTaskOps.OP_CREATE_OBJECT
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        data.update(self.CREATE_DEFAULTS)
        create_settings = self._adjust_settings_for_create(settings)
        data.update(create_settings)
        body = self._compose_request_body(operation='create',
                                          operation_type=self.OPERATION,
                                          settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()),
                      SolaceCloudApi.API_SERVICES,
                      service_id,
                      SolaceCloudApi.API_REQUESTS,
                      'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=body, module_op=module_op)

    def update_func(self, client_profile_name, settings=None, delta_settings=None):
        module_op = SolaceTaskOps.OP_UPDATE_OBJECT
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        get_settings = self.get_func(client_profile_name)
        update_settings = self._adjust_settings_for_update(delta_settings,
                                                           get_settings)
        mandatory = {
            self.OBJECT_KEY: client_profile_name
        }
        data = mandatory
        data.update(update_settings)
        body = self._compose_request_body(operation='update',
                                          operation_type=self.OPERATION,
                                          settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()), SolaceCloudApi.API_SERVICES,
                      service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=body, module_op=module_op)

    def delete_func(self, client_profile_name):
        module_op = SolaceTaskOps.OP_DELETE_OBJECT
        # POST services/{paste-your-serviceId-here}/requests/clientProfileRequests
        data = {
            self.OBJECT_KEY: client_profile_name
        }
        body = self._compose_request_body(operation='delete',
                                          operation_type=self.OPERATION, settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [self.solace_cloud_api.get_api_base_path(self.get_config()), SolaceCloudApi.API_SERVICES,
                      service_id, SolaceCloudApi.API_REQUESTS, 'clientProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=body, module_op=module_op)


def run_module():
    module_args = dict(
        name=dict(type='str',
                  aliases=['client_profile', 'client_profile_name'],
                  required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud_mandatory())
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_state())
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceCloudClientProfileTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
