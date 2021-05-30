#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_service_authentication_ldap_profile
short_description: ldap profile
description:
- "Configure a LDAP Profile object on a Broker Service."
- "Self-Hosted Broker Service: most operations are NOT idempotent."
- "Solace Cloud Service: only 1 LDAP Profile object allowed, name='default'. Once LDAP Profile is created it cannot be deleted, disable instead."
notes:
- "STATUS: B(EXPERIMENTAL)"
- "Module Sempv1 Config: https://docs.solace.com/Configuring-and-Managing/Configuring-LDAP-Authentication.htm"
- "Module Solace Cloud: no API documentation available, reverse engineer from console."
options:
  name:
    description: Name of the LDAP Profile. Maps to 'ldap-profile' in the SEMP V1 API.
    required: true
    type: str
    aliases: [ldap_profile, ldap_profile_name]
  state:
    description: Target state.
    required: false
    default: present
    type: str
    choices:
      - present
      - absent
      - enabled
      - disabled
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv1_settings
- solace.pubsub_plus.solace.solace_cloud_settings
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_get_service_authentication_ldap_profiles
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
  name: "solace_service_authentication_ldap_profile example"
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace_service_authentication_ldap_profile:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
  tasks:
  - name: set args for ldap profile
    set_fact:
      ldap_profile_settings:
        ldap_profile_name: "{{ 'asct_ldap_profile_1' if broker_type != 'solace_cloud' else 'default' }}"
        allow_unauthentication_authentication: false
        admin_dn: uid=solace_service,ou=Users,o=orgId,dc=myorg,dc=com
        admin_pwd: solace_service_pwd
        start_tls: false
        ldap_server_uri_1: ldap://ldap_1.myorg.com:389
        ldap_server_uri_2: ldap://ldap_2.myorg.com:389
        search:
          base_dn: ou=Users,o=orgId,dc=myorg,dc=com
          filter: (cn=$CLIENT_USERNAME)
          follow_continuation_references: true
          deref: always
          scope: subtree
          timeout: 20

  - name: create
    solace_service_authentication_ldap_profile:
      name: "{{ ldap_profile_settings.ldap_profile_name }}"
      solace_cloud_settings:
        allowUnauthenticatedAuthentication: "{{ ldap_profile_settings.allow_unauthentication_authentication }}"
        adminDn: "{{ ldap_profile_settings.admin_dn }}"
        adminPassword: "{{ ldap_profile_settings.admin_pwd }}"
        ldapServerOne: "{{ ldap_profile_settings.ldap_server_uri_1 }}"
        searchBaseDn: "{{ ldap_profile_settings.search.base_dn }}"
        searchFilter: "{{ ldap_profile_settings.search.filter }}"
        searchFollowContinuationReferences: "{{ ldap_profile_settings.search.follow_continuation_references }}"
        searchDeref: "{{ ldap_profile_settings.search.deref }}"
        searchScope: "{{ ldap_profile_settings.search.scope }}"
        searchTimeout: "{{ ldap_profile_settings.search.timeout }}"
        startTls: "{{ ldap_profile_settings.start_tls }}"
      sempv1_settings:
        admin:
          admin-dn: "{{ ldap_profile_settings.admin_dn }}"
          admin-password: "{{ ldap_profile_settings.admin_pwd }}"
        search:
          base-dn:
            distinguished-name: "{{ ldap_profile_settings.search.base_dn }}"
          filter:
            filter: "{{ ldap_profile_settings.search.filter }}"
          timeout:
            duration: "{{ ldap_profile_settings.search.timeout }}"
        ldap-server:
          ldap-host: "{{ ldap_profile_settings.ldap_server_uri_1 }}"
          server-index: "1"
      state: present

  - name: update
    solace_service_authentication_ldap_profile:
      name: "{{ ldap_profile_settings.ldap_profile_name }}"
      solace_cloud_settings:
        ldapServerTwo: "{{ ldap_profile_settings.ldap_server_uri_2 }}"
      sempv1_settings:
        ldap-server:
          ldap-host: "{{ ldap_profile_settings.ldap_server_uri_2 }}"
          server-index: 2
      state: present

  - name: enable
    solace_service_authentication_ldap_profile:
      name: "{{ ldap_profile_settings.ldap_profile_name }}"
      state: enabled

  - name: disable
    solace_service_authentication_ldap_profile:
      name: "{{ ldap_profile_settings.ldap_profile_name }}"
      state: disabled

  - name: delete
    solace_service_authentication_ldap_profile:
      name: "{{ ldap_profile_settings.ldap_profile_name }}"
      state: absent
    when: broker_type != 'solace_cloud'
