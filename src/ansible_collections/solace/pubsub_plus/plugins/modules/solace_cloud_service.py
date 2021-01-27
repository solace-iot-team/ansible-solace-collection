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
- Creating a service in Solace Cloud is a long-running process. In case creation fails, module will delete the service and try again, up to 3 times.
- "Reference: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm."
notes:
- "The Solace Cloud API does not support updates to a service. Hence, changes are not supported here."
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
    default: 20
  settings:
    description:
    - Additional settings for state=present. See Reference documentation output of M(solace_cloud_get_service) for details.
    - "Note: For state=present, provide at least: msgVpnName, datacenterId, serviceTypeId, serviceClassId."
    type: dict
    required: false
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
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
tasks:
- set_fact:
    api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"

- name: "Create Solace Cloud Service"
  solace_cloud_service:
    api_token: "{{ api_token }}"
    name: "foo"
    settings:
        msgVpnName: "foo"
        datacenterId: "aws-ca-central-1a"
        serviceTypeId: "enterprise"
        serviceClassId: "enterprise-250-nano"
        state: present

- set_fact:
    service_info: "{{ result.response }}"
    service_id: "{{ result.response.serviceId }}"
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
response:
    description: the response from the call
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
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
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
            raise SolaceParamsValidationError('name', name, "required for state='present'")
        if state == 'absent' and not name and not service_id:
            raise SolaceParamsValidationError(f"name, {self.get_config().PARAM_SERVICE_ID}", name, "at least one is required for state='absent'")

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
            service = self.solace_cloud_api.find_service_by_name_in_services(services, value)
            if not service:
                return None
            service_id = service[self.KEY_SERVICE_ID]
        else:
            service_id = value

        # save service_id
        self._service_id = service_id

        service = self.solace_cloud_api.get_service(self.get_config(), self._service_id)
        if not service:
            return None

        if service['creationState'] == 'failed':
            logging.debug("solace cloud service in failed state - deleting ...")
            _resp = self.solace_cloud_api.delete_service(self.get_config(), self._service_id)
            return None

        wait_timeout_minutes = self.get_module().params['wait_timeout_minutes']
        if service['creationState'] != 'completed' and wait_timeout_minutes > 0:
            logging.debug("solace cloud service creationState not completed (creationState=%s) - waiting to complete ...", service['creationState'])
            service = self.solace_cloud_api.wait_for_service_create_completion(self.get_config(), wait_timeout_minutes, self._service_id)

        return service

    def create_func(self, key, name, settings=None):
        if not settings:
            raise SolaceParamsValidationError('settings', settings, "required for creating a service")
        data = {
            'adminState': 'start',
            'partitionId': 'default',
            'name': name
        }
        data.update(settings)
        return self.solace_cloud_api.create_service(self.get_config(), self.get_module().params['wait_timeout_minutes'], data)

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
        wait_timeout_minutes=dict(type='int', required=False, default=20)
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id())
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_state())
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceCloudServiceTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
