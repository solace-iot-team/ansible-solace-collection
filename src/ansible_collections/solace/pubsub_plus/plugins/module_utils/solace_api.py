# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
import os
__metaclass__ = type

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceCloudApiResponseDataError, SolaceEnvVarError, SolaceError, SolaceInternalErrorAbstractMethod, SolaceApiError, SolaceParamsValidationError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskConfig, SolaceTaskBrokerConfig, SolaceTaskSolaceCloudConfig
from ansible.module_utils.basic import AnsibleModule
import json
import urllib.parse
import logging
import time
import xml.etree.ElementTree as ET
import re


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
        SolaceUtils.module_fail_on_import_error(
            module, SOLACE_API_HAS_IMPORT_ERROR, SOLACE_API_IMPORT_ERR_TRACEBACK)
        self.module = module
        self.safe_for_path_array = None
        return

    def get_module(self):
        return self.module

    def get_auth(self, config: SolaceTaskConfig) -> str:
        raise SolaceInternalErrorAbstractMethod()

    def get_url(self, config: SolaceTaskConfig, path: str) -> str:
        raise SolaceInternalErrorAbstractMethod()

    def get_headers(self, config: SolaceTaskConfig, op: str) -> dict:
        return config.get_headers(op)

    def set_safe_for_path_array(self, safe_for_path_array):
        self.safe_for_path_array = safe_for_path_array

    def make_get_request(self, config: SolaceTaskConfig, path_array: list, module_op=SolaceTaskOps.OP_READ_OBJECT, query_params=None):
        return self.make_request(config, requests.get, path_array, json_body=None, query_params=query_params, module_op=module_op)

    def make_post_request(self, config: SolaceTaskConfig, path_array: list, json_body=None, module_op=SolaceTaskOps.OP_CREATE_OBJECT):
        return self.make_request(config, requests.post, path_array, json_body, query_params=None, module_op=module_op)

    def make_delete_request(self, config: SolaceTaskConfig, path_array: list, module_op=SolaceTaskOps.OP_DELETE_OBJECT):
        return self.make_request(config, requests.delete, path_array, json_body=None, query_params=None, module_op=module_op)

    def make_patch_request(self, config: SolaceTaskConfig, path_array: list, json_body=None, module_op=SolaceTaskOps.OP_UPDATE_OBJECT):
        return self.make_request(config, requests.patch, path_array, json_body, query_params=None, module_op=module_op)

    def make_put_request(self, config: SolaceTaskConfig, path_array: list, json_body=None, module_op=SolaceTaskOps.OP_UPDATE_OBJECT):
        return self.make_request(config, requests.put, path_array, json_body)

    def handle_response(self, resp, module_op):
        if resp.status_code != 200:
            self.handle_bad_response(resp, module_op)
        return self.handle_good_response(resp, module_op)

    def handle_bad_response(self, resp, module_op):
        raise SolaceInternalErrorAbstractMethod()

    def handle_good_response(self, resp, module_op):
        if resp.text:
            j = resp.json()
            if 'data' in j.keys():
                return j['data']
        return {}

    def get_response_body(self, resp):
        if resp.text:
            return resp.json()
        return None

    def _make_request(self, config: SolaceTaskConfig, request_func, path_array: list, json_body, query_params, module_op):
        if self.safe_for_path_array:
            _path = SolaceApi.compose_path(
                path_array, self.safe_for_path_array)
        else:
            _path = SolaceApi.compose_path(path_array)
        _url = self.get_url(config, _path)
        _query_params = query_params if query_params else {}
        _reverse_proxy_query_params = config.get_reverse_proxy_query_params()
        if _reverse_proxy_query_params:
            _query_params.update(_reverse_proxy_query_params)
        _headers = self.get_headers(config, module_op)
        # NOTE: url encode query params manually for SEMP
        _query_params_str = ''
        if _query_params:
            _query_params_str = urllib.parse.urlencode(
                _query_params, safe=',*')
        resp = request_func(
            _url,
            json=json_body,
            auth=self.get_auth(config),
            timeout=config.get_timeout(),
            headers=_headers,
            verify=config.get_validate_certs(),
            params=_query_params_str)
        SolaceApi.log_http_roundtrip(resp)
        return resp

    def make_request(self, config: SolaceTaskConfig, request_func, path_array: list, json_body=None, query_params=None, module_op=None):
        try_count = 0
        delay_secs = 30
        max_tries = 20
        do_retry = True
        while do_retry and try_count < max_tries:
            resp = self._make_request(config,
                                      request_func,
                                      path_array,
                                      json_body,
                                      query_params,
                                      module_op)
            if resp.status_code in [502, 504]:
                logging.warning("resp.status_code: %d, resp.reason: '%s', try number: %d",
                                resp.status_code, resp.reason, try_count)
                time.sleep(delay_secs)
            elif resp.status_code in [500]:
                _body = self.get_response_body(resp)
                if _body is not None:
                    if 'subCode' in _body:
                        if _body['subCode'] == '5000_104':
                            logging.warning("resp.status_code: %d, resp.message: '%s', try number: %d",
                                            resp.status_code, _body['message'], try_count)
                            time.sleep(delay_secs)
                            #  "status_code": 500,
                            #   "body": {
                            #   "message": "The server is too busy to respond",
                            #   "subCode": "5000_104",
                            #   "errorId": "52610751ae592888",
                            #   "traceId": "52610751ae592888"
                            # }
            else:
                do_retry = False
            try_count += 1
        return self.handle_response(resp, module_op)

    @staticmethod
    def compose_path(path_array, safe=','):
        if not type(path_array) is list:
            raise TypeError(
                f"argument 'path_array' is not an array but {type(path_array)}")
        # ensure elements are 'url encoded'
        # except first one, which is a path containing '/'
        paths = []
        for i, path_elem in enumerate(path_array):
            if path_elem == '':
                raise ValueError(
                    f"path_elem='{path_elem}' is empty in path_array='{str(path_array)}'.")
            if i > 0:
                # deals with wildcards in topic strings
                # e.g. for MQTT subscriptions: '#' and '+'
                new_path_elem = urllib.parse.quote_plus(path_elem, safe=safe)
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
    def get_http_request_body(resp):
        if hasattr(resp.request, 'body') and resp.request.body:
            try:
                decoded_body = resp.request.body.decode()
                request_body = json.loads(decoded_body)
            except AttributeError:
                request_body = resp.request.body
        else:
            request_body = "{}"
        return request_body

    @staticmethod
    def log_http_roundtrip(resp):
        if not solace_sys.ENABLE_LOGGING:
            return
        request_body = SolaceApi.get_http_request_body(resp)
        resp_body = SolaceUtils.parse_response_text(resp.text)
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

    @staticmethod
    def get_uri_path(uri):
        uri_components = urllib.parse.urlparse(uri)
        return uri_components.path

    @staticmethod
    def get_uri_query(uri):
        uri_components = urllib.parse.urlparse(uri)
        return uri_components.query


