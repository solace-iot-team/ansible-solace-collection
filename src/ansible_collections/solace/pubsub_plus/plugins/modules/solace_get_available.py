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
short_description: check if broker semp & spool is available
description:
- Check if broker service is reachable via SEMP and if the spool is ready. Calls "GET /about/api" and creates/deletes a test queue.
- To check, evaluate the return ``is_available``. ``rc==1`` is only set in case of a module or API error.
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/about/getAbout"
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue/createMsgVpnQueue"
options:
  wait_timeout_seconds:
    description:
    - Number of seconds to run tests for SEMP and spool availability. Polls every 5 seconds for `wait_timeout_seconds` until service is available.
    - Value must be `> 0`.
    type: int
    required: false
    default: 600
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
any_errors_fatal: true
module_defaults:
  solace_get_available:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: "Wait until broker service available"
    solace.pubsub_plus.solace_get_available:
    register: available_result

  - name: "Check if available"
    debug:
        msg:
        - "service not available"
    when: not available_result.is_available
    failed_when: true
'''

RETURN = '''
is_available:
    description: Flag indicating whether broker service is available.
    type: bool
    returned: always
is_semp_available:
    description: Flag indicating whether broker service SEMP is available.
    type: bool
    returned: always
is_spool_available:
    description: Flag indicating whether broker service spool is available.
    type: bool
    returned: always
msg:
    description: Details in case of an error.
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

import traceback
import uuid
import time
import logging
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceApiError, SolaceParamsValidationError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys

SOLACE_GET_AVAILABLE_HAS_IMPORT_ERROR = False
SOLACE_GET_AVAILABLE_ERR_TRACEBACK = None
try:
    import requests
except ImportError:
    SOLACE_GET_AVAILABLE_HAS_IMPORT_ERROR = True
    SOLACE_GET_AVAILABLE_ERR_TRACEBACK = traceback.format_exc()


class SolaceGetAvailableTask(SolaceBrokerGetTask):

    DELAY_SECONDS = 5

    def __init__(self, module):
        SolaceUtils.module_fail_on_import_error(
            module, SOLACE_GET_AVAILABLE_HAS_IMPORT_ERROR, SOLACE_GET_AVAILABLE_ERR_TRACEBACK)
        super().__init__(module)

    def validate_params(self):
        params = self.get_module().params
        wait_timeout_seconds = params['wait_timeout_seconds']
        if wait_timeout_seconds <= 0:
            raise SolaceParamsValidationError(
                'wait_timeout_seconds', wait_timeout_seconds, "must be >= 0")

    def calculate_max_tries(self, wait_timeout_seconds):
        if wait_timeout_seconds > self.DELAY_SECONDS:
            return wait_timeout_seconds // self.DELAY_SECONDS
        return 1

    def do_wait_semp_available(self, wait_timeout_seconds):
        ex = None
        try_count = 0
        max_tries = self.calculate_max_tries(wait_timeout_seconds)
        while try_count < max_tries:
            logging.debug("try number: %d", try_count)
            try:
                self.sempv2_api.make_get_request(
                    self.get_config(), [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG] + ["about", "api"])
                return True, None
            except SolaceApiError as e:
                if try_count + 1 >= max_tries or e.get_sempv2_error_code() == 72:
                    raise e
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.SSLError) as e:
                self.logExceptionAsDebug(type(e), e)
                ex = str(e)
            try_count += 1
            if try_count < max_tries:
                time.sleep(self.DELAY_SECONDS)
        return False, ex

    def do_wait_spool_available(self, wait_timeout_seconds):
        ex = None
        try_count = 0
        max_tries = self.calculate_max_tries(wait_timeout_seconds)
        vpn_name = self.get_module().params['msg_vpn']
        queue_name = str(uuid.uuid4())
        data = {
            'msgVpnName': vpn_name,
            'queueName': queue_name
        }
        create_path_array = [
            SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'queues']
        delete_path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                             'msgVpns', vpn_name, 'queues', queue_name]
        while try_count < max_tries:
            logging.debug("try number: %d", try_count)
            try:
                self.sempv2_api.make_post_request(
                    self.get_config(), create_path_array, data)
                self.sempv2_api.make_delete_request(
                    self.get_config(), delete_path_array)
                return True, None
            except SolaceApiError as e:
                if try_count + 1 >= max_tries or e.get_sempv2_error_code() == 72:
                    raise e
                self.logExceptionAsDebug(type(e), e)
                ex = e.get_ansible_msg()
            try_count += 1
            if try_count < max_tries:
                time.sleep(self.DELAY_SECONDS)
        return False, ex

    def do_task(self):
        self.validate_params()
        self.update_result({
            'is_available': False,
            'is_semp_available': False,
            'is_spool_available': False
        })
        wait_timeout_seconds = self.get_module().params['wait_timeout_seconds']
        is_semp_available = False
        is_spool_available = False
        is_spool_tested = False
        semp_ex = None
        spool_ex = None
        is_semp_available, semp_ex = self.do_wait_semp_available(
            wait_timeout_seconds)
        if is_semp_available:
            is_spool_tested = True
            is_spool_available, spool_ex = self.do_wait_spool_available(
                wait_timeout_seconds)
        self.update_result({
            'is_semp_available': is_semp_available,
            'is_available': is_semp_available and is_spool_available
        })
        if is_spool_tested:
            self.update_result({
                'is_spool_available': is_spool_available
            })
        _msg = []
        if semp_ex:
            _msg += ['HTTP response:', semp_ex]
        if spool_ex:
            _msg += ['SPOOL response:', spool_ex]
        msg = None if len(_msg) == 0 else _msg
        return msg, self.get_result()


def run_module():
    module_args = dict(
        wait_timeout_seconds=dict(type='int', required=False, default=600)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
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
