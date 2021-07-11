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
module: solace_gather_facts
short_description: gather broker facts
description: >
  Retrieve facts from the Solace broker and set 'ansible_facts.solace'.
  Call at the beginning of the playbook so all subsequent tasks can use '{{ ansible_facts.solace.<path-to-fact> }}' or M(solace_get_facts) module.
  Supports Solace Cloud and standalone brokers.
  Retrieves: service/broker info, about info, virtual router name, messaging endpoints, etc.
notes:
- In order to access other hosts' (other than the current 'inventory_host') facts, you must not use the 'serial' strategy for the playbook.
- "Module Sempv2 Config - about: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/about"
- "Module Sempv2 Config - broker: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/all/getBroker"
- "Module Solace Cloud Api - get service: https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm"
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.broker_config_solace_cloud
seealso:
- module: solace_get_facts
- module: solace_cloud_account_gather_facts
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
  solace_gather_facts:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:
- name: Gather Solace Facts
  solace_gather_facts:

- name: "Save hostvars to ./hostvars.json"
  copy:
    content: "{{ hostvars | to_nice_json }}"
    dest: ./hostvars.json
  delegate_to: localhost
'''

RETURN = '''
ansible_facts:
    description: "The facts as returned by the APIs. Element: 'solace'."
    type: dict
    returned: success
    elements: dict
    sample:
        ansible_facts:
            solace:
                isSolaceCloud: false
                about:
                    api:
                        platform: "VMR"
                        sempVersion: "2.17"
                    user:
                        globalAccessLevel: "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"
                        msgVpns:
                            - msgVpnName: "default"
                              accessLevel: "read-write"
                service_facts:
                    info: "various service/broker info"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceApiError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi, SolaceSempV1Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGatherFactsTask(SolaceBrokerGetTask):

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        self.sempv1_api = SolaceSempV1Api(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def add_path_value(self, dictionary, path_array, value):
        if len(path_array) > 1:
            if path_array[0] not in dictionary.keys():
                dictionary[path_array[0]] = {}
            self.add_path_value(
                dictionary[path_array[0]], path_array[1:], value)
        else:
            if(path_array[0] == ''):
                dictionary['broker'] = value
            else:
                dictionary[path_array[0]] = value

    def get_about_info(self):
        # GET /about, /about/api, /about/user, /about/user/msgVpns
        about_info = dict()
        path_array_list = [
            ["about"],
            ["about", "user"],
            ["about", "user", "msgVpns"],
            ["about", "api"]
        ]
        for path_array in path_array_list:
            resp = self.sempv2_api.make_get_request(
                self.get_config(), [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG] + path_array)
            self.add_path_value(about_info, path_array, resp)
        about_info['isSolaceCloud'] = self.get_config().is_solace_cloud()
        return about_info

    def get_service_info(self) -> dict:
        resp = dict(
            vpns=dict()
        )
        msg_vpns = self.sempv2_api.make_get_request(self.get_config(
        ), [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, "about", "user", "msgVpns"])
        for msg_vpn in msg_vpns:
            # GET /msgVpns/{msgVpnName}
            vpn_name = msg_vpn['msgVpnName']
            path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                          'msgVpns', vpn_name]
            msg_vpn_info = self.sempv2_api.get_object_settings(
                self.get_config(), path_array)
            resp['vpns'].update({vpn_name: msg_vpn_info})

        if self.get_config().is_solace_cloud():
            resp['service'] = self.solace_cloud_api.get_service(
                self.get_config(), self.get_module().params['solace_cloud_service_id'])
            resp['virtualRouterName'] = "n/a"
            # is this the potential virutal router?
            # 'primaryRouterName'
        else:
            # get service
            xml_post_cmd = "<rpc><show><service></service></show></rpc>"
            try:
                resp_service = self.sempv1_api.make_post_request(
                    self.get_config(), xml_post_cmd, SolaceTaskOps.OP_READ_OBJECT)
            except SolaceApiError as e:
                if self.get_config().reverse_proxy:
                    self.logExceptionAsError(
                        f"using reverse-proxy, failed to execute SEMP V1 call: {xml_post_cmd}", e)
                    # return resp
                raise e
            resp['service'] = resp_service['rpc-reply']['rpc']['show']['service']['services']
            # get virtual router
            xml_post_cmd = "<rpc><show><router-name></router-name></show></rpc>"
            resp_virtual_router = self.sempv1_api.make_post_request(
                self.get_config(), xml_post_cmd, SolaceTaskOps.OP_READ_OBJECT)
            resp['virtualRouterName'] = resp_virtual_router['rpc-reply']['rpc']['show']['router-name']['router-name']

        return resp

    def do_task(self):

        ansible_facts = dict(
            solace=dict()
        )
        about_info = self.get_about_info()
        service_info = self.get_service_info()
        ansible_facts['solace'].update(about_info)
        ansible_facts['solace'].update(service_info)

        result = self.create_result()
        result.update(dict(
            ansible_facts=ansible_facts
        ))
        return None, result


def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGatherFactsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
