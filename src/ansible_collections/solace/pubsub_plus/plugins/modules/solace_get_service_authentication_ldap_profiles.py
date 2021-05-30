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
module: solace_get_service_authentication_ldap_profiles
short_description: get ldap profiles
description:
- "Get a list of LDAP Profile Objects configured on a Broker Service."
notes:
- "STATUS: B(EXPERIMENTAL)"
- "Module Sempv1: https://docs.solace.com/Configuring-and-Managing/Configuring-LDAP-Authentication.htm"
- "Module Solace Cloud: no API documentation available, reverse engineer from console."
options:
    where_name:
        description:
        - "Query for ldap profile name. Maps to 'profile-name' in the SEMP V1 API."
        - "Has no effect for Solace Cloud, there is only 1 profile named 'default'."
        required: false
        default: '*'
        type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_service_authentication_ldap_profile
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
  solace_get_service_authentication_ldap_profiles:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:
- name: example for self-hosted broker
  block:
    - name: create ldap profile
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

    - name: get
      solace_get_service_authentication_ldap_profiles:
        where_name: "foo"
      register: result
  when: broker_type != 'solace_cloud'

- name: example for Solace Cloud broker
  block:
    - name: create or update ldap profile
      solace_service_authentication_ldap_profile:
        name: default
        solace_cloud_settings:
          adminDn: adminDN
          ldapServerOne: ldap://192.167.123.4:389
          searchBaseDn: baseDN
          searchFilter: searchFilter
    - name: get
      solace_get_service_authentication_ldap_profiles:
      register: result
  when: broker_type == 'solace_cloud'

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
  sample:
    solace-cloud-sample:
      -   adminDn: adminDn
          adminPassword: adminPwd
          allowUnauthenticatedAuthentication: false
          enabled: true
          groupMembershipSecondarySearchBaseDn: null
          groupMembershipSecondarySearchDeref: ALWAYS
          groupMembershipSecondarySearchEnabled: false
          groupMembershipSecondarySearchFilter: (member=$ATTRIBUTE_VALUE_FROM_PRIMARY_SEARCH)
          groupMembershipSecondarySearchFilterAttributeFromPrimarySearch: null
          groupMembershipSecondarySearchFollowContinuationReferences: false
          groupMembershipSecondarySearchFollowContinuationShutdown: false
          groupMembershipSecondarySearchScope: SUBTREE
          groupMembershipSecondarySearchTimeout: 5
          id: default
          ldapServerOne: ldap://ldap_1.myorg.com:389
          ldapServerThree: null
          ldapServerTwo: ldap://ldap_2.myorg.com:389
          profileName: default
          searchBaseDn: ou=Users,o=orgId,dc=myorg,dc=com
          searchDeref: ALWAYS
          searchFilter: (cn=$CLIENT_USERNAME)
          searchFollowContinuationReferences: false
          searchScope: SUBTREE
          searchTimeout: 5
          startTls: false
          type: ldapAuthenticationProfile
    sempv1-sample:
      - admin-dn: null
        group-membership-secondary-search:
            base-dn: null
            deref: always
            filter: (member=$ATTRIBUTE_VALUE_FROM_PRIMARY_SEARCH)
            filter-attribute-from-primary-search: dn
            follow-continuation-references: 'Yes'
            scope: subtree
            shutdown: 'Yes'
            timeout: '5'
        ldap-servers-v2:
            ldap-server:
            -   index: '1'
                ldap-uri: null
            -   index: '2'
                ldap-uri: null
            -   index: '3'
                ldap-uri: null
        profile-name: default
        referral-session:
            last-error: None
            last-error-time: null
            referral-host-uri: null
        search:
            base-dn: null
            deref: always
            filter: (cn=$CLIENT_USERNAME)
            follow-continuation-references: 'Yes'
            scope: subtree
            timeout: '5'
        shutdown: 'Yes'
        starttls: 'No'
        tls: 'No'
        unauthenticated-authentication: Disallowed
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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceNoModuleSupportForSolaceCloudError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV1PagingGetApi, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetServiceAuthenticationLdapProfilesTask(SolaceGetTask):

    def __init__(self, module):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)
        self.sempv1_get_paging_api = SolaceSempV1PagingGetApi(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config

    def _get_list_solace_cloud(self):
        # GET services/{service-id}/requests/ldapAuthenticationProfile/default
        # only 1 exists, name=default
        service_id = self.get_config().get_params()['solace_cloud_service_id']
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id, 'ldapAuthenticationProfile', 'default']
        return [self.solace_cloud_api.get_object_settings(self.get_config(), path_array)]

    def get_list(self):
        if self.get_config().is_solace_cloud():
            return self._get_list_solace_cloud()
        # SEMP V1
        params = self.get_config().get_params()
        rpc_dict = {
            'show': {
                'ldap-profile': {
                    'profile-name': params['where_name']
                }
            }
        }
        # test: paging
        # 'count': '',
        # 'num-elements': 1
        response_list_path_array = ['rpc-reply', 'rpc', 'show', 'ldap-profile', 'ldap-profile']
        return self.sempv1_get_paging_api.get_objects(self.get_config(), self.sempv1_get_paging_api.convertDict2Sempv1RpcXmlString(rpc_dict), response_list_path_array)

    def do_task(self):
        objects = self.get_list()
        result = self.create_result_with_list(objects)
        return None, result


def run_module():
    module_args = dict(
        where_name=dict(type='str', required=False, default='*')
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )
    solace_task = SolaceGetServiceAuthenticationLdapProfilesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