'''

RETURN = '''
response:
    description: The call/response to/from the API request.
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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError, SolaceNoModuleStateSupportError, SolaceSempv1VersionNotSupportedError, SolaceModuleUsageError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV1Api, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceServiceAuthenticationLdapProfileTask(SolaceBrokerCRUDTask):

    MIN_SEMP_V1_VERSION = "9.3"

    def __init__(self, module):
        super().__init__(module)
        self.sempv1_api = SolaceSempV1Api(module)
        self.solace_cloud_api = SolaceCloudApi(module)
        self.current_settings = None

    def check_min_sempv1_supported_version(self):
        min_sempv1_version = SolaceUtils.create_version(self.MIN_SEMP_V1_VERSION)
        raw_api_version, version = self.sempv1_api.get_sempv1_version(self.get_config())
        if version < min_sempv1_version:
            raise SolaceSempv1VersionNotSupportedError(self.get_module()._name, f"{version}({raw_api_version})", min_sempv1_version)

    def normalize_current_settings(self, current_settings: dict, new_settings: dict) -> dict:
        if self.get_config().is_solace_cloud():
            # remember current_settings for update call: it needs it
            self.current_settings = current_settings
            return current_settings
        # SEMP V1
        # TODO: implement to test if changes are requested.
        # not trivial, what is the schema?
        # convert current_settings to same data structure as new_settings
        return current_settings

    def do_task_extension(self, args, new_state, new_settings, current_settings):
        if not current_settings:
            name = self.get_module().params['name']
            usr_msg = f"ldap profile '{name}' does not exist; cannot enable/disable"
            raise SolaceModuleUsageError(self.get_module()._name, new_state, usr_msg)
        if self.get_config().is_solace_cloud():
            is_enabled = current_settings['enabled']
        else:
            is_enabled = True if current_settings['shutdown'] == 'No' else False
        if new_state == 'enabled':
            if is_enabled:
                return None, self.create_result(rc=0, changed=False)
            result = self.create_result(rc=0, changed=True)
            if not self.get_module().check_mode:
                result['response'] = self.enable_func(*args)
            return None, result
        if new_state == 'disabled':
            if not is_enabled:
                return None, self.create_result(rc=0, changed=False)
            result = self.create_result(rc=0, changed=True)
            if not self.get_module().check_mode:
                result['response'] = self.disable_func(*args)
            return None, result
        super().do_task_extension(args, new_state, new_settings, current_settings)

    def validate_params(self):
        params = self.get_module().params
        name = params.get('name', None)
        if self.get_config().is_solace_cloud() and name != 'default':
            raise SolaceParamsValidationError('name', name, "ldap profile name for Solace Cloud must be 'default'.")
        invalid_chars = '-'
        if SolaceUtils.stringContainsAnyChars(name, invalid_chars):
            raise SolaceParamsValidationError('name', name, f"contains 1 or more invalid chars from set: '{invalid_chars}'")

    def get_args(self):
        params = self.get_module().params
        return [params['name']]

    def get_settings_arg_name(self) -> str:
        if self.get_config().is_solace_cloud():
            return 'solace_cloud_settings'
        else:
            return 'sempv1_settings'

    def _get_func_solace_cloud(self, ldap_profile_name):
        # GET services/{service-id}/requests/ldapAuthenticationProfile/default
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, 'ldapAuthenticationProfile', ldap_profile_name]
        return self.solace_cloud_api.get_object_settings(self.get_config(), path_array)

    def get_func(self, ldap_profile_name):
        if self.get_config().is_solace_cloud():
            return self._get_func_solace_cloud(ldap_profile_name)
        # SEMP V1
        self.check_min_sempv1_supported_version()
        rpc_dict = {
            'show': {
                'ldap-profile': {
                    'profile-name': ldap_profile_name,
                    'detail': None
                }
            }
        }
        _resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict), SolaceTaskOps.OP_READ_OBJECT)
        _resp_ldap_profile = _resp['rpc-reply']['rpc']['show']['ldap-profile']
        if _resp_ldap_profile:
            return _resp_ldap_profile['ldap-profile']
        else:
            return None

    def _disable_func_solace_cloud(self, ldap_profile_name):
        data = {
            'enabled': False
        }
        return self._make_solace_cloud_update_request(ldap_profile_name, data)

    def disable_func(self, ldap_profile_name):
        if self.get_config().is_solace_cloud():
            return self._disable_func_solace_cloud(ldap_profile_name)
        # SEMP V1
        rpc_dict = {
            'authentication': {
                'ldap-profile': {
                    'profile-name': ldap_profile_name,
                    'shutdown': None
                }
            }
        }
        _resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict), SolaceTaskOps.OP_UPDATE_OBJECT)
        _call_log = {
            self.sempv1_api.getNextCallKey(): {
                'enable': {
                    'rpc': rpc_dict,
                    'response': _resp
                }
            }
        }
        return _call_log

    def _enable_func_solace_cloud(self, ldap_profile_name):
        data = {
            'enabled': True
        }
        return self._make_solace_cloud_update_request(ldap_profile_name, data)

    def enable_func(self, ldap_profile_name):
        if self.get_config().is_solace_cloud():
            return self._enable_func_solace_cloud(ldap_profile_name)
        # SEMP V1
        rpc_dict = {
            'authentication': {
                'ldap-profile': {
                    'profile-name': ldap_profile_name,
                    'no': {
                        'shutdown': None
                    }
                }
            }
        }
        _resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict), SolaceTaskOps.OP_UPDATE_OBJECT)
        _call_log = {
            self.sempv1_api.getNextCallKey(): {
                'enable': {
                    'rpc': rpc_dict,
                    'response': _resp
                }
            }
        }
        return _call_log

    def _compose_solace_cloud_request_body(self, operation: str, settings: dict) -> dict:
        return {
            'operation': operation,
            'ldapAuthenticationProfile': settings
        }

    def _make_solace_cloud_update_request(self, ldap_profile_name, settings):
        module_op = SolaceTaskOps.OP_UPDATE_OBJECT
        # POST services/{service-id}/requests/ldapAuthenticationProfileRequests
        data = self.current_settings if self.current_settings else {}
        data.update(settings if settings else {})
        body = self._compose_solace_cloud_request_body(operation='update', settings=data)
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, SolaceCloudApi.API_REQUESTS, 'ldapAuthenticationProfileRequests']
        return self.solace_cloud_api.make_service_post_request(self.get_config(), path_array, service_id, json_body=body, module_op=module_op)

    def _create_func_solace_cloud(self, ldap_profile_name, settings):
        data = {
            'profileName': ldap_profile_name,
            "searchDeref": "ALWAYS",
            "searchFilter": "(cn=$CLIENT_USERNAME)",
            "searchScope": "SUBTREE",
            "searchTimeout": 5,
            "groupMembershipSecondarySearchDeref": "ALWAYS",
            "groupMembershipSecondarySearchFilter": "(member=$ATTRIBUTE_VALUE_FROM_PRIMARY_SEARCH)",
            "groupMembershipSecondarySearchScope": "SUBTREE",
            "groupMembershipSecondarySearchTimeout": 5
        }
        data.update(settings if settings else {})
        return self._make_solace_cloud_update_request(ldap_profile_name, data)

    def create_func(self, ldap_profile_name, settings=None):
        if self.get_config().is_solace_cloud():
            return self._create_func_solace_cloud(ldap_profile_name, settings)
        # SEMP V1
        create_rpc_dict = {
            'authentication': {
                'create': {
                    'ldap-profile': {
                        'profile-name': ldap_profile_name
                    }
                }
            }
        }
        resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(create_rpc_dict), SolaceTaskOps.OP_CREATE_OBJECT)
        if settings:
            resp = self._update_func_sempv1(ldap_profile_name, settings, settings, SolaceTaskOps.OP_CREATE_OBJECT)
        return resp

    def _update_func_solace_cloud(self, ldap_profile_name, settings, delta_settings):
        return self._make_solace_cloud_update_request(ldap_profile_name, settings)

    def _send_sempv1_update(self, ldap_profile_name, key, val, op):
        _rpc_update_dict = {
            'authentication': {
                'ldap-profile': {
                    key: val
                }
            }
        }
        _rpc_dict = {
            'authentication': {
                'ldap-profile': {
                    'profile-name': ldap_profile_name
                }
            }
        }
        rpc_dict = SolaceUtils.merge_dicts_recursive(_rpc_dict, _rpc_update_dict)
        return self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict), op)

    def _update_func_sempv1(self, ldap_profile_name, settings, delta_settings, op):
        if not settings:
            return None
        combined_resps = {}
        # iterate over settings.keys and send 1 update after the other
        for key, val in settings.items():
            if val:
                if key == 'search' and isinstance(val, dict):
                    # iterate through sarch
                    for skey, sval in val.items():
                        _resp = self._send_sempv1_update(ldap_profile_name, key, {skey: sval}, op)
                        _call_log = {
                            self.sempv1_api.getNextCallKey(): {
                                key: {
                                    skey: sval,
                                    'response': _resp
                                }
                            }
                        }
                        combined_resps = SolaceUtils.merge_dicts_recursive(combined_resps, _call_log)
                else:
                    _resp = self._send_sempv1_update(ldap_profile_name, key, val, op)
                    _call_log = {
                        self.sempv1_api.getNextCallKey(): {
                            key: val,
                            'response': _resp
                        }
                    }
                    combined_resps = SolaceUtils.merge_dicts_recursive(combined_resps, _call_log)
        return combined_resps

    def update_func(self, ldap_profile_name, settings=None, delta_settings=None):
        if self.get_config().is_solace_cloud():
            return self._update_func_solace_cloud(ldap_profile_name, settings, delta_settings)
        return self._update_func_sempv1(ldap_profile_name, settings, delta_settings, SolaceTaskOps.OP_UPDATE_OBJECT)

    def _delete_func_solace_cloud(self, ldap_profile_name):
        raise SolaceNoModuleStateSupportError(self.get_module()._name, self.get_module().params['state'], 'Solace Cloud', 'disable profile instead')

    def delete_func(self, ldap_profile_name):
        if self.get_config().is_solace_cloud():
            return self._delete_func_solace_cloud(ldap_profile_name)
        # SEMP V1
        rpc_dict = {
            'authentication': {
                'no': {
                    'ldap-profile': {
                        'profile-name': ldap_profile_name
                    }
                }
            }
        }
        return self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict), SolaceTaskOps.OP_DELETE_OBJECT)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['ldap_profile', 'ldap_profile_name']),
        state=dict(type='str', default='present', choices=['absent', 'present', 'enabled', 'disabled'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_sempv1_settings())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )
    solace_task = SolaceServiceAuthenticationLdapProfileTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
