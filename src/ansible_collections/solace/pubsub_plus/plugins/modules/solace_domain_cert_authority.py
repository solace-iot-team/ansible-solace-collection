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
module: solace_domain_cert_authority
TODO
SEMPV2 min version: 2.19, otherwise use solace_cert_authority

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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApiCertAuthority
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError, SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceDomainCertAuthorityTask(SolaceBrokerCRUDTask):

    MIN_SEMP_V2_VERSION_STR = "2.19"

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
        self.solace_cloud_api = SolaceCloudApiCertAuthority(module)

    def validate_params(self):
        params = self.get_module().params
        name = params['name']
        if '-' in name:
            raise SolaceParamsValidationError(
                'name', name, "must not contain '-'")

    def get_args(self):
        params = self.get_module().params
        return [params['name']]

    def _get_func_solace_cloud(self, cert_authority_name):
        # GET services/{serviceId}/serviceCertificateAuthorities/{certAuthorityName}
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApiCertAuthority.API_BASE_PATH, SolaceCloudApiCertAuthority.API_SERVICES,
                      service_id, 'serviceCertificateAuthorities', cert_authority_name]
        obj_settings = self.solace_cloud_api.get_object_settings(
            self.get_config(), path_array)
        # TODO: check if it is a domain cert
        import logging
        import json
        logging.debug(
            f"obj_settings=\n{json.dumps(obj_settings, indent=2)}")
        if(obj_settings is not None):
            logging.debug(
                f"obj_settings is not None")

        return obj_settings

    def get_func(self, cert_authority_name):
        if self.get_config().is_solace_cloud():
            return self._get_func_solace_cloud(cert_authority_name)
        # GET /domainCertAuthorities/{certAuthorityName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'domainCertAuthorities', cert_authority_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def _create_func_solace_cloud(self, cert_authority_name, settings):
        # POST /services/${serviceId}/requests/serviceCertificateAuthorityRequests
        # {
        #     "certificate": {
        #         "name": "xxxxx",
        #         "content": "xxxxxx",
        #         "action": "create"
        #     },
        #     "revocationCheckEnabled": null,
        #     "ocspOverrideUrl": null,
        #     "ocspTimeout": null,
        #     "ocspNonResponderCertEnabled": null,
        #     "certType": "domain"
        # }
        cert_content = (settings['certContent'] if settings else None)
        if settings:
            settings.pop('certContent', None)
        body = {
            'certificate': {
                'name': cert_authority_name,
                'content': cert_content,
                'action': 'create'
            },
            'certType': 'domain'
        }
        body.update(self.SOLACE_CLOUD_DEFAULTS)
        body.update(settings if settings else {})
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApiCertAuthority.API_BASE_PATH, SolaceCloudApiCertAuthority.API_SERVICES,
                      service_id, SolaceCloudApiCertAuthority.API_REQUESTS, 'serviceCertificateAuthorityRequests']
        return self.solace_cloud_api.make_service_post_request(
            self.get_config(),
            path_array,
            service_id,
            json_body=body,
            module_op=SolaceTaskOps.OP_CREATE_OBJECT
        )

    def create_func(self, cert_authority_name, settings=None):
        if self.get_config().is_solace_cloud():
            return self._create_func_solace_cloud(cert_authority_name, settings)
        # POST /domainCertAuthorities
        data = {
            self.OBJECT_KEY: cert_authority_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'domainCertAuthorities']
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
            },
            'certType': 'domain'
        }
        if cert_content:
            body['certificate'].update({'content': cert_content})
        body.update(settings if settings else {})
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApiCertAuthority.API_BASE_PATH, SolaceCloudApiCertAuthority.API_SERVICES,
                      service_id, SolaceCloudApiCertAuthority.API_REQUESTS, 'serviceCertificateAuthorityRequests']
        return self.solace_cloud_api.make_service_post_request(
            self.get_config(),
            path_array,
            service_id,
            json_body=body,
            module_op=SolaceTaskOps.OP_UPDATE_OBJECT
        )

    def update_func(self, cert_authority_name, settings=None, delta_settings=None):
        if self.get_config().is_solace_cloud():
            return self._update_func_solace_cloud(cert_authority_name, settings, delta_settings)
        # PATCH /domainCertAuthorities/{certAuthorityName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'domainCertAuthorities', cert_authority_name]
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
        path_array = [SolaceCloudApiCertAuthority.API_BASE_PATH, SolaceCloudApiCertAuthority.API_SERVICES,
                      service_id, SolaceCloudApiCertAuthority.API_REQUESTS, 'serviceCertificateAuthorityRequests']
        return self.solace_cloud_api.make_service_post_request(
            self.get_config(),
            path_array,
            service_id,
            json_body=body,
            module_op=SolaceTaskOps.OP_DELETE_OBJECT
        )

    def delete_func(self, cert_authority_name):
        if self.get_config().is_solace_cloud():
            return self._delete_func_solace_cloud(cert_authority_name)
        # DELETE /domainCertAuthorities/{certAuthorityName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'domainCertAuthorities', cert_authority_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = {}
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceDomainCertAuthorityTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
