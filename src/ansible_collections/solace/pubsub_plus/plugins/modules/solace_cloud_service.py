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
module: solace_cloud_service
short_description: manage Solace Cloud services
description:
- Create & delete Solace Cloud services.
- "Note that you can't change a service once it has been created. Only option: delete & re-create."
- "Note that a service name must be unique in the global Solace Cloud namespace. Creating a service using an existing name (regardless in which account) will fail."
- Creating a service in Solace Cloud is a long-running process. In case creation fails, module will delete the service and try again, up to 3 times.
- >
    The module operates at a Solace Cloud Account level, therefor, you don't necessarily require an inventory file.
    Using `hosts: localhost` as a host and passing the Solace Cloud Api Token as an environment variable works as well.
notes:
- "The Solace Cloud API does not support updates to a service. Hence, changes are not supported here."
- "Module Solace Cloud API: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm"
options:
  name:
    description:
    - The name of the service to manage. Mandatory for state='present'.
    - "Note: The name must be a key, it is used as a YAML / JSON key. Use only ASCII, '-', or '_'. No whitespaces."
    type: str
    required: false
  solace_cloud_service_id:
    description:
    - The service id of a service in Solace Cloud.
    - Allowed option for state='absent'
    type: str
    required: false
    aliases: [service_id]
  wait_timeout_minutes:
    description:
    - Minutes to wait until service is created. Module polls every 30 seconds to check on service state.
    - wait_timeout_minutes == 0 ==> no waiting, module returns immediately.
    - wait_timeout_minutes > 0 ==> waits, polls every 30 seconds until service request completed.
    type: int
    required: false
    default: 30
  solace_cloud_settings:
    description:
    - Additional settings for state=present. See Reference documentation output of M(solace_cloud_get_service) for details.
    - "Note: For state=present, provide at least: msgVpnName, datacenterId, serviceTypeId, serviceClassId."
    type: dict
    required: false
    aliases: [settings]
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
- solace.pubsub_plus.solace.state
seealso:
- module: solace_cloud_get_service
- module: solace_cloud_get_services
- module: solace_cloud_get_facts
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: localhost
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
tasks:
- name: check input
  assert:
    that:
        - SOLACE_CLOUD_API_TOKEN is defined and SOLACE_CLOUD_API_TOKEN | length > 0
    fail_msg: "one or more variables not defined"

- name: create service
  solace_cloud_service:
    api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    name: "foo"
    settings:
        msgVpnName: "foo"
        datacenterId: "aws-ca-central-1a"
        serviceTypeId: "enterprise"
        serviceClassId: "enterprise-250-nano"
        eventBrokerVersion: "9.6"
        state: present

- set_fact:
    service_info: "{{ result.response }}"
    trust_store_uri: "{{ result.response.msgVpnAttributes.truststoreUri }}"

- name: extract inventory from service info
  solace_cloud_get_facts:
    from_dict: "{{ service_info }}"
    get_formattedHostInventory:
        host_entry: "{{ service_info.name }}"
        meta:
            service_name: "{{ service_info.name }}"
            service_id: "{{ service_info.serviceId }}"
            datacenterId: "{{ service_info.datacenterId }}"
            serviceTypeId: "{{ service_info.serviceTypeId}}"
            serviceClassId: "{{ service_info.serviceClassId }}"
            serviceClassDisplayedAttributes: "{{ service_info.serviceClassDisplayedAttributes }}"
    register: result

- name: save inventory to file
  copy:
    content: "{{ result.facts.formattedHostInventory | to_nice_yaml }}"
    dest: "./tmp/solace-cloud.{{ service_info.name }}.inventory.yml"
    changed_when: false
  delegate_to: localhost

- name: save service info to file
  copy:
    content: "{{ service_info | to_nice_yaml }}"
    dest: "./tmp/solace-cloud.{{ service_info.name }}.info.yml"
  delegate_to: localhost

- name: save service info to file
  copy:
    content: "{{ service_info | to_nice_yaml }}"
    dest: "./tmp/solace-cloud.{{ service_info.name }}.info.yml"
  delegate_to: localhost

- name: download certificate
  get_url:
    url: "{{ trust_store_uri }}"
    dest: "./tmp/solace-cloud.{{ service_info.name }}.pem"

- name: delete service
  solace_cloud_service:
    api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    name: "{{ service_info.name }}"
    state: absent
