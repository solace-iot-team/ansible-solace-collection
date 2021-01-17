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
module: solace_cert_authority

TODO: re-work doc

short_description: certificate authority

description:
- "Allows addition, removal and configuration of certificate authority objects on Solace Brokers in an idempotent manner."

notes:
- "Solace Cloud currently does not support managing certificate authorities."
- "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/certAuthority."

options:
    name:
        description: The name of the Certificate Authority. Maps to 'certAuthorityName' in the API.
        required: true
        type: str
    cert_content:
        description: The certificate.
        required: false
        default: ''
        type: str

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
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
    solace_cert_authority:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
tasks:
  - name: set files
    set_fact:
      cert_key_file: ./tmp/key.pem
      cert_file: ./tmp/cert.pem

  - name: create certificate
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
      name: bar
      cert_content: "{{ lookup('file', cert_file) }}"
      settings:
        revocationCheckEnabled: false
      state: present

  - name: remove
    solace_cert_authority:
      name: bar
      state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceCertAuthorityTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'certAuthorityName'
    SOLACE_CLOUD_DEFAULTS = {
        # 'revocationCheckEnabled': False,
        # 'ocspOverrideUrl': None,
        # 'ocspTimeout': None,
        # 'ocspNonResponderCertEnabled': False
    }

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def validate_params(self):
        params = self.get_module().params
        name = params['name']
        if '-' in name:
            raise SolaceParamsValidationError('name', name, f"must not contain '-'")

    def get_args(self):
        params = self.get_module().params
        return [params['name']]

    def _get_func_solace_cloud(self, cert_authority_name):
        # GET services/{serviceId}/serviceCertificateAuthorities/{certAuthorityName}
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, 'serviceCertificateAuthorities', cert_authority_name]
        return self.solace_cloud_api.get_object_settings(self.get_config(), path_array)

    def get_func(self, cert_authority_name):
        if self.get_config().is_solace_cloud():
            return self._get_func_solace_cloud(cert_authority_name)
        # GET /certAuthorities/{certAuthorityName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'certAuthorities', cert_authority_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def _create_func_solace_cloud(self, cert_authority_name, settings):
        # POST /services/${serviceId}/requests/serviceCertificateAuthorityRequests
        cert_content = (settings['certContent'] if settings else None)
        if settings:
            settings.pop('certContent', None)
        body = {
            'certificate': {
                'name': cert_authority_name,
                'content': cert_content,
                'action': 'create'
            }
        }
        body.update(self.SOLACE_CLOUD_DEFAULTS)
        body.update(settings if settings else {})
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, SolaceCloudApi.API_REQUESTS, 'serviceCertificateAuthorityRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, body)

    def create_func(self, cert_authority_name, settings=None):
        if self.get_config().is_solace_cloud():
            return self._create_func_solace_cloud(cert_authority_name, settings)
        # POST /certAuthorities
        data = {
            self.OBJECT_KEY: cert_authority_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'certAuthorities']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def _update_func_solace_cloud(self, cert_authority_name, settings, delta_settings):
        # POST /services/${serviceId}/requests/serviceCertificateAuthorityRequests
        cert_content = None
        if settings:
            cert_content = settings.pop('certContent', None)
        body = {
            'certificate': {
                'name': cert_authority_name,
                'action': 'update'
            }
        }
        if cert_content:
            body['certificate'].update({ 'content': cert_content})
        body.update(settings if settings else {})
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, SolaceCloudApi.API_REQUESTS, 'serviceCertificateAuthorityRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, body)

    def update_func(self, cert_authority_name, settings=None, delta_settings=None):
        if self.get_config().is_solace_cloud():
            return self._update_func_solace_cloud(cert_authority_name, settings, delta_settings)
        # PATCH /certAuthorities/{certAuthorityName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'certAuthorities', cert_authority_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def _delete_func_solace_cloud(self, cert_authority_name):
        # POST /services/{serviceId}/requests/serviceCertificateAuthorityRequests
        body = {
            'certificate': {
                'name': cert_authority_name,
                'action': 'delete'
            }
        }
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, SolaceCloudApi.API_REQUESTS, 'serviceCertificateAuthorityRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, body)

    def delete_func(self, cert_authority_name):
        if self.get_config().is_solace_cloud():
            return self._delete_func_solace_cloud(cert_authority_name)
        # DELETE /certAuthorities/{certAuthorityName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'certAuthorities', cert_authority_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )
    solace_task = SolaceCertAuthorityTask(module)
    solace_task.execute()


def main():

    run_module()


if __name__ == '__main__':
    main()