class SolaceSempV2Api(SolaceApi):

    API_BASE_SEMPV2_CONFIG = "/SEMP/v2/config"
    API_BASE_SEMPV2_PRIVATE_CONFIG = "/SEMP/v2/__private_config__"
    API_BASE_SEMPV2_MONITOR = "/SEMP/v2/monitor"
    API_BASE_SEMPV2_PRIVATE_MONITOR = "/SEMP/v2/__private_monitor__"
    API_BASE_SEMPV2_ACTION = "/SEMP/v2/action"
    API_BASE_SEMPV2_PRIVATE_ACTION = "/SEMP/v2/__private_action__"

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        return

    def get_auth(self, config: SolaceTaskBrokerConfig) -> str:
        return config.get_semp_auth()

    def get_url(self, config: SolaceTaskBrokerConfig, path: str) -> str:
        return config.get_semp_url(path)

    def get_sempv2_version(self, config: SolaceTaskBrokerConfig):
        resp = self.make_get_request(config, [
                                     SolaceSempV2Api.API_BASE_SEMPV2_CONFIG] + ["about", "api"], query_params=None)
        raw_api_version = SolaceUtils.get_key(resp, "sempVersion")
        # format: 2.21
        try:
            v = SolaceUtils.create_version(raw_api_version)
        except SolaceInternalError as e:
            raise SolaceInternalError(
                f"sempv2 version parsing failed: {raw_api_version}") from e
        return raw_api_version, v

    def handle_bad_response(self, resp, module_op):
        _resp = dict(
            status_code=resp.status_code,
            reason=resp.reason if resp.reason else None
        )
        if resp.text:
            _resp.update(dict(
                body=SolaceUtils.parse_response_text(resp.text)
            ))
        raise SolaceApiError(resp, _resp, self.get_module()._name, module_op)

    def get_object_settings(self, config: SolaceTaskBrokerConfig, path_array: list, module_op=SolaceTaskOps.OP_READ_OBJECT) -> dict:
        # returns settings or None if not found
        try:
            resp = self.make_get_request(config, path_array, module_op)
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
            raise SolaceApiError(e.get_http_resp(), resp,
                                 config.get_module()._name, module_op) from e
        return resp