'''

RETURN = '''
response:
    description: response from the Api call. contains the service info.
    type: dict
    returned: success
    sample:
        accountingLimits:
        - id: NetworkUsage
          thresholds:
          - type: warning
            value: '75'
        adminState: completed
        attributes:
            customizedMessagingPorts: {}
            customizedResourceNames: {}
            monitoring: {}
            certificateAuthorities: []
            clientProfiles: []
            created: 1608128117689
            creationState: pending
            datacenterId: aws-eu-west-2a
            locked: false
            messagingStorage: 25
            msgVpnAttributes: {}
            msgVpnName: as_test_broker
            name: ansible_solace_test_broker
            serviceClassDisplayedAttributes:
            Clients: '250'
            High Availability: HA Group
            Message Broker Tenancy: Dedicated
            Network Speed: 450 Mbps
            Network Usage: 50 GB per month
            Queues: '250'
            Storage: 25 GB
            serviceClassId: enterprise-250-nano
            serviceId: 1a2o94jfedl9
            servicePackageId: DH-V13.0
            serviceStage: generalavailability
            serviceTypeId: enterprise
            timestamp: 0
            type: service
            userId: xxx
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
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError, SolaceError
from ansible.module_utils.basic import AnsibleModule
import logging
import json


class SolaceCloudServiceTask(SolaceCloudCRUDTask):

    KEY_SERVICE_ID = 'serviceId'
    KEY_NAME = 'name'

    def __init__(self, module):
        super().__init__(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def validate_params(self):
        # state=present: name is required
        # state=absent: name or service_id required
        params = self.get_module().params
        name = params.get('name', None)
        service_id = params.get(self.get_config().PARAM_SERVICE_ID, None)
        state = params['state']
        if state == 'present' and not name:
            raise SolaceParamsValidationError(
                'name', name, "required for state='present'")
        if state == 'absent' and not name and not service_id:
            raise SolaceParamsValidationError(
                f"name, {self.get_config().PARAM_SERVICE_ID}", name, "at least one is required for state='absent'")

    def get_args(self):
        params = self.get_module().params
        service_id = params.get(self.get_config().PARAM_SERVICE_ID, None)
        if service_id:
            return self.KEY_SERVICE_ID, service_id
        name = params['name']
        return [self.KEY_NAME, name]

    def get_func(self, key, value):
        if key == self.KEY_NAME:
            services = self.solace_cloud_api.get_services(self.get_config())
            service = self.solace_cloud_api.find_service_by_name_in_services(
                services, value)
            if not service:
                return None
            service_id = service[self.KEY_SERVICE_ID]
        else:
            service_id = value
        # save service_id
        self._service_id = service_id
        service = self.solace_cloud_api.get_service(
            self.get_config(), self._service_id)
        if not service:
            return None
        if service['creationState'] == 'failed':
            logging.debug(
                "solace cloud service '%s' in failed state - deleting ...", value)
            _resp = self.solace_cloud_api.delete_service(
                self.get_config(), self._service_id)
            return None
        wait_timeout_minutes = self.get_module().params['wait_timeout_minutes']
        if service['creationState'] != 'completed' and wait_timeout_minutes > 0:
            logging.debug(
                "solace cloud service creationState not completed (creationState=%s) - waiting to complete ...", service['creationState'])
            service = self.solace_cloud_api.wait_for_service_create_completion(
                self.get_config(), wait_timeout_minutes, self._service_id)
        return service

    def create_func(self, key, name, settings=None):
        if not settings:
            raise SolaceParamsValidationError(
                'settings', settings, "required for creating a service")
        data = {
            'adminState': 'start',
            'partitionId': 'default',
            'name': name
        }
        data.update(settings)
        return self.solace_cloud_api.create_service(self.get_config(), self.get_module().params['wait_timeout_minutes'], data)

    # TODO: wait until implemented in Solace Cloud API
    # def update_func(self, key, name, settings=None, delta_settings=None):
    #     if not settings:
    #         raise SolaceParamsValidationError('settings', settings, "required for creating a service")
    #     data = {
    #         'adminState': 'start',
    #         'partitionId': 'default',
    #         'name': name
    #     }
    #     data.update(settings)
    #     return self.solace_cloud_api.create_service(self.get_config(), self.get_module().params['wait_timeout_minutes'], data)

    def update_func(self, key, value, settings=None, delta_settings=None):
        msg = [
            f"Solace Cloud Service '{key}={value}' already exists.",
            "You cannot update an existing service. Only option: delete & re-create.",
            "changes requested: see 'delta'"
        ]
        raise SolaceError(msg, dict(delta=delta_settings))

    def delete_func(self, key, value):
        return self.solace_cloud_api.delete_service(self.get_config(), self._service_id)


def run_module():
    module_args = dict(
        name=dict(type='str', required=False, default=None),
        wait_timeout_minutes=dict(type='int', required=False, default=30)
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id())
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_state())
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceCloudServiceTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
