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
notes:
- "STATUS: B(EXPERIMENTAL)"
- "Does not support Solace Cloud API. If required, submit a feature request."
- "Module Sempv1 Config: https://docs.solace.com/Configuring-and-Managing/Configuring-LDAP-Authentication.htm"
- "Note: Self-Hosted Broker Service: most operations are NOT idempotent."
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
- name: create
  solace_service_authentication_ldap_profile:
    name: foo
    sempv1_settings:
      admin:
        admin-dn: adminDN
      search:
        base-dn:
          distinguished-name: baseDN
        filter:
          filter: searchFilter
      ldap-server:
        ldap-host: ldap://192.167.123.4:389
        server-index: "1"
    state: present

- name: update
  solace_service_authentication_ldap_profile:
    name: foo
    sempv1_settings:
      admin:
        admin-dn: adminDN
      search:
        base-dn:
          distinguished-name: DC=dev,DC=solace,DC=local
        filter:
          filter: "(SamAccountName= $CLIENT_USERNAME)"
      ldap-server:
        ldap-host: ldap://192.167.123.5:389
        server-index: 2
    state: present

- name: enable
  solace_service_authentication_ldap_profile:
    name: foo
    state: enabled

- name: disable
  solace_service_authentication_ldap_profile:
    name: foo
    state: disabled

- name: delete
  solace_service_authentication_ldap_profile:
    name: foo
    state: absent
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError, SolaceNoModuleSupportForSolaceCloudError, SolaceSempv1VersionNotSupportedError
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

    def check_min_sempv1_supported_version(self):
        min_sempv1_version = SolaceUtils.create_version(self.MIN_SEMP_V1_VERSION)
        raw_api_version, version = self.sempv1_api.get_sempv1_version(self.get_config())
        if version < min_sempv1_version:
            raise SolaceSempv1VersionNotSupportedError(self.get_module()._name, f"{version}({raw_api_version})", min_sempv1_version)

    def normalize_current_settings(self, current_settings: dict, new_settings: dict) -> dict:
        if self.get_config().is_solace_cloud():
            return current_settings
        # SEMP V1
        # TODO: implement to test if changes are requested.
        # not trivial, what is the schema?
        # convert current_settings to same data structure as new_settings
        return current_settings

    def do_task_extension(self, args, new_state, new_settings, current_settings):
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
        raise SolaceNoModuleSupportForSolaceCloudError(self.get_module()._name)

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
        _resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict))
        _resp_ldap_profile = _resp['rpc-reply']['rpc']['show']['ldap-profile']
        if _resp_ldap_profile:
            return _resp_ldap_profile['ldap-profile']
        else:
            return None

    def _disable_func_solace_cloud(self, ldap_profile_name):
        raise SolaceNoModuleSupportForSolaceCloudError(self.get_module()._name)

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
        _resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict))
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
        raise SolaceNoModuleSupportForSolaceCloudError(self.get_module()._name)

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
        _resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict))
        _call_log = {
            self.sempv1_api.getNextCallKey(): {
                'enable': {
                    'rpc': rpc_dict,
                    'response': _resp
                }
            }
        }
        return _call_log

    def _create_func_solace_cloud(self, ldap_profile_name, settings):
        raise SolaceNoModuleSupportForSolaceCloudError(self.get_module()._name)

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
        resp = self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(create_rpc_dict))
        if settings:
            resp = self._update_func_sempv1(ldap_profile_name, settings, settings)
        return resp

    def _update_func_solace_cloud(self, ldap_profile_name, settings, delta_settings):
        raise SolaceNoModuleSupportForSolaceCloudError(self.get_module()._name)

    def _send_sempv1_update(self, ldap_profile_name, key, val):
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
        return self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict))

    def _update_func_sempv1(self, ldap_profile_name, settings, delta_settings):
        if not settings:
            return None
        combined_resps = {}
        # iterate over settings.keys and send 1 update after the other
        for key, val in settings.items():
            if val:
                if key == 'search' and isinstance(val, dict):
                    # iterate through sarch
                    for skey, sval in val.items():
                        _resp = self._send_sempv1_update(ldap_profile_name, key, {skey: sval})
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
                    _resp = self._send_sempv1_update(ldap_profile_name, key, val)
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
        return self._update_func_sempv1(ldap_profile_name, settings, delta_settings)

    def _delete_func_solace_cloud(self, ldap_profile_name):
        raise SolaceNoModuleSupportForSolaceCloudError(self.get_module()._name)

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
        return self.sempv1_api.make_post_request(self.get_config(), self.sempv1_api.convertDict2Sempv1RpcXmlString(rpc_dict))


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
