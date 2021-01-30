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
module: solace_get_cert_authorities
short_description: get list of cert authorities
description:
- "Get a list of Certificate Authority objects."
- "Supports Solace Cloud Brokers as well as Solace Standalone Brokers."
notes:
- "Using Solace Cloud: where clause only supports operations: '=='"
- ""
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/certAuthority/getCertAuthorities"
- "Module Sempv2 Monitor: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/certAuthority/getCertAuthorities"
- "Module Solace Cloud API: not available"
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.get_list
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_cert_authority
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
  solace_cert_authority:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN | default(omit) }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
  solace_get_cert_authorities:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN | default(omit) }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:
- name: create cert authority
  solace_cert_authority:
    name: foo
    settings:
      certContent: "the-cert"
      state: present

- name: get list config
  solace_get_cert_authorities:
    query_params:
      where:
        - "certAuthorityName==foo"
  register: result

- name: print result
  debug:
    msg:
      - "{{ result.result_list }}"
      - "{{ result.result_list_count }}"

- name: get list monitor
  solace_get_cert_authorities:
    api: monitor
    query_params:
      where:
        - "certAuthorityName==foo"
  register: result

- name: print result
  debug:
    msg:
      - "{{ result.result_list }}"
      - "{{ result.result_list_count }}"
'''

RETURN = '''
result_list:
  description: The list of objects found containing requested fields. Payload depends on API called.
  returned: success
  type: list
  elements: dict
result_list_count:
  description: Number of items in result_list.
  returned: success
  type: int
rc:
  description: Return code. rc=0 on success, rc=1 on error.
  type: int
  returned: always
  sample:
    success:
      rc: 0
    error:
      rc: 1
msg:
  description: The response from the HTTP call in case of error.
  type: dict
  returned: error
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask, SolaceCloudGetTask, SolaceTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError, SolaceInternalError
from ansible.module_utils.basic import AnsibleModule
import re


class Mappings:
    SEMPV2_SOLACE_CLOUD = {
        "certAuthorityName": "name"
    }


class SolaceCloudGetCertAuthoritiesTask(SolaceCloudGetTask):
    def __init__(self, module):
        super().__init__(module)

    # TODO: implement the other OPs: !=, <, >, <=, >=
    def filter_cert_authority(self, cert_authority_settings: dict, query_params: dict) -> dict:
        if not query_params:
            return cert_authority_settings
        where_list = []
        if ("where" in query_params and query_params['where'] and len(query_params['where']) > 0):
            where_list = query_params['where']
        is_match = True
        for where in where_list:
            # OP: ==
            where_elements = where.split('==')
            if len(where_elements) != 2:
                raise SolaceParamsValidationError('query_params.where', where, "cannot parse where clause - must be in format '{key}=={pattern}' (other ops are not supported)")
            sempv2_key = where_elements[0]
            pattern = where_elements[1]
            solace_cloud_key = Mappings.SEMPV2_SOLACE_CLOUD.get(sempv2_key, None)
            if not solace_cloud_key:
                raise SolaceParamsValidationError('query_params.where', where, f"unknown key for solace cloud '{sempv2_key}' - check with SEMPv2 settings")
            # pattern match
            solace_cloud_value = cert_authority_settings.get(solace_cloud_key, None)
            if not solace_cloud_value:
                raise SolaceInternalError(f"solace-cloud-key={solace_cloud_key} not found in solace cloud settings - likely a key map issue")
            # create regex
            regex = pattern.replace("*", ".+")
            this_match = re.search(regex, solace_cloud_value)
            is_match = (is_match and this_match)
            if not is_match:
                break
        if is_match:
            return cert_authority_settings
        return None

    def _get_cert_authority(self, service_id, cert_authority_name, query_params):
        # GET services/{serviceId}/serviceCertificateAuthorities/{certAuthorityName}
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, 'serviceCertificateAuthorities', cert_authority_name]
        resp = self.solace_cloud_api.get_object_settings(self.get_config(), path_array)
        cert_authority = resp['certificate']
        return self.filter_cert_authority(cert_authority, query_params)

    def do_task(self):
        params = self.get_module().params
        service_id = params['solace_cloud_service_id']
        query_params = params['query_params']
        service = self.get_solace_cloud_api().get_service(self.get_config(), service_id)
        cert_authoritie_names = service['certificateAuthorities']
        cert_authorities = []
        for cert_authority_name in cert_authoritie_names:
            cert_authority = self._get_cert_authority(service_id, cert_authority_name, query_params)
            if cert_authority:
                cert_authorities.append(cert_authority)
        result = self.create_result_with_list(cert_authorities)
        return None, result


class SolaceBrokerGetCertAuthoritiesTask(SolaceBrokerGetPagingTask):
    def __init__(self, module):
        super().__init__(module)

    def get_path_array(self, params: dict) -> list:
        # GET /certAuthorities
        return ['certAuthorities']


class SolaceGetCertAuthoritiesTask(SolaceTask):
    def __init__(self, module):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config

    def do_task(self):
        if self.get_config().is_solace_cloud():
            solace_task = SolaceCloudGetCertAuthoritiesTask(self.get_module())
            return solace_task.do_task()
        solace_task = SolaceBrokerGetCertAuthoritiesTask(self.get_module())
        return solace_task.do_task()


def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGetCertAuthoritiesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
