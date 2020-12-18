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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceError
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule
if not sc.HAS_IMPORT_ERROR:
    import requests
    import xmltodict


class SolaceGatherFactsTask(su.SolaceTask):

    def __init__(self, module):
        sc.module_fail_on_import_error(module, sc.HAS_IMPORT_ERROR, sc.IMPORT_ERR_TRACEBACK)
        su.SolaceTask.__init__(self, module)
        return

    def _get_about_info(self):
        # GET /about, /about/api, /about/user, /about/user/msgVpns
        about_info = dict()

        path_array_list = [
            ["about"],
            ["about", "user"],
            ["about", "user", "msgVpns"],
            ["about", "api"]
        ]

        for path_array in path_array_list:
            ok, resp, headers = make_get_request(self.solace_config, [su.SEMP_V2_CONFIG] + path_array)
            if ok:
                addPathValue(about_info, path_array, resp)
            else:
                return False, resp

        about_info['isSolaceCloud'] = su.is_broker_solace_cloud(self.solace_config)
        about_info['Server'] = headers['Server']

        return True, about_info

    def _get_service_info_solace_cloud(self):
        # GET https://api.solace.cloud/api/v0/services/{{serviceId}}
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH, self.solace_config.solace_cloud_config['service_id']]
        return su.make_get_request(self.solace_config, path_array)

    def _get_service_info_broker(self):
        # GET /
        # issue: not much info for brokers with semp api version < 2.17
        # ok, resp, headers = make_get_request(self.solace_config, [su.SEMP_V2_CONFIG] + [''])
        # if not ok:
        #     return False, resp
        # get service info via SEMP v1
        xml_post_cmd = "<rpc><show><service></service></show></rpc>"
        ok, resp_service = make_sempv1_post_request(self.solace_config, xml_post_cmd)
        if not ok:
            resp_service['hint'] = "this could be a Solace Cloud service, but not configured as such."
            return False, resp_service
        resp = resp_service['rpc-reply']['rpc']['show']['service']['services']
        # get the virutal router name via SEMP v1
        xml_post_cmd = "<rpc><show><router-name></router-name></show></rpc>"
        ok, resp_virtual_router = make_sempv1_post_request(self.solace_config, xml_post_cmd)
        if not ok:
            resp_virtual_router['hint'] = "this could be a Solace Cloud service, but not configured as such."
            return False, resp_virtual_router
        resp['virtualRouterName'] = resp_virtual_router['rpc-reply']['rpc']['show']['router-name']['router-name']

        return ok, resp

    def _get_service_info(self):

        service_info = dict()

        if(su.is_broker_solace_cloud(self.solace_config)):
            ok, resp = self._get_service_info_solace_cloud()
        else:
            ok, resp = self._get_service_info_broker()

        if not ok:
            return False, resp

        service_info = resp

        return True, service_info

    def gather_facts(self):

        facts = dict(
            service=dict()
        )

        ok, resp = self._get_about_info()
        if not ok:
            return False, resp
        facts = resp

        ok, resp = self._get_service_info()
        if not ok:
            return False, resp
        facts['service'] = resp

        return True, facts


def make_get_request(solace_config, path_array):

    path = su.compose_path(path_array)

    try:
        resp = requests.get(
            solace_config.vmr_url + path,
            json=None,
            auth=solace_config.vmr_auth,
            timeout=solace_config.vmr_timeout,
            headers={'x-broker-name': solace_config.x_broker},
            params=None
        )
        if sc.ENABLE_LOGGING:
            sc.log_http_roundtrip(resp)
        if resp.status_code != 200:
            return False, su.parse_bad_response(resp), dict(resp.headers)
        return True, su.parse_good_response(resp), dict(resp.headers)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        return False, str(e), dict()


def make_sempv1_post_request(solace_config, xml_data):
    headers = {
        'Content-Type': 'application/xml',
        'x-broker-name': solace_config.x_broker
    }
    resp = requests.post(
        solace_config.vmr_url + "/SEMP",
        data=xml_data,
        auth=solace_config.vmr_auth,
        timeout=solace_config.vmr_timeout,
        headers=headers,
        params=None
    )
    if sc.ENABLE_LOGGING:
        sc.log_http_roundtrip(resp)
    if resp.status_code != 200:
        raise SolaceError("SEMP v1 call not successful. Pls check the log and raise an issue.")
    # SEMP v1 always returns 200 (it seems)
    # error: rpc-reply.execute-result.@code != ok or missing
    # if error: rpc-reply ==> display
    resp_body = xmltodict.parse(resp.text)
    try:
        code = resp_body['rpc-reply']['execute-result']['@code']
    except KeyError:
        return False, resp_body
    if code != "ok":
        return False, resp_body
    return True, resp_body


def addPathValue(dictionary, path_array, value):
    if len(path_array) > 1:
        if path_array[0] not in dictionary.keys():
            dictionary[path_array[0]] = {}
        addPathValue(dictionary[path_array[0]], path_array[1:], value)
    else:
        if(path_array[0] == ''):
            dictionary['broker'] = value
        else:
            dictionary[path_array[0]] = value


def run_module():
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_solace_cloud_config())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        ansible_facts=dict(),
        rc=0
    )

    solace_task = SolaceGatherFactsTask(module)
    ok, resp = solace_task.gather_facts()
    if not ok:
        result['rc'] = 1
        module.fail_json(msg=resp, **result)

    result['ansible_facts']['solace'] = resp
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
