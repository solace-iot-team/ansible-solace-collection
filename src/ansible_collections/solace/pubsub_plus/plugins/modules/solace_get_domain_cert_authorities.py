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
module: solace_get_domain_cert_authorities
short_description: get list of domain certificates
description:
- "Get a list of Domain Certificate objects configured on a service."
- "Supports standalone brokers and Solace Cloud."
requirements:
- "Requires min SempV2 API v2.19 for standalone brokers. See M(solace_get_cert_authorities) for earlier SempV2 versions."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/domainCertAuthority/getDomainCertAuthorities"
- "Module Sempv2 Monitor: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/domainCertAuthority/getDomainCertAuthorities"
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.get_list
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_domain_cert_authority
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

-
  name: "solace_domain_cert_authority.doc-example"
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
    solace.pubsub_plus.solace_domain_cert_authority:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
    solace.pubsub_plus.solace_get_domain_cert_authorities:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
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
    solace_domain_cert_authority:
      name: asc_test
      settings:
        certContent: "{{ lookup('file', cert_file) }}"
      state: present

  - name: get config of cert authority
    solace_get_domain_cert_authorities:
      query_params:
        where:
          - "certAuthorityName==asc_test"

  - name: get monitor of cert authority
    solace_get_domain_cert_authorities:
      api: monitor
      query_params:
        where:
          - "certAuthorityName==asc_test"

  - name: remove cert authority
    solace_domain_cert_authority:
      name: asc_test
      state: absent

###
# The End.
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

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask, SolaceCloudGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApiCertAuthority
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudGetDomainCertAuthoritiesTask(SolaceCloudGetTask):
    def __init__(self, module):
        super().__init__(module)
        self.solace_cloud_cert_auth_api = SolaceCloudApiCertAuthority(module)

    def do_task(self):
        params = self.get_module().params
        service_id = params['solace_cloud_service_id']
        query_params = params['query_params']
        service = self.get_solace_cloud_api().get_service(self.get_config(), service_id)
        cert_authoritie_names = service['domainCertificateAuthorities']
        cert_authorities = []
        for cert_authority_name in cert_authoritie_names:
            cert_authority = self.solace_cloud_cert_auth_api.get_cert_authority(
                self.get_config(), service_id, cert_authority_name, query_params)
            if cert_authority:
                cert_authorities.append(cert_authority)
        result = self.create_result_with_list(cert_authorities)
        return None, result


class SolaceBrokerGetDomainCertAuthoritiesTask(SolaceBrokerGetPagingTask):

    MIN_SEMP_V2_VERSION_STR = "2.19"

    def __init__(self, module):
        super().__init__(module)

    def is_supports_paging(self):
        return False

    def get_path_array(self, params: dict) -> list:
        # GET /domainCertAuthorities
        return ['domainCertAuthorities']


class SolaceGetDomainCertAuthoritiesTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config

    def do_task(self):
        if self.get_config().is_solace_cloud():
            solace_task = SolaceCloudGetDomainCertAuthoritiesTask(
                self.get_module())
            return solace_task.do_task()
        solace_task = SolaceBrokerGetDomainCertAuthoritiesTask(
            self.get_module())
        return solace_task.do_task()


def run_module():
    module_args = {}
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceGetDomainCertAuthoritiesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
