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

TODO: solace cloud does not support it
SEMPV2 min version: 2.19


short_description: certificate authority
description:
- "Allows addition, removal and configuration of certificate authority objects on Solace Brokers in an idempotent manner."
- "Supports standalone brokers and Solace Cloud."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/certAuthority"
- "Module Solace Cloud API: not available"
- "Uses deprecated SempV2 API. Since 2.19, broker supports 'clientCertAuthority' & 'domainCertAuthority' instead. Raise an issue if these are required."
seealso:
- module: solace_get_cert_authorities
options:
  name:
    description: The name of the Certificate Authority. Maps to 'certAuthorityName' in the Sempv2 API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.broker_config_solace_cloud
author:
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
TODO: write example playbook and copy here
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
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:
  - name: set files
    set_fact:
      cert_key_file: ./tmp/key.pem
      cert_file: ./tmp/cert.pem

  - name: generate certificate
    command: >
      openssl req
      -x509
      -newkey
      rsa:4096
      -keyout {{ cert_key_file }}
      -out {{ cert_file }}
      -days 365
      -nodes
      -subj "/C=UK/ST=London/L=London/O=Solace/OU=Org/CN=www.example.com"

  - name: add
    solace_cert_authority:
      name: foo
      settings:
        certContent: "{{ lookup('file', cert_file) }}"
        revocationCheckEnabled: false
      state: present

  - name: remove
    solace_cert_authority:
      name: foo
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