class SolaceSempV2PagingGetApi(SolaceSempV2Api):

    def __init__(self, module: AnsibleModule, is_supports_paging: bool = True):
        super().__init__(module)
        self.next_url = None
        self.is_supports_paging = is_supports_paging
        return

    def get_url(self, config: SolaceTaskBrokerConfig, path: str) -> str:
        if self.next_url:
            parse_result = urllib.parse.urlparse(self.next_url)
            next_url_path = parse_result.path
            next_url_query = parse_result.query
            new_parse_result = parse_result._replace(
                netloc=config.get_broker_netloc())
            new_parse_result = new_parse_result._replace(
                path=config.get_broker_semp_base_path() + next_url_path)
            new_parse_result = new_parse_result._replace(query=next_url_query)
            new_next_url = new_parse_result.geturl()
            return new_next_url
        new_next_url = config.get_semp_url(path)
        return new_next_url

    def handle_good_response(self, resp, module_op):
        if resp.text:
            return resp.json()
        return {}

    def get_monitor_api_base(self) -> str:
        return SolaceSempV2Api.API_BASE_SEMPV2_MONITOR

    def get_objects(self,
                    config: SolaceTaskBrokerConfig,
                    api: str,
                    page_count: int,
                    path_array: list,
                    query_params: dict = None,
                    get_monitor_api_base_func=get_monitor_api_base) -> list:
        _query_params = {}
        if self.is_supports_paging:
            _query_params.update({
                "count": page_count
            })
        if query_params:
            if ("where" in query_params
                    and query_params['where'] is not None
                    and len(query_params['where']) > 0):
                _query_params.update({
                    "where": ','.join(query_params['where'])
                })
            if ("select" in query_params
                    and query_params['select'] is not None
                    and len(query_params['select']) > 0):
                _query_params.update({
                    "select": ','.join(query_params['select'])
                })
        api_base = self.API_BASE_SEMPV2_CONFIG
        if api == 'monitor':
            api_base = get_monitor_api_base_func()
        path_array = [api_base] + path_array
        result_list = []
        hasNextPage = True
        while hasNextPage:
            body = self.make_get_request(
                config, path_array, module_op=SolaceTaskOps.OP_READ_OBJECT_LIST, query_params=_query_params)
            data_list = []
            # monitor api may have collections as well
            collections_list = []
            if "data" in body.keys():
                data_list = body['data']
            if "collections" in body.keys():
                collections_list = body['collections']
            # merge collections & data into result_list. assuming same index and same length.
            for i, data in enumerate(data_list):
                result_element = dict(
                    data=data
                )
                if len(collections_list) > 0:
                    result_element.update(
                        dict(collections=collections_list[i]))
                result_list.append(result_element)
            # check if more pages
            if "meta" not in body:
                hasNextPage = False
            elif "paging" not in body["meta"]:
                hasNextPage = False
            elif "nextPageUri" not in body["meta"]["paging"]:
                hasNextPage = False
            else:
                self.next_url = body["meta"]["paging"]["nextPageUri"]
                _query_params = None
        self.next_url = None
        return result_list

    def get_all_objects_from_config_api(self, config: SolaceTaskBrokerConfig, path_array: list) -> list:
        return self.get_objects(config, self.API_BASE_SEMPV2_CONFIG, 100, path_array)


