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
module: solace_cloud_get_facts
short_description: get Solace Cloud service facts
description:
- Convenience functions to access Solace Cloud service facts gathered with M(solace_cloud_get_service).
options:
  from_dict:
    description: The JSON object (dict) which holds the service facts.
    required: True
    type: dict
  field_funcs:
    description: List of pre-built field functions that retrieve values from the 'from_dict'.
    required: false
    type: list
    default: []
    elements: str
    suboptions:
      get_serviceSEMPManagementEndpoints:
        description: Retrieves the SEMP management endpoint.
        type: str
        required: no
  get_formattedHostInventory:
    description: >
        Get the facts formatted as a JSON host inventory.
        Retrieve the inventory field by field or save to file and use in subsequent playbooks as an inventory.
    type: dict
    required: no
    suboptions:
      host_entry:
        description: The entry for this broker / service in the hosts file. Must be a valid JSON key.
        type: str
        required: true
      api_token:
        description: The API token to access the Solace Cloud Service API.
        type: str
        required: false
      meta:
        description: Additional meta data describing the service instance.
        type: dict
        required: true
seealso:
- module: solace_cloud_get_service
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
tasks:
  - set_fact:
      api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      service_id: "the-service-id"

  - name: "Get Service"
    solace_cloud_get_service:
      api_token: "{{ api_token }}"
      service_id: "{{ service_id }}"
    register: result

  - name: "Set Fact: Solace Service Details"
    set_fact:
      sc_service_details: "{{ result.response }}"

  - name: "Get Semp Management Endpoints"
    solace_cloud_get_facts:
      from_dict: "{{ sc_service_details }}"
      field_funcs:
        - get_serviceSEMPManagementEndpoints
      register: semp_enpoints_facts

  - name: "Save Solace Cloud Service SEMP Management Endpoints to File"
    copy:
      content: "{{ semp_enpoints_facts | to_nice_json }}"
      dest: "./tmp/facts.solace_cloud_service.semp.json"
    delegate_to: localhost

  - name: "Set Fact: Solace Service SEMP"
    set_fact:
      sempv2_host: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.SecuredSEMP.uriComponents.host }}"
      sempv2_port: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.SecuredSEMP.uriComponents.port }}"
      sempv2_is_secure_connection: True
      sempv2_username: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.username }}"
      sempv2_password: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.password }}"
      sempv2_timeout: 60

  - name: "Gather Solace Facts from Service"
    solace_gather_facts:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ api_token }}"
      solace_cloud_service_id: "{{ serviceId }}"

  - name: "Save Solace Cloud Service Facts to File"
    copy:
      content: "{{ ansible_facts.solace | to_nice_json }}"
      dest: "./tmp/solace_facts.solace_cloud_service.json"
    delegate_to: localhost

  - name: "Get Host Inventory"
    solace_cloud_get_facts:
      from_dict: "{{ sc_service_details }}"
      get_formattedHostInventory:
        host_entry: "{{ sc_service_name }}"
        api_token: "{{ api_token }}"
        meta:
          service_name: "{{ sc_service_details.name }}"
          service_id: "{{ sc_service_details.serviceId }}"
          datacenterId: "{{ sc_service_details.datacenterId }}"
          serviceTypeId: "{{ sc_service_details.serviceTypeId}}"
          serviceClassId: "{{ sc_service_details.serviceClassId }}"
          serviceClassDisplayedAttributes: "{{ sc_service_details.serviceClassDisplayedAttributes }}"
    register: inv_results

  - name: "Save Solace Cloud Service inventory to File"
    copy:
      content: "{{ inv_results.facts.formattedHostInventory | to_nice_json }}"
      dest: "./tmp/inventory.{{ sc_service_name }}.json"
    delegate_to: localhost
'''

RETURN = '''
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
    description: error message if not ok
    type: str
    returned: error
facts:
    description: The facts retrieved from the input.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceReadFactsTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError, SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule
from urllib.parse import urlparse
import json
from json.decoder import JSONDecodeError


