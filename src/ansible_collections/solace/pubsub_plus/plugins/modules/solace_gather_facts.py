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

short_description: Retrieve facts from the Solace event broker and set 'ansible_facts.solace'.

description: >
  Retrieves facts from the Solace event broker and set 'ansible_facts.solace'.
  Call at the beginning of the playbook so all subsequent tasks can use '{{ ansible_facts.solace.<path-to-fact> }}' or M(solace_get_facts) module.
  Supports Solace Cloud and brokers.
  Retrieves: service/broker info, about info, virtual router name, messaging endpoints, etc.

notes:
- In order to access other hosts' (other than the current 'inventory_host') facts, you must not use the 'serial' strategy for the playbook.
- "Reference about: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/about)."
- "Reference broker: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/all/getBroker)."
- "Reference Solace Cloud: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm) - Get Service / Connections Details."

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.solace_cloud_config

seealso:
- module: solace_get_facts

author:
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
-
  name: "Get Information about the broker / service"
  hosts: "{{ brokers }}"
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
      solace_cloud_api_token: "{{ solace_cloud_api_token | default(omit) }}"
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

msg, 
rc,
solace:
    about,
    service (solace cloud)
    service (broker)

ansible_facts.solace:
    description: The facts as returned from the APIs.
    type: dict
    returned: success
    elements: dict
    sample:
        ansible_facts:
            solace:
                isSolaceCloud: false
                Server: "Solace_VMR/9.6.0.27"
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

'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGatherFactsTask(SolaceBrokerGetTask):

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def add_path_value(self, dictionary, path_array, value):
        if len(path_array) > 1:
            if path_array[0] not in dictionary.keys():
                dictionary[path_array[0]] = {}
            self.add_path_value(dictionary[path_array[0]], path_array[1:], value)
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
            resp = self.sempv2_api.make_get_request(self.get_config(), [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG] + path_array )
            self.add_path_value(about_info, path_array, resp)
        about_info['isSolaceCloud'] = self.get_config().is_solace_cloud()
        return about_info


  # def _get_service_info_broker(self):
    #     # GET /
    #     # issue: not much info for brokers with semp api version < 2.17
    #     # ok, resp, headers = make_get_request(self.solace_config, [su.SEMP_V2_CONFIG] + [''])
    #     # if not ok:
    #     #     return False, resp
    #     # get service info via SEMP v1
    #     xml_post_cmd = "<rpc><show><service></service></show></rpc>"
    #     ok, resp_service = make_sempv1_post_request(self.solace_config, xml_post_cmd)
    #     if not ok:
    #         resp_service['hint'] = "this could be a Solace Cloud service, but not configured as such."
    #         return False, resp_service
    #     resp = resp_service['rpc-reply']['rpc']['show']['service']['services']
    #     # get the virutal router name via SEMP v1
    #     xml_post_cmd = "<rpc><show><router-name></router-name></show></rpc>"
    #     ok, resp_virtual_router = make_sempv1_post_request(self.solace_config, xml_post_cmd)
    #     if not ok:
    #         resp_virtual_router['hint'] = "this could be a Solace Cloud service, but not configured as such."
    #         return False, resp_virtual_router
    #     resp['virtualRouterName'] = resp_virtual_router['rpc-reply']['rpc']['show']['router-name']['router-name']

    #     return ok, resp

    def get_service_info(self):

        if self.get_config().is_solace_cloud:
            return self.solace_cloud_api.get_service(self.get_config(), self.get_module().params['solace_cloud_service_id'])
        else:
            raise NotImplementedError("implement sempv1_api ...")
            # return self.sempv1_api.get_service(...)

    def do_task(self):

        about_info = self.get_about_info()
        service_info = self.get_service_info()

        ansible_facts = dict(
            solace=dict(
                service=service_info
            )
        )
        ansible_facts['solace'].update(about_info)
        
        result = self.create_result()
        result.update(dict(
            ansible_facts=ansible_facts
        ))
        return None, result


# def make_sempv1_post_request(solace_config, xml_data):
#     headers = {
#         'Content-Type': 'application/xml',
#         'x-broker-name': solace_config.x_broker
#     }
#     resp = requests.post(
#         solace_config.vmr_url + "/SEMP",
#         data=xml_data,
#         auth=solace_config.vmr_auth,
#         timeout=solace_config.vmr_timeout,
#         headers=headers,
#         params=None
#     )
#     if sc.ENABLE_LOGGING:
#         sc.log_http_roundtrip(resp)
#     if resp.status_code != 200:
#         raise SolaceError("SEMP v1 call not successful. Pls check the log and raise an issue.")
#     # SEMP v1 always returns 200 (it seems)
#     # error: rpc-reply.execute-result.@code != ok or missing
#     # if error: rpc-reply ==> display
#     resp_body = xmltodict.parse(resp.text)
#     try:
#         code = resp_body['rpc-reply']['execute-result']['@code']
#     except KeyError:
#         return False, resp_body
#     if code != "ok":
#         return False, resp_body
#     return True, resp_body



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
