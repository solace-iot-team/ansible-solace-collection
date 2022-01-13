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

TODO: only works on standalone brokers, sempv2 version < 2.19
does not work on solace cloud

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

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetCertAuthoritiesTask(SolaceBrokerGetPagingTask):

    MAX_SEMP_V2_VERSION_STR = "2.18"

    def __init__(self, module):
        super().__init__(module)

    def get_path_array(self, params: dict) -> list:
        # GET /certAuthorities
        return ['certAuthorities']


def run_module():
    module_args = {}
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceGetCertAuthoritiesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