class SolaceCloudGetFactsTask(SolaceReadFactsTask):

    FIELD_FUNCS = [
        "get_serviceSEMPManagementEndpoints"
    ]

    def __init__(self, module):
        super().__init__(module)

    def validate_params(self):
        params = self.get_module().params

        from_dict = params['from_dict']
        if not isinstance(from_dict, dict):
            raise SolaceParamsValidationError("from_dict", type(from_dict), "invalid type, must be a dict")

        # check state of service
        service_state = self.get_field(from_dict, 'creationState')
        if service_state != 'completed':
            raise SolaceParamsValidationError("service creationState", service_state, "is not 'completed'")

        has_get_funcs = self.validate_param_field_funcs(self.FIELD_FUNCS, params['field_funcs'])

        param_get_formattedHostInventory = params.get('get_formattedHostInventory', None)
        if param_get_formattedHostInventory:
            has_get_funcs = True
        if not has_get_funcs:
            raise SolaceError("no get functions found - specify at least one")
        return

    def do_task(self):
        self.validate_params()
        params = self.get_module().params
        search_dict = params['from_dict']
        field_funcs = params['field_funcs']
        facts = dict()
        if field_funcs and len(field_funcs) > 0:
            for field_func in field_funcs:
                field, value = self.call_dynamic_func(field_func, search_dict)
                facts[field] = value

        param_get_formattedHostInventory = params['get_formattedHostInventory']
        if param_get_formattedHostInventory:
            field, value = self.get_formattedHostInventory(search_dict,
                                                           param_get_formattedHostInventory['host_entry'],
                                                           param_get_formattedHostInventory['api_token'],
                                                           param_get_formattedHostInventory['meta'])
            facts[field] = value

        result = self.create_result(rc=0, changed=False)
        result['facts'] = facts
        return None, result

    def get_formattedHostInventory(self, search_dict: dict, host_entry: str, api_token: str = None, meta: dict = None):
        _eps_field, eps_val = self.get_serviceSEMPManagementEndpoints(search_dict)
        inv = dict(
            all=dict()
        )
        hosts = dict()
        hosts[host_entry] = {
            'meta': meta,
            'ansible_connection': 'local',
            'broker_type': 'solace_cloud',
            'solace_cloud_service_id': search_dict['serviceId'],
            'sempv2_host': eps_val['SEMP']['SecuredSEMP']['uriComponents']['host'],
            "sempv2_port": eps_val['SEMP']['SecuredSEMP']['uriComponents']['port'],
            "sempv2_is_secure_connection": True,
            "sempv2_username": eps_val['SEMP']['username'],
            "sempv2_password": eps_val['SEMP']['password'],
            "sempv2_timeout": "60",
            "vpn": self.get_vpn(search_dict),
            "virtual_router": "primary"
        }
        if api_token:
            hosts[host_entry].update({'solace_cloud_api_token': api_token})

        inv['all']['hosts'] = hosts
        return 'formattedHostInventory', inv

    def get_serviceSEMPManagementEndpoints(self, search_dict: dict):
        eps = dict(
            SEMP=dict(
                SecuredSEMP=dict()
            )
        )
        mgmt_protocols_dict = self.get_field(search_dict, 'managementProtocols')
        if mgmt_protocols_dict is None:
            raise SolaceError("Could not find 'managementProtocols' in 'from_dict'.")
        semp_dict = self.get_nested_dict(mgmt_protocols_dict, field="name", value='SEMP')
        if semp_dict is None:
            raise SolaceError("Could not find 'name=SEMP' in 'managementProtocols' in 'from_dict'.")
        sec_semp_end_point_dict = self.get_protocol_endpoint(semp_dict, field='name', value='Secured SEMP Config')
        sec_semp_uri = self.get_protocol_endpoint_uri(sec_semp_end_point_dict)
        t = urlparse(sec_semp_uri)
        sec_semp_protocol = t.scheme
        sec_semp_host = t.hostname
        sec_semp_port = t.port
        # put the dict together
        sec_semp = dict()
        sec_semp_ucs = dict()
        sec_semp_ucs['protocol'] = sec_semp_protocol
        sec_semp_ucs['host'] = sec_semp_host
        sec_semp_ucs['port'] = sec_semp_port
        sec_semp['uriComponents'] = sec_semp_ucs
        sec_semp['uri'] = sec_semp_uri
        eps['SEMP']['SecuredSEMP'] = sec_semp
        eps['SEMP']['username'] = semp_dict['username']
        eps['SEMP']['password'] = semp_dict['password']
        return 'serviceManagementEndpoints', eps

    def get_vpn(self, search_dict: dict) -> str:
        vpn_attributes = search_dict.get('msgVpnAttributes', None)
        if not vpn_attributes:
            raise SolaceError(f"Could not find 'msgVpnAttributes' in dict:{search_dict}.")
        vpn_name = vpn_attributes.get('vpnName', None)
        if not vpn_name:
            raise SolaceError(f"Could not find 'vpnName' in dict:{search_dict}.")
        return vpn_name

    def get_protocol_endpoint(self, search_dict: dict, field: str, value: str):
        element = 'endPoints'
        if element not in search_dict:
            raise SolaceError(f"Could not find '{element}' in dict:{search_dict}.")
        end_points = search_dict[element]
        if len(end_points) == 0:
            raise SolaceError(f"Empty list:'{element}' in dict:{search_dict}.")
        end_point_dict = self.get_nested_dict(end_points, field, value)
        if end_point_dict is None:
            raise SolaceError(f"Could not find end point with '{field}={value}'.")
        return end_point_dict

    def get_protocol_endpoint_uri(self, search_dict: dict):
        element = 'uris'
        if element not in search_dict:
            errs = [
                f"Could not find '{element}' in end point:",
                f"{json.dumps(search_dict)}"
            ]
            raise SolaceError(errs)
        if len(search_dict['uris']) != 1:
            errs = [
                f"'{element}' list contains != 1 elements in end point:",
                f"{json.dumps(search_dict)}"
            ]
            raise SolaceError(errs)
        return search_dict['uris'][0]


def run_module():
    module_args = dict(
        from_dict=dict(type='dict', required=True),
        field_funcs=dict(type='list', required=False, elements='str'),
        get_formattedHostInventory=dict(type='dict',
                                        required=False,
                                        default=None,
                                        options=dict(
                                            host_entry=dict(type='str', required=True),
                                            api_token=dict(type='str', required=False, no_log=True),
                                            meta=dict(type='dict', required=True)
                                        ))
    )
    arg_spec = dict()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceCloudGetFactsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
