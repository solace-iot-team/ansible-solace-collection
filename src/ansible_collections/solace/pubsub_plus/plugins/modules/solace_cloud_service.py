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

version_added: "2.9.11"

short_description: "Create & delete Solace Cloud services."

description: >
    Create & delete Solace Cloud services.
    Note that you can't change a service once it has been created.
    Only option: delete & re-create.

notes:
- "The Solace Cloud API does not support updates to a service. Hence, changes are not supported here."
- "Creating a service in Solace Cloud is a long-running process. See examples for checking until completed."
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm)."

options:
  name:
    description:
        - The name of the service to manage. Mandatory for state='present'.
        - "Note: The name must be a key, it is used as a YAML / JSON key. Use only ASCII, '-', or '_'. No whitespaces."
    type: str
    required: false
  service_id:
    description: The service-id of the service to manage. Allowed option for state='absent'.
    type: str
    required: false
  settings:
    description:
        - Additional settings for state=present. See Reference documentation output of M(solace_cloud_get_service) for details.
        - "Note: For state=present, provide at least: msgVpnName, datacenterId, serviceTypeId, serviceClassId."
    type: dict
    required: false

extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_service_config
- solace.pubsub_plus.solace.state

author: Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''

hosts: all
gather_facts: no
any_errors_fatal: true
collections:
    - solace.pubsub_plus
tasks:
  - name: "Create Solace Cloud Service"
    solace_cloud_service:
        api_token: "{{ api_token_all_permissions }}"
        name: "{{ sc_service.name }}"
        settings:
            msgVpnName: "{{ sc_service.msgVpnName}}"
            datacenterId: "{{ sc_service.datacenterId }}"
            serviceTypeId: "{{ sc_service.serviceTypeId}}"
            serviceClassId: "{{ sc_service.serviceClassId }}"
            state: present

  - set_fact:
        sc_service_created_interim_info: "{{ result.response }}"
        sc_service_created_id: "{{ result.response.serviceId }}"

  - name: "Print Solace Cloud Service: service id"
    debug:
        msg: "service_id = {{ sc_service_created_id }}"

  - name: "Wait for Service Provisioning to Complete"
    solace_cloud_get_service:
        api_token: "{{ api_token_all_permissions }}"
        service_id: "{{ sc_service_created_id }}"
    register: get_service_result
    until: "get_service_result.rc != 0 or get_service_result.response.creationState == 'completed'"
    retries: 40
    delay: 30 # Every 30 seconds

  - set_fact:
        sc_service_created_info: "{{ result.response }}"

  - name: "Save New Solace Cloud Service Facts to File"
    copy:
        content: "{{ sc_service_created_info | to_nice_json }}"
        dest: "./tmp/facts.solace_cloud_service.{{ sc_service.name }}.json"
    delegate_to: localhost

'''

RETURN = '''

rc:
    description: return code, either 0 (ok), 1 (not ok)
    type: int
    returned: always
    sample:
        rc: 0
msg:
    description: error message if not ok
    type: str
    returned: error
