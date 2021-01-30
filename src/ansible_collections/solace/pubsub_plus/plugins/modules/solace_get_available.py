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
short_description: check if broker is available
description:
- Check if broker/service is reachable and responsive. Calls "GET /about".
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/about/getAbout"
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
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
    returned: always
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible.module_utils.basic import AnsibleModule


class SolaceGetAvailableTask(SolaceBrokerGetTask):

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def do_task(self):
        resp = self.sempv2_api.make_get_request(self.get_config(), [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG] + ["about"])
        result = self.create_result()
        result.update({'is_available': True})
        return resp, result


def run_module():
    module_args = dict(
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )
    solace_task = SolaceGetAvailableTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