class SolaceSempV1Api(SolaceApi):

    API_BASE_SEMPV1 = "/SEMP"

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.call_num = -1

    def get_sempv1_version(self, config: SolaceTaskBrokerConfig):
        rpc_xml = "<rpc><show><service></service></show></rpc>"
        resp = self.make_post_request(
            config, rpc_xml, SolaceTaskOps.OP_READ_SEMP_VERSION)
        rpc_reply = resp['rpc-reply']
        raw_api_version = SolaceUtils.get_key(rpc_reply, "@semp-version")
        # format: soltr/9_9VMR
        s = raw_api_version[6:9].replace('_', '.')
        try:
            v = SolaceUtils.create_version(s)
        except SolaceInternalError as e:
            raise SolaceInternalError(
                f"sempv1 version parsing failed: {raw_api_version}") from e
        return raw_api_version, v

    def get_headers(self, config: SolaceTaskConfig, op: str) -> dict:
        headers = {
            'Content-Type': 'application/xml'
        }
        headers.update(config.get_headers(op))
        return headers

    def handle_response(self, resp, module_op):
        # SEMP v1 always returns 200 (it seems)
        # error: rpc-reply.execute-result.@code != ok or missing
        resp_body = xmltodict.parse(resp.text) if resp.text else None
        if resp.status_code != 200:
            raise SolaceApiError(
                resp, resp_body, self.get_module()._name, module_op)
        try:
            code = resp_body['rpc-reply']['execute-result']['@code']
        except KeyError as e:
            _err = {
                'call': xmltodict.parse(SolaceApi.get_http_request_body(resp)),
                'response': resp_body
            }
            raise SolaceApiError(
                resp, _err, self.get_module()._name, module_op) from e
        if code != "ok":
            _err = {
                'call': xmltodict.parse(SolaceApi.get_http_request_body(resp)),
                'response': resp_body
            }
            raise SolaceApiError(
                resp, _err, self.get_module()._name, module_op)
        return resp_body

    def convertDict2Sempv1RpcXmlString(self, d) -> str:
        rpc_elem = SolaceUtils.convertDict2XmlElem('rpc', d)
        return ET.tostring(rpc_elem, encoding='utf-8').decode('utf-8')

    def getNextCallKey(self):
        self.call_num = self.call_num + 1
        return 'rpc-call-' + str(self.call_num)

    def make_post_request(self, config: SolaceTaskConfig, xml_cmd: str, module_op: str):
        url = config.get_semp_url(self.API_BASE_SEMPV1)
        resp = requests.post(
            url,
            data=xml_cmd,
            auth=config.get_semp_auth(),
            timeout=config.get_timeout(),
            headers=self.get_headers(config, module_op),
            params=None
        )
        SolaceApi.log_http_roundtrip(resp)
        return self.handle_response(resp, module_op)


class SolaceSempV1PagingGetApi(SolaceSempV1Api):

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        return

    def get_objects(self, config: SolaceTaskBrokerConfig, xml_cmd: str, reponse_list_path_array: list) -> list:
        result_list = []
        hasNextPage = True
        while hasNextPage:
            semp_resp = self.make_post_request(
                config, xml_cmd, SolaceTaskOps.OP_READ_OBJECT_LIST)
            # extract the list
            _d = semp_resp
            for path in reponse_list_path_array:
                if _d and path in _d:
                    _d = _d[path]
                else:
                    # empty list / not found
                    return []
            if isinstance(_d, dict):
                resp = [_d]
            elif isinstance(_d, list):
                resp = _d
            else:
                raise SolaceInternalError(
                    f"unknown SEMP v1 return type: {type(_d)}")
            result_list.extend(resp)
            # see if there is more
            more_cookie = None
            if 'more-cookie' in semp_resp['rpc-reply']:
                more_cookie = semp_resp['rpc-reply']['more-cookie']
            if more_cookie:
                xml_cmd = xmltodict.unparse(more_cookie)
                hasNextPage = True
            else:
                hasNextPage = False
        return result_list


