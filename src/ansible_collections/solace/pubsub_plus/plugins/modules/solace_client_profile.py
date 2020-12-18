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
module: solace_client_profile

short_description: client profile

description:
- "Configure a Client Profile object. Allows addition, removal and configuration of Client Profile objects on Solace Brokers in an idempotent manner."
- "Supports Solace Cloud Brokers as well as Solace Standalone Brokers."

notes:
- "Solace Cloud: Polls periodically until Client Profile created and only then returns."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile)."
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_client_profiles.htm)."

seealso:
- module: solace_get_client_profiles

options:
  name:
    description: Name of the client profile. Maps to 'clientProfileName' in the API.
    type: str
    required: true
    aliases: [client_profile, client_profile_name]

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.settings
- solace.pubsub_plus.solace.state
- solace.pubsub_plus.solace.solace_cloud_config

author:
  - Mark Street (@mkst)
  - Swen-Helge Huber (@ssh)
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
    solace_client_profile:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
        solace_cloud_api_token: "{{ solace_cloud_api_token | default(omit) }}"
        solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:

  - name: Delete Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        state: absent

  - name: Create Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        state: present

  - name: Update Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        settings:
          allowGuaranteedMsgSendEnabled: true
          allowGuaranteedMsgReceiveEnabled: true
          allowGuaranteedEndpointCreateEnabled: true
        state: present

  - name: Delete Client Profile
    solace_client_profile:
        name: "test_ansible_solace"
        state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 / Solace Cloud request.
    type: dict
    returned: success
'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceClientProfileTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'clientProfileName'

    SOLACE_CLOUD_DEFAULTS = {
        'allowTransactedSessionsEnabled': False,
        'allowBridgeConnectionsEnabled': False,
        'allowGuaranteedEndpointCreateEnabled': False,
        'allowSharedSubscriptionsEnabled': False,
        'allowGuaranteedMsgSendEnabled': False,
        'allowGuaranteedMsgReceiveEnabled': False,
        'elidingEnabled': False
    }

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn']]

    def lookup_item(self):
        return self.module.params['name']

    def _get_func_solace_cloud(self, solace_config, lookup_item_value):
        # GET /{paste-your-serviceId-here}/clientProfiles/{{clientProfileName}}
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH, solace_config.solace_cloud_config['service_id'], su.CLIENT_PROFILES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def _get_func(self, solace_config, vpn, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def get_func(self, solace_config, vpn, lookup_item_value):
        if(su.is_broker_solace_cloud(solace_config)):
            return self._get_func_solace_cloud(solace_config, lookup_item_value)
        else:
            return self._get_func(solace_config, vpn, lookup_item_value)

    def _create_func_solace_cloud(self, solace_config, client_profile_name, data):
        # POST /{paste-your-serviceId-here}/requests/clientProfileRequests
        body = su.compose_solace_cloud_body('create', 'clientProfile', data)
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH,
                      solace_config.solace_cloud_config['service_id'],
                      su.SOLACE_CLOUD_REQUESTS,
                      su.SOLACE_CLOUD_CLIENT_PROFILE_REQUESTS]
        return su.make_post_request(solace_config, path_array, body)

    def _create_func(self, solace_config, vpn, client_profile_name, data):
        # POST /msgVpns/{msgVpnName}/clientProfiles
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES]
        return su.make_post_request(solace_config, path_array, data)

    def create_func(self, solace_config, vpn, client_profile_name, settings=None):
        mandatory = {
            self.LOOKUP_ITEM_KEY: client_profile_name,
        }
        data = su.merge_dicts(self.SOLACE_CLOUD_DEFAULTS, mandatory, settings)
        if(su.is_broker_solace_cloud(solace_config)):
            return self._create_func_solace_cloud(solace_config, client_profile_name, data)
        else:
            return self._create_func(solace_config, vpn, client_profile_name, data)

    def _update_func_solace_cloud(self, solace_config, lookup_item_value, delta_settings, current_settings):
        # POST /{paste-your-serviceId-here}/requests/clientProfileRequests
        # for POST: add the current_settings, override with delta_settings

        # check that only 1 item and extract current settings
        if len(list(current_settings.keys())) != 1:
            resp = dict(
                error="Error parsing Solace Cloud Client Profile current settings.",
                current_settings=current_settings
            )
            return False, resp
        else:
            curr_settings = list(current_settings.values())[0]

        # inconsistency in Solace Cloud API:
        # elidingEnabled:
        #   create: must be provided as boolean (true or false)
        #   get: returns it as null if it was false
        #   update: must be provided as true or false

        if curr_settings and curr_settings['elidingEnabled'] is None:
            curr_settings['elidingEnabled'] = False

        mandatory = {
            self.LOOKUP_ITEM_KEY: lookup_item_value,
        }
        data = su.merge_dicts(curr_settings, mandatory, delta_settings)
        body = su.compose_solace_cloud_body('update', 'clientProfile', data)
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH,
                      solace_config.solace_cloud_config['service_id'],
                      su.SOLACE_CLOUD_REQUESTS,
                      su.SOLACE_CLOUD_CLIENT_PROFILE_REQUESTS]
        return su.make_post_request(solace_config, path_array, body)

    def _update_func(self, solace_config, vpn, lookup_item_value, delta_settings, current_settings):
        # PATCH /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, delta_settings)

    def update_func(self, solace_config, vpn, lookup_item_value, delta_settings=None, current_settings=None):
        if(su.is_broker_solace_cloud(solace_config)):
            return self._update_func_solace_cloud(solace_config, lookup_item_value, delta_settings, current_settings)
        else:
            return self._update_func(solace_config, vpn, lookup_item_value, delta_settings, current_settings)

    def _delete_func_solace_cloud(self, solace_config, client_profile_name):
        # POST /{paste-your-serviceId-here}/requests/clientProfileRequests
        data = {
            self.LOOKUP_ITEM_KEY: client_profile_name,
        }
        body = su.compose_solace_cloud_body('delete', 'clientProfile', data)
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH,
                      solace_config.solace_cloud_config['service_id'],
                      su.SOLACE_CLOUD_REQUESTS,
                      su.SOLACE_CLOUD_CLIENT_PROFILE_REQUESTS]
        return su.make_post_request(solace_config, path_array, body)

    def _delete_func(self, solace_config, vpn, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)

    def delete_func(self, solace_config, vpn, lookup_item_value):
        if(su.is_broker_solace_cloud(solace_config)):
            return self._delete_func_solace_cloud(solace_config, lookup_item_value)
        else:
            return self._delete_func(solace_config, vpn, lookup_item_value)


def run_module():
    """Entrypoint to module."""
    module_args = dict(
        name=dict(type='str', aliases=['client_profile', 'client_profile_name'], required=True)
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    arg_spec.update(su.arg_spec_solace_cloud_config())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceClientProfileTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():

    run_module()


if __name__ == '__main__':
    main()
