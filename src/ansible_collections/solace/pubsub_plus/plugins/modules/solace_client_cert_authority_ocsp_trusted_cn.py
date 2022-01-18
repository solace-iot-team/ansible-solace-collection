#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_client_cert_authority_ocsp_trusted_cn
short_description: ocsp responder trusted common name
description:
- "Allows addition, removal and configuration of OCSP Responder Trusted Common Name objects on Solace Brokers in an idempotent manner."
- "Supports standalone brokers only."
requirements:
- "Requires min SempV2 API v2.19 for standalone brokers. See M(solace_cert_authority) for earlier SempV2 versions."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientCertAuthority/getClientCertAuthorityOcspTlsTrustedCommonNames"
- "Module Solace Cloud API: not available"
seealso:
- module: solace_get_client_cert_authority_ocsp_trusted_cns
- module: solace_client_cert_authority
- module: solace_cert_authority
options:
  name:
    description: The expected trusted common name of the responder remote certificate. Maps to 'ocspTlsTrustedCommonName' in the Sempv2 API.
    required: true
    type: str
    aliases:
    - ocspTlsTrustedCommonName
  client_cert_authority_name:
    description: The name of the Certificate Authority. Maps to 'certAuthorityName' in the Sempv2 API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
author:
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

-
  name: "solace_client_cert_authority.doc-example"
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace.pubsub_plus.solace_gather_facts:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
    solace.pubsub_plus.solace_client_cert_authority:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
    solace.pubsub_plus.solace_get_client_cert_authorities:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
    solace.pubsub_plus.solace_client_cert_authority_ocsp_trusted_cn:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
    solace.pubsub_plus.solace_get_client_cert_authority_ocsp_trusted_cns:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
  tasks:
  - name: gather facts
    solace_gather_facts:
    # no_log: true
  - set_fact:
      is_solace_cloud: "{{ ansible_facts.solace.isSolaceCloud }}"
      sempv2_version: "{{ ansible_facts.solace.about.api.sempVersion }}"
      working_dir: "{{ WORKING_DIR }}"
      cert_file: "{{ WORKING_DIR }}/cert.pem"

  - name: end play if incorrect sempV2 version
    meta: end_play
    when: sempv2_version|float < 2.19

  - name: "main: generate certificate"
    command: >
      openssl req
      -x509
      -newkey
      rsa:4096
      -keyout {{ working_dir }}/key.pem
      -out {{ cert_file }}
      -days 365
      -nodes
      -subj "/C=UK/ST=London/L=London/O=Solace/OU=Org/CN=www.example.com"

  - name: create cert authority
    solace_client_cert_authority:
      name: asc_test
      settings:
        certContent: "{{ lookup('file', cert_file) }}"
        revocationCheckEnabled: false
      state: present

  - name: get config of cert authority
    solace_get_client_cert_authorities:
      query_params:
        where:
          - "certAuthorityName==asc_test"

  - name: get monitor of cert authority
    solace_get_client_cert_authorities:
      api: monitor
      query_params:
        where:
          - "certAuthorityName==asc_test"

# set an OCSP trusted name
# note: not available in Solace Cloud API
  - name: set trusted name
    block:
    - name: add trusted name
      solace_client_cert_authority_ocsp_trusted_cn:
        name: "*.domain.com"
        client_cert_authority_name: asc_test
        state: present

    - name: get list of trusted names
      solace_get_client_cert_authority_ocsp_trusted_cns:
        client_cert_authority_name: asc_test

    - name: remove trusted name
      solace_client_cert_authority_ocsp_trusted_cn:
        name: "*.domain.com"
        client_cert_authority_name: asc_test
        state: absent

    when: not is_solace_cloud

  - name: remove cert authority
    solace_client_cert_authority:
      name: asc_test
      state: absent

###
# The End.
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceClientCertAuthorityTask(SolaceBrokerCRUDTask):

    MIN_SEMP_V2_VERSION_STR = "2.19"
    OBJECT_KEY = 'ocspTlsTrustedCommonName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def validate_params(self):
        params = self.get_module().params
        client_cert_authority_name = params['client_cert_authority_name']
        if '-' in client_cert_authority_name:
            raise SolaceParamsValidationError(
                'client_cert_authority_name', client_cert_authority_name, "must not contain '-'")

    def get_args(self):
        params = self.get_module().params
        return [params['client_cert_authority_name'], params['name']]

    def get_func(self, cert_authority_name, tls_trusted_cn):
        # GET /clientCertAuthorities/{certAuthorityName}/ocspTlsTrustedCommonNames/{ocspTlsTrustedCommonName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'clientCertAuthorities',
                      cert_authority_name, 'ocspTlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, cert_authority_name, tls_trusted_cn, settings=None):
        # POST /clientCertAuthorities/{certAuthorityName}/ocspTlsTrustedCommonNames
        data = {
            self.OBJECT_KEY: tls_trusted_cn,
            'certAuthorityName': cert_authority_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'clientCertAuthorities',
                      cert_authority_name, 'ocspTlsTrustedCommonNames']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, cert_authority_name, tls_trusted_cn):
        # DELETE /clientCertAuthorities/{certAuthorityName}/ocspTlsTrustedCommonNames/{ocspTlsTrustedCommonName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'clientCertAuthorities', cert_authority_name,
                      'ocspTlsTrustedCommonNames', tls_trusted_cn]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=[
                  'ocspTlsTrustedCommonName']),
        client_cert_authority_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    # arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceClientCertAuthorityTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