class SolaceCloudApi(SolaceApi):

    ENV_VAR_ANSIBLE_SOLACE_SOLACE_CLOUD_HOME = "ANSIBLE_SOLACE_SOLACE_CLOUD_HOME"
    ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_US = "us"
    ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_AU = "au"
    API_BASE_PATH_US = "https://api.solace.cloud/api/v0"
    API_BASE_PATH_AU = "https://api.solacecloud.com.au/api/v0"

    API_DATA_CENTERS = "datacenters"
    API_SERVICES = "services"
    API_REQUESTS = "requests"

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        return

    def get_api_base_path(self, config: SolaceTaskSolaceCloudConfig) -> str:
        solace_cloud_home_value = self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_US

        if config.solace_cloud_home is not None and config.solace_cloud_home != '':
            solace_cloud_home_value = config.solace_cloud_home.lower()
        else:
            solaceCloudHomeEnvVal = os.getenv(
                self.ENV_VAR_ANSIBLE_SOLACE_SOLACE_CLOUD_HOME)
            if solaceCloudHomeEnvVal is not None and solaceCloudHomeEnvVal != '':
                if solaceCloudHomeEnvVal.lower() == self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_US:
                    solace_cloud_home_value = self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_US
                elif solaceCloudHomeEnvVal.lower() == self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_AU:
                    solace_cloud_home_value = self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_AU
                else:
                    raise SolaceEnvVarError(self.ENV_VAR_ANSIBLE_SOLACE_SOLACE_CLOUD_HOME,
                                            solaceCloudHomeEnvVal,
                                            f"allowed values: {self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_US}, {self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_AU}")
        if solace_cloud_home_value == self.ANSIBLE_SOLACE_SOLACE_CLOUD_HOME_US:
            return self.API_BASE_PATH_US
        else:
            return self.API_BASE_PATH_AU

    def get_auth(self, config: SolaceTaskBrokerConfig) -> str:
        return config.get_solace_cloud_auth()

    def get_url(self, config: SolaceTaskBrokerConfig, path: str) -> str:
        return config.get_solace_cloud_url(path)

    def handle_response(self, resp, module_op):
        # POST: https://api.solace.cloud/api/v0/services: returns 201
        # POST: ../requests returns 202: accepted if long running request
        if resp.status_code not in [200, 201, 202]:
            self.handle_bad_response(resp, module_op)
        # TODO: test for deleting service (failed state)
        # import logging
        # logging.debug(f">>>>> handling good response, resp.status_code={resp.status_code}")
        return self.handle_good_response(resp, module_op)

    def handle_good_response(self, resp, module_op):
        _resp = super().handle_good_response(resp, module_op)
        if _resp == {}:
            # return the body
            if resp.text:
                j = resp.json()
                return j
        else:
            return _resp
        return {}

    def handle_bad_response(self, resp, module_op):
        _resp = dict(status_code=resp.status_code,
                     reason=resp.reason
                     )
        _resp.update({'body': SolaceUtils.parse_response_text(resp.text)})
        raise SolaceApiError(resp, _resp, self.get_module()._name, module_op)

    def get_data_centers(self, config: SolaceTaskSolaceCloudConfig) -> list:
        # GET /api/v0/datacenters
        resp = self.make_get_request(
            config, [self.get_api_base_path(config), self.API_DATA_CENTERS], query_params=None)
        return resp

    def _transform_service(self, service: dict) -> dict:
        # ----------
        # add eventBrokerVersion --> standardized settings across POST and GET
        # if it doesn't exist
        # msgVpnAttributes.vmrVersion="9.6.0.46"
        # eventBrokerVersion="9.6"
        if "eventBrokerVersion" in service:
            return service
        vmrVersion = None
        if "msgVpnAttributes" in service:
            if "vmrVersion" in service["msgVpnAttributes"]:
                vmrVersion = service['msgVpnAttributes']['vmrVersion']
        if vmrVersion:
            service['eventBrokerVersion'] = vmrVersion[0:3]
        else:
            # total hack, no fallback option though
            service['eventBrokerVersion'] = '9.6'
        # ----------
        return service

    def get_services(self, config: SolaceTaskSolaceCloudConfig) -> list:
        # GET https://api.solace.cloud/api/v0/services
        module_op = SolaceTaskOps.OP_READ_OBJECT_LIST
        try:
            _resp = self.make_get_request(
                config, [self.get_api_base_path(config), self.API_SERVICES], module_op)
        except SolaceApiError as e:
            resp = e.get_resp()
            # TODO: what is the code if solace cloud account has 0 services?
            if resp['status_code'] == 404:
                return []
            raise SolaceApiError(e.get_http_resp(), resp,
                                 self.get_module()._name, module_op) from e
        if isinstance(_resp, dict):
            return [self._transform_service(_resp)]
        # it is a list of services
        resp = []
        for _service in _resp:
            service = self._transform_service(_service)
            resp.append(service)
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
            raise SolaceInternalError(
                f"solace cloud response not 'dict' nor 'list' but {type(services)}")
        return None

    def get_service(self, config: SolaceTaskSolaceCloudConfig, service_id: str) -> dict:
        # GET https://api.solace.cloud/api/v0/services/{{serviceId}}?included=serviceClass
        # retrieves a single service
        module_op = SolaceTaskOps.OP_READ_OBJECT
        try:
            _resp = self.make_get_request(
                config, [self.get_api_base_path(config), self.API_SERVICES, service_id], module_op)
        except SolaceApiError as e:
            resp = e.get_resp()
            if resp['status_code'] == 404:
                return None
            raise SolaceApiError(e.get_http_resp(), resp,
                                 self.get_module()._name, module_op) from e
        return self._transform_service(_resp)

    def get_service_additional_hostnames(self, config: SolaceTaskSolaceCloudConfig, service_id: str) -> list:
        # GET https://api.solace.cloud/api/v0/services/{{serviceId}}?connectionDetails=false
        # retrieves a single service
        service = self.get_service(config, service_id)
        if not service:
            raise SolaceError(
                f"solace_cloud_service_id={service_id} not found")
        additionalHostnames = []
        if 'attributes' in service:
            if 'additionalHostnames' in service['attributes']:
                if isinstance(service['attributes']['additionalHostnames'], list):
                    additionalHostnames = service['attributes']['additionalHostnames']
        return additionalHostnames

    def get_services_with_details(self, config: SolaceTaskSolaceCloudConfig) -> list:
        # get services, then for each service, get details
        _services = self.get_services(config)
        services = []
        for _service in _services:
            services.append(self.get_service(config, _service['serviceId']))
        return services

    def create_service(self, config: SolaceTaskSolaceCloudConfig, wait_timeout_minutes: int, data: dict, try_count=0) -> dict:
        # POST https://api.solace.cloud/api/v0/services
        module_op = SolaceTaskOps.OP_CREATE_OBJECT
        resp = self.make_post_request(
            config, [self.get_api_base_path(config), self.API_SERVICES], data, module_op)
        _service_id = resp['serviceId']
        if wait_timeout_minutes > 0:
            res = self.wait_for_service_create_completion(
                config, wait_timeout_minutes, resp['serviceId'])
            if "failed" in res:
                logging.warn(
                    "solace cloud service creation failed, service_id=%s, try number: %d", _service_id, try_count)
                if try_count < 3:
                    time.sleep(10)
                    logging.warn(
                        "solace cloud service in failed state - deleting service_id=%s ...", _service_id)
                    _resp = self.delete_service(config, _service_id)
                    time.sleep(30)
                    logging.warn("creating solace cloud service again ...")
                    _resp = self.create_service(
                        config, wait_timeout_minutes, data, try_count + 1)
                    logging.warn("new service_id=%s", _resp['serviceId'])
                    return self.wait_for_service_create_completion(config, wait_timeout_minutes, _resp['serviceId'])
                else:
                    r = dict(
                        msg=f"create service: Solace Cloud API failed to create service after {try_count} attempts",
                        response=res
                    )
                    raise SolaceApiError(
                        None, r, self.get_module()._name, module_op)
            else:
                return res
        else:
            return resp

    def wait_for_service_create_completion(self, config: SolaceTaskSolaceCloudConfig, timeout_minutes: int, service_id: str) -> dict:
        module_op = SolaceTaskOps.OP_READ_OBJECT
        is_completed = False
        is_failed = False
        try_count = -1
        delay = 30  # seconds
        max_retries = (timeout_minutes * 60) // delay

        while not is_completed and not is_failed and try_count < max_retries:
            logging.debug("service_id:%s, try number: %d",
                          service_id, try_count + 1)
            resp = self.get_service(config, service_id)
            if not resp:
                # edge case: service deleted before creation completed
                raise SolaceApiError(
                    resp, "service not found - may have been deleted while creating", self.get_module()._name, module_op)
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
                msg=f"create service not completed, timeout(mins)={timeout_minutes}, creationState={resp['creationState']}",
                response=resp
            )
            raise SolaceApiError(None, r, self.get_module()._name, module_op)
        return resp

    def delete_service(self, config: SolaceTaskSolaceCloudConfig, service_id: str) -> dict:
        # DELETE https://api.solace.cloud/api/v0/services/{{serviceId}}
        path_array = [self.get_api_base_path(config),
                      SolaceCloudApi.API_SERVICES, service_id]
        return self.make_delete_request(config, path_array)

    def get_object_settings(self, config: SolaceTaskBrokerConfig, path_array: list) -> dict:
        # returns settings or None if not found
        module_op = SolaceTaskOps.OP_READ_OBJECT
        try:
            _resp = self.make_get_request(config, path_array, module_op)
            # api oddity: 'some' calls return a list with 1 dict in it
            # logging.debug(
            #     f"get_object_settings._resp=\n{json.dumps(_resp, indent=2)}")
            if isinstance(_resp, list):
                if len(_resp) == 1 and isinstance(_resp[0], dict):
                    resp = _resp[0]
                else:
                    raise SolaceCloudApiResponseDataError(self.get_module()._name,
                                                          'api response has more than 1 element in list, needs investigation', {'resp': _resp})
            else:
                resp = _resp
        except SolaceApiError as e:
            resp = e.get_resp()
            if resp['status_code'] == 404:
                return None
            raise SolaceApiError(e.get_http_resp(), resp,
                                 self.get_module()._name, module_op) from e
        return resp

    def get_service_request_status(self, config: SolaceTaskBrokerConfig, service_id: str, request_id: str):
        module_op = SolaceTaskOps.OP_READ_OBJECT
        # GET https://api.solace.cloud/api/v0/services/{paste-your-serviceId-here}/requests/{{requestId}}
        path_array = [self.get_api_base_path(config), self.API_SERVICES,
                      service_id, self.API_REQUESTS, request_id]
        resp = self.make_get_request(config, path_array, module_op)
        # resp may not yet contain 'adminProgress' depending on whether this creation has started yet
        # add it in
        if 'adminProgress' not in resp:
            resp['adminProgress'] = 'inProgress'
        return resp

    def wait_for_service_requests_to_finish(self, config: SolaceTaskBrokerConfig, timeout_minutes: int, service_id: str):
        module_op = SolaceTaskOps.OP_READ_OBJECT
        # GET https://api.solace.cloud/api/v0/services/{paste-your-serviceId-here}/requests
        # returns list of dicts,
        # - check all elements,
        # - if "adminProgress" == "inProgress", wait and try again
        # - raise SolaceApiError if timeout
        are_all_completed = False
        try_count = -1
        delay = 30  # seconds
        max_retries = (timeout_minutes * 60) // delay
        while not are_all_completed and try_count < max_retries:
            path_array = [self.get_api_base_path(config), self.API_SERVICES,
                          service_id, self.API_REQUESTS]
            resp = self.make_get_request(config, path_array, module_op)
            # logging.debug(f"wait_for_service_requests_to_finish(): resp=\n{json.dumps(resp, indent=2)}")
            # iterate through list to check if any adminProgress == inProgress
            # use generator:
            matches = (
                respElem for respElem in resp if respElem['adminProgress'] == 'inProgress')
            notCompletedElement = next(matches, None)
            if notCompletedElement is None:
                are_all_completed = True
            try_count += 1
            if not are_all_completed and timeout_minutes > 0:
                time.sleep(delay)

        if not are_all_completed:
            msg = [
                "timeout waiting for all outstanding service requests to be completed",
                f"timeout(mins)={timeout_minutes}",
                "request in progress:",
                str(notCompletedElement)]
            raise SolaceApiError(
                resp, msg, self.get_module()._name, module_op)
        return

    def make_service_post_request(self, config: SolaceTaskBrokerConfig, path_array: list, service_id: str, json_body, module_op):

        timeout_minutes = config.get_timeout() // 60
        # set min timeout to 5 mins
        timeout_minutes = max(timeout_minutes, 5)

        # check if there are any jobs still running against this service and wait until completed
        self.wait_for_service_requests_to_finish(
            config, timeout_minutes, service_id)

        # now make the request
        resp = self.make_request(config, requests.post, path_array, json_body)
        # import logging
        # import json
        # logging.debug(f"resp (make_request) = \n{json.dumps(resp, indent=2)}")
        request_id = resp['id']
        is_completed = False
        is_failed = False
        try_count = -1
        delay = 15  # seconds
        max_retries = (timeout_minutes * 60) // delay
        # wait 1 cycle before start polling
        time.sleep(delay)
        while not is_completed and not is_failed and try_count < max_retries:
            resp = self.get_service_request_status(config,
                                                   service_id,
                                                   request_id)
            # import logging, json
            # logging.debug(f"resp (get_service_request_status)= \n{json.dumps(resp, indent=2)}")
            is_completed = (resp['adminProgress'] == 'completed')
            is_failed = (resp['adminProgress'] == 'failed')
            try_count += 1
            if timeout_minutes > 0:
                time.sleep(delay)

        if is_failed:
            raise SolaceApiError(
                resp, resp, self.get_module()._name, module_op)
        if not is_completed:
            msg = [
                f"timeout service post request - not completed, timeout(mins)={timeout_minutes}, state={resp['adminProgress']}", str(resp)]
            raise SolaceInternalError(msg)
        return resp


