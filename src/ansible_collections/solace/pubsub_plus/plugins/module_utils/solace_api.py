# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalErrorAbstractMethod, SolaceApiError, SolaceInternalError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskConfig, SolaceTaskBrokerConfig, SolaceTaskSolaceCloudConfig
from ansible.module_utils.basic import AnsibleModule
import json
import urllib.parse
import logging
import time

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
        if resp.text:
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
        if "authorization" in _headers:
            _headers["authorization"] = "***"
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
                            body=SolaceUtils.parse_response_body(resp.text)
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


class SolaceCloudApi(SolaceApi):

    API_BASE_PATH = "https://api.solace.cloud/api/v0"
    API_DATA_CENTERS = "datacenters"
    API_SERVICES = "services"
    
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        return

    def handle_response(self, resp):
        # POST: https://api.solace.cloud/api/v0/services: returns 201
        if not resp.status_code in [200, 201]:
            self.handle_bad_response(resp)
        # TODO: test for deleting service (failed state)
        import logging
        logging.debug(f">>>>> handling good response, resp.status_code={resp.status_code}")    
        return self.handle_good_response(resp)   

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

    def get_services(self, config: SolaceTaskSolaceCloudConfig) -> dict:
        # GET https://api.solace.cloud/api/v0/services
        # retrieves a list of services (either 'owned by me' or 'owned by org', depending on permissions)
        # returns dict() for 1 service, list for many, or None if not found
        try:
            resp = self.make_get_request(config, [self.API_BASE_PATH, self.API_SERVICES])
        except SolaceApiError as e:
            resp = e.get_resp()
            # TODO: what is the code if solace cloud account has 0 services?
            if resp['status_code'] == 404:
                return None
            raise SolaceApiError(resp)
        return resp

    def find_service_by_name_in_services(self, services, name):
        if isinstance(services, dict):
            if name == services.get('name'):
                return services
        elif isinstance(services, list):
            for service in services:
                if name == service.get('name'):
                    return service
        else:
            raise SolaceInternalError(f"solace cloud response not 'dict' nor 'list' but {type(services)}")
        return None

    def get_service(self, config: SolaceTaskSolaceCloudConfig, service_id: str) -> dict:
        # GET https://api.solace.cloud/api/v0/services/{{serviceId}}
        # retrieves a single service
        try:
            resp = self.make_get_request(config, [self.API_BASE_PATH, self.API_SERVICES, service_id])
        except SolaceApiError as e:
            resp = e.get_resp()
            if resp['status_code'] == 404:
                return None
            raise SolaceApiError(resp)
        return resp

    def create_service(self, config: SolaceTaskSolaceCloudConfig, wait_timeout_minutes: int, data: dict, try_count=0) -> dict:        
        # POST https://api.solace.cloud/api/v0/services
        resp = self.make_post_request(config, [self.API_BASE_PATH, self.API_SERVICES], data)
        _service_id = resp['serviceId']
        if wait_timeout_minutes > 0:
            res = self.wait_for_service_create_completion(config, wait_timeout_minutes, resp['serviceId'])
            if "failed" in res:
                if try_count < 3:
                    import logging
                    logging.debug("solace cloud service in failed state - deleting ...")
                    _resp = self.delete_service(config, _service_id)
                    logging.debug("creating solace cloud service again ...")
                    _resp = self.create_service(config, wait_timeout_minutes, data, try_count+1)
                    return self.wait_for_service_create_completion(config, wait_timeout_minutes, resp['serviceId'])
                else:
                    r = dict(
                        msg=f"create service: Solace Cloud API failed to create service after {try_count} attempts",
                        response=res
                    )
                    raise SolaceApiError(r)
            else:
                return res    
        else:
            return resp

    def wait_for_service_create_completion(self, config: SolaceTaskSolaceCloudConfig, timeout_minutes: int, service_id: str) -> dict:
        is_completed = False
        is_failed = False
        try_count = -1
        delay = 30  # seconds
        max_retries = (timeout_minutes * 60) // delay

        while not is_completed and not is_failed and try_count < max_retries:
            resp = self.get_service(config, service_id)
            if not resp:
                # edge case: service deleted before creation completed
                raise SolaceApiError("service not found - may have been deleted while creating")
            is_completed = (resp['creationState'] == 'completed')
            is_failed = (resp['creationState'] == 'failed')
            try_count += 1
            if timeout_minutes > 0:
                time.sleep(delay)

        if is_failed:
            return dict(
                failed=True,
                response=resp
            )
        if not is_completed:
            r = dict(
                msg=f"create service not completed, state={resp['creationState']}",
                response=resp
            )
            raise SolaceApiError(r)
        return resp

    def delete_service(self, config: SolaceTaskSolaceCloudConfig, service_id: str) -> dict:
        # DELETE https://api.solace.cloud/api/v0/services/{{serviceId}}
        path_array = [SolaceCloudApi.API_BASE_PATH, SolaceCloudApi.API_SERVICES, service_id]
        return self.make_delete_request(config, path_array)
