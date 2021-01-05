# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceApiError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible.module_utils.basic import AnsibleModule
import json


class SolaceSempV2Api(SolaceApi):

    API_BASE_SEMPV2_CONFIG="/SEMP/v2/config"
    API_BASE_SEMPV2_MONITOR="/SEMP/v2/monitor"
    
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        return

    def get_sempv2_version(self, config: SolaceTaskBrokerConfig) -> str:
        resp = self.make_get_request(config, [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG] + ["about", "api"])
        return SolaceUtils.get_key(resp, "sempVersion")

    def handle_bad_response(self, resp):
        _resp = dict()
        if not resp.text:
            _resp = resp
        else:
            _resp = dict(status_code=resp.status_code,
                            reason=resp.reason,
                            body=json.loads(resp.text)
                            )
        raise SolaceApiError(_resp)

    def get_object_settings(self, config: SolaceTaskBrokerConfig, path_array: list) -> dict:
        # returns settings or None if not found
        try:
            resp = self.make_get_request(config, path_array)
        except SolaceApiError as e:
            resp = e.get_resp()
            # check if not found error, otherwise raise error
            if isinstance(resp, dict):
                if ('body' in resp and 'meta' in resp['body']):
                    meta = resp['body']['meta']
                    if ('responseCode' in meta and meta['responseCode'] == 400
                            and 'error' in meta
                            and 'code' in meta['error']
                            and meta['error']['code'] == 6):
                        return None
            raise SolaceApiError(resp)
        return resp