class SolaceCloudApiCertAuthority(SolaceCloudApi):

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        return

    MAPPINGS = {
        'certAuthorityName': 'name'
    }

    # TODO: implement the other OPs: !=, <, >, <=, >=
    def filter(self, settings: dict, query_params: dict) -> dict:
        if not query_params:
            return settings
        where_list = []
        if ("where" in query_params and query_params['where'] and len(query_params['where']) > 0):
            where_list = query_params['where']
        is_match = True
        for where in where_list:
            # OP: ==
            where_elements = where.split('==')
            if len(where_elements) != 2:
                raise SolaceParamsValidationError(
                    'query_params.where', where, "cannot parse where clause - must be in format '{key}=={pattern}' (other ops are not supported)")
            sempv2_key = where_elements[0]
            pattern = where_elements[1]
            solace_cloud_key = self.MAPPINGS.get(sempv2_key, None)
            if not solace_cloud_key:
                raise SolaceParamsValidationError(
                    'query_params.where', where, f"unknown key for solace cloud '{sempv2_key}' - check with Solace Cloud API settings")
            # pattern match
            solace_cloud_value = settings.get(
                solace_cloud_key, None)
            if not solace_cloud_value:
                raise SolaceInternalError(
                    f"solace-cloud-key={solace_cloud_key} not found in solace cloud settings - likely a key map issue")
            # create regex
            regex = pattern.replace("*", ".+")
            this_match = re.search(regex, solace_cloud_value)
            is_match = (is_match and this_match)
            if not is_match:
                break
        if is_match:
            return settings
        return None

    def get_cert_authority(self, config, service_id, cert_authority_name, query_params):
        # GET services/{serviceId}/serviceCertificateAuthorities/{certAuthorityName}
        path_array = [self.get_api_base_path(config), SolaceCloudApi.API_SERVICES,
                      service_id, 'serviceCertificateAuthorities', cert_authority_name]
        resp = self.get_object_settings(config, path_array)
        cert_authority = resp['certificate']
        return self.filter(cert_authority, query_params)