response:
    description: the response from the create call.
    type: complex
    returned: success
    sample:
        accountingLimits:
        - id: NetworkUsage
          thresholds:
          - type: warning
            value: '75'
        unit: bytes
        value: '50000000000'
        adminState: start
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
    contains:
        serviceId:
            description: The service Id of the created service
            returned: "success for state=present"
            type: str
        adminState:
            description: The state of the service
            returned: success
            type: str
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_cloud_utils as scu
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudServiceTask(scu.SolaceCloudTask):

    LOOKUP_ITEM_KEY_SERVICE_ID = 'serviceId'
    LOOKUP_ITEM_KEY_NAME = 'name'

    def __init__(self, module):
        sc.module_fail_on_import_error(module, sc.HAS_IMPORT_ERROR, sc.IMPORT_ERR_TRACEBACK)
        scu.SolaceCloudTask.__init__(self, module)
        self._service_id = None
        self.validate_args(*(self.get_args() + self.lookup_item_kv()))
        return

    def lookup_item_kv(self):
        # state=present: name is required, return key=name, value=name
        # state=absent: name or service_id required. service_id takes precedence. return k,v depending on presence
        # return [k, v]
        # fail module on error
        # exception on code error
        state = self.module.params['state']
        if state == 'present':
            if self.module.params['name'] is not None:
                return [self.LOOKUP_ITEM_KEY_NAME, self.module.params['name']]
            else:
                msg = "Key 'name' not specified. Mandatory for state='present'."
                result = dict(changed=False, rc=1)
                self.module.fail_json(msg=msg, **result)
        elif state == 'absent':
            if self.module.params['service_id'] is not None:
                return [self.LOOKUP_ITEM_KEY_SERVICE_ID, self.module.params['service_id']]
            elif self._service_id is not None:
                # after get_func, self._service_id is set
                return [self.LOOKUP_ITEM_KEY_SERVICE_ID, self._service_id]
            elif self.module.params['name'] is not None:
                return [self.LOOKUP_ITEM_KEY_NAME, self.module.params['name']]
            else:
                msg = "Neither key specified: 'service_id' nor 'name'. At least one is required for state='absent'."
                result = dict(changed=False, rc=1)
                self.module.fail_json(msg=msg, **result)
        else:
            # should not be possible based on choices for state
            raise ValueError(f"unknown state={state}. pls raise an issue.")
        return

    def validate_args(self, lookup_item_key, lookup_item_value):
        return

    def get_func(self, sc_config, lookup_item_key, lookup_item_value):
        """Return ok flag and dict of the object if found, otherwise None."""
        service_id = None
        if lookup_item_key == self.LOOKUP_ITEM_KEY_NAME:
            # GET https://api.solace.cloud/api/v0/services
            # retrieves a list of services (either 'owned by me' or 'owned by org', depending on permissions)
            path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH]
            ok, resp = self.get_configuration(sc_config, path_array, lookup_item_key, lookup_item_value)
            if not ok:
                return False, resp
            # if found, retrieve the full configuration
            if resp is not None:
                if self.LOOKUP_ITEM_KEY_SERVICE_ID in resp:
                    service_id = resp[self.LOOKUP_ITEM_KEY_SERVICE_ID]
                else:
                    raise KeyError(f"Could not find key:'{self.LOOKUP_ITEM_KEY_SERVICE_ID}' in Solace Cloud GET services response. Pls raise an issue.")
            else:
                return True, None
        elif lookup_item_key == self.LOOKUP_ITEM_KEY_SERVICE_ID:
            service_id = lookup_item_value
        else:
            raise ValueError(f"unknown lookup_item_key='{lookup_item_key}'. Pls raise an issue.")

        # not found
        if not service_id:
            return True, None
        # save service_id
        self._service_id = service_id
        # GET https://api.solace.cloud/api/v0/services/{{serviceId}}
        # retrieves a single service
        path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH, service_id]
        return self.get_configuration(sc_config, path_array)

    def create_func(self, sc_config, lookup_item_key, lookup_item_value, settings=None):
        # POST https://api.solace.cloud/api/v0/services
        if not settings:
            fail_msg = "mandatory 'settings' missing or empty"
            result = dict(changed=False, rc=1)
            self.module.fail_json(msg="Create Service: " + fail_msg, **result)
        if lookup_item_key != self.LOOKUP_ITEM_KEY_NAME:
            raise ValueError(f"lookup_item_key='{self.LOOKUP_ITEM_KEY_NAME}' expected, but received '{lookup_item_key}. Pls raise an issue.")

        defaults = {
            'adminState': 'start',
            'partitionId': 'default'
        }
        fail_msg = None
        mandatory = {
            'name': lookup_item_value,
            'msgVpnName': settings.get('msgVpnName'),
            'datacenterId': settings.get('datacenterId'),
            'serviceClassId': settings.get('serviceClassId'),
            'serviceTypeId': settings.get('serviceTypeId')
        }
        missing_mandatory_keys = [k for k in mandatory if mandatory.get(k) is None]
        if missing_mandatory_keys:
            fail_msg = f"mandatory keys missing in 'settings': '{str(missing_mandatory_keys)}'"
        if fail_msg:
            result = dict(changed=False, rc=1)
            self.module.fail_json(msg="Create Service: " + fail_msg, **result)

        # this de-dups it again, settings override mandatory
        data = sc.merge_dicts(defaults, mandatory, settings)
        path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH]
        return scu.make_post_request(sc_config, path_array, data)

    def update_func(self, sc_config, lookup_item_key, lookup_item_value, delta_settings=None):
        resp = dict(
            error="Solace Cloud Service already exists. You can't update a Solace Cloud Service. Only option: delete & re-create."
        )
        return False, resp

    def delete_func(self, sc_config, lookup_item_key, lookup_item_value):
        # DELETE https://api.solace.cloud/api/v0/services/{{serviceId}}
        if lookup_item_key != self.LOOKUP_ITEM_KEY_SERVICE_ID:
            raise ValueError(f"lookup_item_key='{self.LOOKUP_ITEM_KEY_SERVICE_ID}' expected, but received '{lookup_item_key}. Pls raise an issue.")
        service_id = lookup_item_value
        path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH, service_id]
        return scu.make_delete_request(sc_config, path_array)

    def get_configuration(self, sc_config, path_array, lookup_item_key=None, lookup_item_value=None):
        """Return ok flag and dict of object if found, otherwise None."""

        ok, resp = scu.make_get_request(sc_config, path_array)
        # not found: ok=False, resp['status_code']==404
        if not ok:
            if resp['status_code'] == 404:
                return True, None
            return False, resp
        if lookup_item_key and lookup_item_value:
            service = self._find_service(resp, lookup_item_key, lookup_item_value)
        else:
            service = resp
        return True, service

    def _find_service(self, resp, lookup_item_key, lookup_item_value):
        """Return a dict of object if found, otherwise None."""
        if isinstance(resp, dict):
            value = resp.get(lookup_item_key)
            if value == lookup_item_value:
                return resp
        elif isinstance(resp, list):
            for item in resp:
                value = item.get(lookup_item_key)
                if value == lookup_item_value:
                    return item
        else:
            raise TypeError(f"argument 'resp' is not a 'dict' nor 'list' but {type(resp)}. Pls raise an issue.")
        return None


def run_module():
    """Entrypoint to module."""
    module_args = dict(
        name=dict(type='str', required=False, default=None),
        service_id=dict(type='str', required=False, default=None)
    )
    arg_spec = scu.arg_spec_solace_cloud()
    arg_spec.update(scu.arg_spec_state())
    arg_spec.update(scu.arg_spec_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceCloudServiceTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():

    run_module()


if __name__ == '__main__':
    main()
