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
module: solace_get_available

short_description: Check if broker/service is reachable and responsive.

description: >
  Check if broker/service is reachable and responsive.
  Calls "GET /about" and sets "is_available=True/False".

extends_documentation_fragment:
- solace.broker

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
-
  name: "Check/wait until brokers available"
  hosts: "{{ brokers }}"
  gather_facts: no
  any_errors_fatal: true
  module_defaults:
    solace_get_available:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"

  tasks:

    - name: "Pause Until Broker/Service available"
      solace_get_available:
      register: _result
      until: "_result.is_available"
      retries: 25 # 25 * 5 seconds
      delay: 5 # Every 5 seconds
'''

RETURN = '''
is_available:
    description: Flag indicating whether broker was reachable or not.
    type: bool
msg:
    description: The response from the HTTP call or error description.
    type: str

samples:

    "is_available": false,
    "msg": "('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))",


'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils as su
from ansible.module_utils.basic import AnsibleModule
if not sc.HAS_IMPORT_ERROR:
    import requests

class SolaceGetAvailableTask(su.SolaceTask):

    def __init__(self, module):
        sc.module_fail_on_import_error(module, sc.HAS_IMPORT_ERROR, sc.IMPORT_ERR_TRACEBACK)
        su.SolaceTask.__init__(self, module)
        return

    def get_available(self):
        ok, resp = make_get_request(self.solace_config, [su.SEMP_V2_CONFIG] + ["about"])
        if not ok:
            return False, resp
        return True, resp


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
            return False, su.parse_bad_response(resp)
        return True, su.parse_good_response(resp)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        return False, str(e)


def run_module():
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        rc=0,
        is_available=True
    )

    solace_task = SolaceGetAvailableTask(module)
    ok, resp = solace_task.get_available()
    result['is_available'] = ok
    module.exit_json(msg=resp, **result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
