# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalErrorAbstractMethod
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskConfig
from ansible.module_utils.basic import AnsibleModule
import json
import urllib.parse
import logging

SOLACE_API_HAS_IMPORT_ERROR = False
SOLACE_API_IMPORT_ERR_TRACEBACK = None
import traceback
try:
    import requests
    import xmltodict
except ImportError:
    SOLACE_API_HAS_IMPORT_ERROR = True
    SOLACE_API_IMPORT_ERR_TRACEBACK = traceback.format_exc()

class SolaceApi(object):

    def __init__(self, module: AnsibleModule):
        SolaceUtils.module_fail_on_import_error(module, SOLACE_API_HAS_IMPORT_ERROR, SOLACE_API_IMPORT_ERR_TRACEBACK)
        return

    def make_get_request(self, config: SolaceTaskConfig, path_array: list):
        return self.make_request(config, requests.get, path_array)

    def make_post_request(self, config: SolaceTaskConfig, path_array: list, json=None):
        return self.make_request(config, requests.post, path_array, json)

    def make_delete_request(self, config: SolaceTaskConfig, path_array: list):
        return self.make_request(config, requests.delete, path_array)

    def make_patch_request(self, config: SolaceTaskConfig, path_array: list, json=None):
        return self.make_request(config, requests.patch, path_array, json)

    def handle_response(self, resp):
        if resp.status_code != 200:
            self.handle_bad_response(resp)
        return self.handle_good_response(resp)    

    def handle_bad_response(self, resp):
        raise SolaceInternalErrorAbstractMethod()

    def handle_good_response(self, resp):
        j = resp.json()
        if 'data' in j.keys():
            return j['data']
        return dict()

    def make_request(self, config: SolaceTaskConfig, request_func, path_array: list, json=None):
        path = SolaceApi.compose_path(path_array)
        url = config.get_url(path)
        resp = request_func(
            url, 
            json=json,
            auth=config.get_auth(),
            timeout=config.get_timeout(),
            headers=config.get_headers(),
            params=None)
        SolaceApi.log_http_roundtrip(resp)
        return self.handle_response(resp)

    # def make_request(self, config: SolaceTaskConfig, request_func, path_array: list, json=None):
    #     path = SolaceApi.compose_path(path_array)
    #     url = config.get_url(path)
    #     try:
    #         resp = request_func(
    #             url, 
    #             json=json,
    #             auth=config.get_auth(),
    #             timeout=config.get_timeout(),
    #             headers=config.get_headers(),
    #             params=None)
    #         SolaceApi.log_http_roundtrip(resp)
    #         return self.handle_response(resp)
    #     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
    #         logging.debug("Request Error: %s", str(e))
    #         return False, str(e)

    @staticmethod
    def compose_path(path_array):
        if not type(path_array) is list:
            raise TypeError(f"argument 'path_array' is not an array but {type(path_array)}")
        # ensure elements are 'url encoded'
        # except first one, which is a path containing '/'
        paths = []
        for i, path_elem in enumerate(path_array):
            if path_elem == '':
                raise ValueError(f"path_elem='{path_elem}' is empty in path_array='{str(path_array)}'.")
            if i > 0:
                # deals with wildcards in topic strings
                # e.g. for MQTT subscriptions: '#' and '+'
                new_path_elem = urllib.parse.quote_plus(path_elem, safe=',')
                paths.append(new_path_elem)
            else:
                paths.append(path_elem)
        return '/'.join(paths)

    @staticmethod
    def _get_http_masked_headers(headers):
        _headers = dict(headers)
        if "Authorization" in _headers:
            _headers["Authorization"] = "***"
        return _headers

    @staticmethod
    def log_http_roundtrip(resp):
        if not solace_sys.ENABLE_LOGGING:
            return
        if hasattr(resp.request, 'body') and resp.request.body:
            try:
                decoded_body = resp.request.body.decode()
                request_body = json.loads(decoded_body)
            except AttributeError:
                request_body = resp.request.body
        else:
            request_body = "{}"

        if resp.text:
            try:
                resp_body = json.loads(resp.text)
            except json.JSONDecodeError:
                # try XML parsing it
                try:
                    resp_body = xmltodict.parse(resp.text)
                except Exception:
                    # print as text at least
                    resp_body = resp.text
        else:
            resp_body = None

        log = {
            'request': {
                'method': resp.request.method,
                'url': resp.request.url,
                'headers': SolaceApi._get_http_masked_headers(resp.request.headers),
                'body': request_body
            },
            'response': {
                'status_code': resp.status_code,
                'reason': resp.reason,
                'url': resp.url,
                'headers': dict(resp.headers),
                'body': resp_body
            }
        }
        logging.debug("\n%s", json.dumps(log, indent=2))
        return    
