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
- Convenience functions to access Solace Cloud service facts gathered with M(solace_cloud_get_service) and returned by M(solace_cloud_service).
options:
  from_dict:
    description: >
      The JSON object (dict) which holds the service facts.
      Could be the result of M(solace_cloud_get_service) or M(solace_cloud_service) (state=present).
    required: True
    type: dict
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
- module: solace_cloud_service
- module: solace_gather_facts
- module: solace_get_facts
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

  - name: get a list of all services in the account
    solace_cloud_get_services:
      api_token: "{{ api_token }}"
    register: result

  - name: save first service in list
    set_fact:
      sc_service: "{{ result.result_list[0] }}"

  - name: get all details for first service in list
    solace_cloud_get_service:
      api_token: "{{ api_token }}"
      service_id: "{{ sc_service.serviceId }}"
    register: result

  - name: save service details
    set_fact:
      sc_service_details: "{{ result.service }}"

  - name: save details to file
    copy:
      content: "{{ sc_service_details | to_nice_json }}"
      dest: "./solace_cloud_service.{{ sc_service.name }}.details.json"
    delegate_to: localhost

  - name: get host inventory for service
    solace_cloud_get_facts:
      from_dict: "{{ sc_service_details }}"
      get_formattedHostInventory:
        host_entry: "{{ sc_service.name }}"
        api_token: "{{ api_token }}"
        meta:
          service_name: "{{ sc_service_details.name }}"
          service_id: "{{ sc_service_details.serviceId }}"
          datacenterId: "{{ sc_service_details.datacenterId }}"
          serviceTypeId: "{{ sc_service_details.serviceTypeId}}"
          serviceClassId: "{{ sc_service_details.serviceClassId }}"
          serviceClassDisplayedAttributes: "{{ sc_service_details.serviceClassDisplayedAttributes }}"
    register: result

  - name: save new service inventory to file
    copy:
      content: "{{ result.facts.formattedHostInventory | to_nice_yaml }}"
      dest: "./inventory.{{ sc_service.name }}.yml"
    delegate_to: localhost

  - name: extract the service facts
    set_fact:
      inventory_facts: "{{ result.facts.formattedHostInventory.all.hosts[sc_service.name] }}"

  - name: set semp connection facts
    set_fact:
      sempv2_host: "{{ inventory_facts.sempv2_host }}"
      sempv2_port: "{{ inventory_facts.sempv2_port }}"
      sempv2_is_secure_connection: "{{ inventory_facts.sempv2_is_secure_connection }}"
      sempv2_username: "{{ inventory_facts.sempv2_username }}"
      sempv2_password: "{{ inventory_facts.sempv2_password }}"
      sempv2_timeout: "{{ inventory_facts.sempv2_timeout }}"
      vpn: "{{ inventory_facts.vpn }}"

  - name: gather facts for service
    solace_gather_facts:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ api_token }}"
      solace_cloud_service_id: "{{ sc_service.serviceId }}"

  - name: retrieve all client connection details
    solace_get_facts:
      hostvars: "{{ hostvars }}"
      hostvars_inventory_hostname: "{{ inventory_hostname }}"
      msg_vpn: "{{ vpn }}"
      get_functions:
        - get_allClientConnectionDetails
    register: result

  - name: save connection details
    set_fact:
      client_connection_details: "{{ result.facts }}"

  - name: save connection details to file
    copy:
      content: "{{ client_connection_details | to_nice_json }}"
      dest: "./facts.solace_cloud_service.{{ sc_service.name }}.client_connection_details.json"
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
    sample:
      get_formattedHostInventory:
        all:
            hosts:
                asc_test_1:
                    ansible_connection: local
                    broker_type: solace_cloud
                    meta:
                        datacenterId: aws-ca-central-1a
                        serviceClassDisplayedAttributes:
                            Clients: '250'
                            High Availability: HA Group
                            Message Broker Tenancy: Dedicated
                            Network Speed: 450 Mbps
                            Network Usage: 50 GB per month
                            Queues: '250'
                            Storage: 25 GB
                        serviceClassId: enterprise-250-nano
                        serviceTypeId: enterprise
                        service_id: 1n34cqfh9i7x
                        service_name: asc_test_1
                    sempv2_host: mr1n34cqfh9i8x.messaging.solace.cloud
                    sempv2_is_secure_connection: true
                    sempv2_password: hihqxxx92sa3bc2sphtp3nl
                    sempv2_port: 943
                    sempv2_timeout: '60'
                    sempv2_username: asc_test_1-admin
                    solace_cloud_service_id: 1n34cqfh9i7x
                    virtual_router: primary
                    vpn: asc_test_1
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceReadFactsTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_facts import SolaceCloudBrokerFacts
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError, SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudGetFactsTask(SolaceReadFactsTask):

    def __init__(self, module):
        super().__init__(module)

    def validate_params(self):
        params = self.get_module().params

        from_dict = params['from_dict']
        if not isinstance(from_dict, dict):
            raise SolaceParamsValidationError("from_dict", type(from_dict), "invalid type, must be a dict")

        has_get_funcs = False
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
        solaceCloudServiceFacts = SolaceCloudBrokerFacts(search_dict, None)

        # check state of service
        service_state = solaceCloudServiceFacts.get_field(search_dict, 'creationState')
        if service_state != 'completed':
            raise SolaceParamsValidationError("service creationState", service_state, "is not 'completed'")

        facts = dict()
        param_get_formattedHostInventory = params['get_formattedHostInventory']
        if param_get_formattedHostInventory:
            field, value = self.get_formattedHostInventory(solaceCloudServiceFacts,
                                                           search_dict,
                                                           param_get_formattedHostInventory['host_entry'],
                                                           param_get_formattedHostInventory['api_token'],
                                                           param_get_formattedHostInventory['meta'])
            facts[field] = value

        result = self.create_result(rc=0, changed=False)
        result['facts'] = facts
        return None, result

    def get_formattedHostInventory(self,
                                   solace_cloud_service_facts: SolaceCloudBrokerFacts,
                                   search_dict: dict,
                                   host_entry: str,
                                   api_token: str = None,
                                   meta: dict = None):
        inv = dict(
            all=dict()
        )
        hosts = dict()

        secured_semp_details = solace_cloud_service_facts.get_semp_client_connection_details()
        msg_vpn_attributes = solace_cloud_service_facts.get_msg_vpn_attributes()
        # import logging, json
        # logging.debug(f"secured_semp_details=\n{secured_semp_details}")
        # logging.debug(f"msg_vpn_attributes=\n{msg_vpn_attributes}")
        hosts[host_entry] = {
            'meta': meta,
            'ansible_connection': 'local',
            'broker_type': 'solace_cloud',
            'solace_cloud_service_id': search_dict['serviceId'],
            'sempv2_host': secured_semp_details['secured']['uri_components']['host'],
            "sempv2_port": secured_semp_details['secured']['uri_components']['port'],
            "sempv2_is_secure_connection": True,
            "sempv2_username": secured_semp_details['authentication']['username'],
            "sempv2_password": secured_semp_details['authentication']['password'],
            "sempv2_timeout": "60",
            "vpn": msg_vpn_attributes['msgVpn'],
            "virtual_router": "primary"
        }
        if api_token:
            hosts[host_entry].update({'solace_cloud_api_token': api_token})

        inv['all']['hosts'] = hosts
        return 'formattedHostInventory', inv


def run_module():
    module_args = dict(
        from_dict=dict(type='dict', required=True),
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
