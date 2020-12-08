#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""Collection of utility classes and functions to aid the solace_* modules."""

import traceback
import logging
import json
import time
SU_HAS_IMPORT_ERROR = False
SU_IMPORT_ERR_TRACEBACK = None
try:
    from inspect import signature
    import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
    import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_cloud_utils as scu
    from ansible.errors import AnsibleError
    import requests
except ImportError:
    SU_HAS_IMPORT_ERROR = True
    SU_IMPORT_ERR_TRACEBACK = traceback.format_exc()


""" Default Whitelist Keys """
DEFAULT_WHITELIST_KEYS = ['password']

""" Solace Cloud resources """
SOLACE_CLOUD_API_SERVICES_BASE_PATH = 'https://api.solace.cloud/api/v0/services'
SOLACE_CLOUD_REQUESTS = 'requests'
SOLACE_CLOUD_CLIENT_PROFILE_REQUESTS = 'clientProfileRequests'

""" Standard resources """
SEMP_V2_CONFIG = '/SEMP/v2/config'
SEMP_V2_MONITOR = '/SEMP/v2/monitor'

""" VPN level reources """

MSG_VPNS = 'msgVpns'
TOPIC_ENDPOINTS = 'topicEndpoints'
ACL_PROFILES = 'aclProfiles'
ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS = 'clientConnectExceptions'
CLIENT_PROFILES = 'clientProfiles'
CLIENT_USERNAMES = 'clientUsernames'
DMR_BRIDGES = 'dmrBridges'
BRIDGES = 'bridges'
BRIDGES_REMOTE_MSG_VPNS = 'remoteMsgVpns'
BRIDGES_REMOTE_SUBSCRIPTIONS = 'remoteSubscriptions'
BRIDGES_TRUSTED_COMMON_NAMES = 'tlsTrustedCommonNames'
CLIENTS = 'clients'

QUEUES = 'queues'
SUBSCRIPTIONS = 'subscriptions'
""" RDP Resources """
RDP_REST_DELIVERY_POINTS = 'restDeliveryPoints'
RDP_REST_CONSUMERS = 'restConsumers'
RDP_TLS_TRUSTED_COMMON_NAMES = 'tlsTrustedCommonNames'
RDP_QUEUE_BINDINGS = 'queueBindings'
""" DMR Resources """
DMR_CLUSTERS = 'dmrClusters'
LINKS = 'links'
REMOTE_ADDRESSES = 'remoteAddresses'
TLS_TRUSTED_COMMON_NAMES = 'tlsTrustedCommonNames'
""" cert authority resources """
CERT_AUTHORITIES = 'certAuthorities'
""" MQTT Sesion level reources """
MQTT_SESSIONS = 'mqttSessions'
MQTT_SESSION_SUBSCRIPTIONS = 'subscriptions'


class SolaceConfig(object):

    def __init__(self,
                 vmr_host,
                 vmr_port,
                 vmr_auth,
                 vmr_secure=False,
                 vmr_timeout=1,
                 x_broker='',
                 vmr_sempVersion='',
                 solace_cloud_config=None):
        self.vmr_auth = vmr_auth
        self.vmr_timeout = float(vmr_timeout)
        self.vmr_url = ('https' if vmr_secure else 'http') + '://' + vmr_host + ':' + str(vmr_port)
        self.x_broker = x_broker
        self.vmr_sempVersion = vmr_sempVersion
        self.solace_cloud_config = solace_cloud_config
        return


class SolaceTask:

    WHITELIST_KEYS = []
    REQUIRED_TOGETHER_KEYS = dict()

    def __init__(self, module):
        sc.module_fail_on_import_error(module, SU_HAS_IMPORT_ERROR, SU_IMPORT_ERR_TRACEBACK)
        self.module = module
        solace_cloud_api_token = self.module.params.get('solace_cloud_api_token', None)
        solace_cloud_service_id = self.module.params.get('solace_cloud_service_id', None)
        # either both are provided or none
        ok = ((solace_cloud_api_token and solace_cloud_service_id)
              or (not solace_cloud_api_token and not solace_cloud_service_id))
        if not ok:
            result = dict(changed=False, rc=1)
            msg = "must provide either both or none for Solace Cloud: solace_cloud_api_token={}, solace_cloud_service_id={}.".format(solace_cloud_api_token, solace_cloud_service_id)
            self.module.fail_json(msg=msg, **result)

        if ok and solace_cloud_api_token and solace_cloud_service_id:
            solace_cloud_config = dict(
                api_token=solace_cloud_api_token,
                service_id=solace_cloud_service_id
            )
        else:
            solace_cloud_config = None

        self.solace_config = SolaceConfig(
            vmr_host=self.module.params['host'],
            vmr_port=self.module.params['port'],
            vmr_auth=(self.module.params['username'], self.module.params['password']),
            vmr_secure=self.module.params['secure_connection'],
            vmr_timeout=self.module.params['timeout'],
            x_broker=self.module.params.get('x_broker', ''),
            vmr_sempVersion=self.module.params.get('semp_version', ''),
            solace_cloud_config=solace_cloud_config
        )
        return

    def do_task(self):

        result = dict(
            changed=False,
            response=dict()
        )

        crud_args = self.crud_args()

        settings = self.module.params['settings']

        if settings:
            # jinja treats everything as a string, so cast ints and floats
            settings = sc.type_conversion(settings, is_broker_solace_cloud(self.solace_config))

        ok, resp = self.get_func(self.solace_config, *(self.get_args() + [self.lookup_item()]))

        if not ok:
            self.module.fail_json(msg=resp, **result)
        # else response was good
        current_configuration = resp
        # whitelist of configuration items that are not returned by GET
        whitelist = self.get_whitelist_keys()
        required_together_keys_list = self.get_required_together_keys()

        if self.lookup_item() in current_configuration:
            if self.module.params['state'] == 'absent':
                if not self.module.check_mode:
                    ok, resp = self.delete_func(self.solace_config, *(self.get_args() + [self.lookup_item()]))
                    if not ok:
                        self.module.fail_json(msg=resp, **result)
                result['changed'] = True
            else:
                if settings and len(settings.keys()):
                    # compare new settings against configuration
                    current_settings = current_configuration[self.lookup_item()]
                    bad_keys = [key for key in settings if key not in current_settings.keys()]
                    # remove whitelist items from bad_keys
                    bad_keys = [item for item in bad_keys if item not in whitelist]
                    # removed keys
                    removed_keys = [item for item in settings if item in whitelist]
                    # fail if any unexpected settings found
                    if len(bad_keys):
                        msg = "invalid key(s) found in 'settings'"
                        result['response'] = dict(
                            invalid_keys=', '.join(bad_keys),
                            hint=[
                                    "possible causes:",
                                    "- wrong spelling or wrong key: check the SEMPv2 reference documentation",
                                    "- module's 'whitelist' isn't up to date: raise an issue"
                                ],
                            valid_keys=list(current_settings) + removed_keys
                        )
                        self.module.fail_json(msg=msg, **result)
                    # changed keys are those that exist in settings and don't match current settings
                    changed_keys = [x for x in settings if x in current_settings.keys()
                                    and settings[x] != current_settings[x]]
                    # add back in anything from the whitelist
                    changed_keys = changed_keys + removed_keys
                    # add any 'required together' keys
                    for together_keys in required_together_keys_list:
                        add_keys = [x for x in changed_keys if x in together_keys]
                        if(add_keys):
                            changed_keys += together_keys
                    # remove duplicates
                    changed_keys = list(dict.fromkeys(changed_keys))
                    # check if user has provided all the keys
                    missing_keys = []
                    for key in changed_keys:
                        if key not in settings:
                            missing_keys += [key]
                    if len(missing_keys):
                        msg = "missing key(s) in 'settings': " + ', '.join(missing_keys)
                        self.module.fail_json(msg=msg, **result)

                    if len(changed_keys):
                        delta_settings = {key: settings[key] for key in changed_keys}
                        if not self.module.check_mode:
                            crud_args.append(delta_settings)
                            # Note:
                            # only add current_settings for modules that support it.
                            # parameter must be called 'current_settings'
                            update_func_signature = signature(self.update_func, follow_wrapped=False)
                            for param in update_func_signature.parameters.values():
                                if param.name == "current_settings":
                                    crud_args.append(current_configuration)

                            ok, resp = self.update_func(self.solace_config, *crud_args)
                            result['response'] = resp
                            if not ok:
                                self.module.fail_json(msg="Error in update_func(). Pls raise an issue.", **result)
                        result['delta'] = delta_settings
                        result['changed'] = True
                else:
                    result['response'] = current_configuration[self.lookup_item()]
        else:
            if self.module.params['state'] == 'present':
                if not self.module.check_mode:
                    if settings:
                        crud_args.append(settings)
                    ok, resp = self.create_func(self.solace_config, *crud_args)
                    if ok:
                        result['response'] = resp
                    else:
                        self.module.fail_json(msg=resp, **result)
                result['changed'] = True

        return result

    def get_func(self, solace_config, *args):
        return False, dict()

    def create_func(self, solace_config, *args):
        return False, dict()

    def update_func(self, solace_config, *args):
        return False, dict()

    def delete_func(self, solace_config, *args):
        return False, dict()

    def lookup_item(self):
        return

    def get_args(self):
        return []

    def crud_args(self):
        return self.get_args() + [self.lookup_item()]

    def lookup_semp_version(self, semp_version):
        raise AnsibleError("argument 'semp_version' not supported by module: {}. implement 'lookup_semp_version()' in module.".format(self.module._name))

    def get_semp_version_key(self, lookup_dict, lookup_vmr_semp_version, lookup_key):
        try:
            v = float(lookup_vmr_semp_version)
        except ValueError:
            raise ValueError("semp_version: '{}' cannot be converted to a float. see 'solace_get_facts' for examples of how to pass in the 'semp_version' argument.".format(lookup_vmr_semp_version))
        ok, version_key = self.lookup_semp_version(v)
        if not ok:
            raise ValueError("unsupported semp_version: '{}'".format(lookup_vmr_semp_version))

        if version_key not in lookup_dict:
            raise ValueError("version_key: '{}' not found in lookup_dict: {}".format(version_key, json.dumps(lookup_dict)))
        version_lookup_dict = lookup_dict[version_key]
        if lookup_key not in version_lookup_dict:
            raise ValueError("lookup_key: '{}' not found in lookup_dict['{}']: '{}'".format(lookup_key, version_key, json.dumps(version_lookup_dict)))
        return version_lookup_dict[lookup_key]

    def get_whitelist_keys(self):
        whitelist = DEFAULT_WHITELIST_KEYS
        whitelist.extend(self.WHITELIST_KEYS)
        return whitelist

    def get_required_together_keys(self):
        return self.REQUIRED_TOGETHER_KEYS

    def get_list_default_query_params(self):
        return 'count=100'

    def execute_get_list(self, path_array):

        query = self.get_list_default_query_params()
        if query is None:
            query = ''

        query_params = self.module.params['query_params']
        if query_params:
            if ("select" in query_params
                    and query_params['select'] is not None
                    and len(query_params['select']) > 0):
                query += ('&' if query != '' else '')
                query += "select=" + ','.join(query_params['select'])
            if ("where" in query_params
                    and query_params['where'] is not None
                    and len(query_params['where']) > 0):
                where_array = []
                for _i, where_elem in enumerate(query_params['where']):
                    where_array.append(where_elem.replace('/', '%2F'))
                query += ('&' if query != '' else '')
                query += "where=" + ','.join(where_array)

        api_path = SEMP_V2_CONFIG
        if self.module.params['api'] == 'monitor':
            api_path = SEMP_V2_MONITOR
        path_array = [api_path] + path_array

        path = compose_path(path_array)

        url = self.solace_config.vmr_url + path + ("?" + query if query is not None else '')

        result_list = []

        hasNextPage = True

        while hasNextPage:

            try:
                resp = requests.get(
                            url,
                            json=None,
                            auth=self.solace_config.vmr_auth,
                            timeout=self.solace_config.vmr_timeout,
                            headers={'x-broker-name': self.solace_config.x_broker},
                            params=None
                )

                if sc.ENABLE_LOGGING:
                    sc.log_http_roundtrip(resp)

                if resp.status_code != 200:
                    return False, parse_bad_response(resp)
                else:
                    body = resp.json()
                    if "data" in body.keys():
                        result_list.extend(body['data'])

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                return False, str(e)

            if "meta" not in body:
                hasNextPage = False
            elif "paging" not in body["meta"]:
                hasNextPage = False
            elif "nextPageUri" not in body["meta"]["paging"]:
                hasNextPage = False
            else:
                url = body["meta"]["paging"]["nextPageUri"]

        return True, result_list

###
# End Class SolaceTask

# composable argument specs


def arg_spec_broker():
    return dict(
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=8080),
        secure_connection=dict(type='bool', default=False),
        username=dict(type='str', default='admin'),
        password=dict(type='str', default='admin', no_log=True),
        timeout=dict(type='int', default='10', required=False),
        x_broker=dict(type='str', default='')
    )


def arg_spec_solace_cloud_config():
    return dict(
        solace_cloud_api_token=dict(type='str', required=False, no_log=True, default=None),
        solace_cloud_service_id=dict(type='str', required=False, default=None)
    )


def arg_spec_vpn():
    return dict(
        msg_vpn=dict(type='str', required=True)
    )


def arg_spec_virtual_router():
    return dict(
        virtual_router=dict(type='str', default='primary', choices=['primary', 'backup'])
    )


def arg_spec_settings():
    return dict(
        settings=dict(type='dict', required=False)
    )


def arg_spec_semp_version():
    return dict(
        semp_version=dict(type='str', required=True)
    )


def arg_spec_state():
    return dict(
        state=dict(type='str', default='present', choices=['absent', 'present'])
    )


def arg_spec_name():
    return dict(
        name=dict(type='str', required=True)
    )


def arg_spec_crud():
    arg_spec = arg_spec_name()
    arg_spec.update(arg_spec_settings())
    arg_spec.update(arg_spec_state())
    return arg_spec


def arg_spec_get_list():
    return dict(
        api=dict(type='str', default='config', choices=['config', 'monitor']),
        query_params=dict(type='dict',
                          required=False,
                          options=dict(
                            select=dict(type='list', default=[], elements='str'),
                            where=dict(type='list', default=[], elements='str')
                          )
                          )
    )

def arg_spec_get_list_monitor():
    return dict(
        query_params=dict(type='dict',
                          required=False,
                          options=dict(
                            select=dict(type='list', default=[], elements='str'),
                            where=dict(type='list', default=[], elements='str')
                          )
                          )
    )


def merge_dicts(*argv):
    data = dict()
    for arg in argv:
        if arg:
            data.update(arg)
    return data


def _build_config_dict(resp, key):
    if not type(resp) is dict:
        raise TypeError("argument 'resp' is not a 'dict' but {}. Hint: check you are using Sempv2 GET single item call and not a list of items.".format(type(resp)))
    # wrong LOOKUP_ITEM_KEY in module
    if key not in resp:
        raise ValueError("wrong 'LOOKUP_ITEM_KEY' in module. semp GET response does not contain key='{}'".format(key))
    # resp is a single dict, not an array
    # return an array with 1 element
    d = dict()
    d[resp[key]] = resp
    return d


def _handle_get_configuration_not_found_errors(resp):
    # Solace Cloud can return:
    # "error": {
    #   "code": 6,
    #   "description": "Problem with tlsCipherSuiteList: Could not retrieve information from management-plane: not found",
    #   "status": "NOT_FOUND"
    # },
    error = resp['error']
    code = error['code']
    description = error['description']
    if code == 6 and description.find("Problem with tlsCipherSuiteList") >= 0:
        return False, resp
    return True, dict()


def get_configuration(solace_config, path_array, key):
    ok, resp = make_get_request(solace_config, path_array)
    if ok:
        return True, _build_config_dict(resp, key)
    elif is_broker_solace_cloud(solace_config):
        # check if status code was 404: not found
        # returned by Solace Cloud API
        if (type(resp) is not dict and resp.status_code == 404):
            return True, dict()
    else:
        # response contains 1 dict if lookup_item/key is found
        # if lookup_item is not found, response http-code: 400 with extra info in meta.error
        # check if responseCode=400 and error.code=6 ==> not found
        if (type(resp) is dict
                and 'responseCode' in resp.keys()
                and resp['responseCode'] == 400
                and 'error' in resp.keys()
                and 'code' in resp['error'].keys()
                and resp['error']['code'] == 6):
            return _handle_get_configuration_not_found_errors(resp)

    return False, resp


# request/response handling

def _wait_solace_cloud_request_completed(solace_config, request_resp):
    # GET https://api.solace.cloud/api/v0/services/{paste-your-serviceId-here}/requests/{{requestId}}
    request_resp_body = json.loads(request_resp.text)
    request_id = request_resp_body['data']['id']
    path_array = [SOLACE_CLOUD_API_SERVICES_BASE_PATH, solace_config.solace_cloud_config['service_id'], 'requests', request_id]
    url = compose_path(path_array)
    auth = BearerAuth(solace_config.solace_cloud_config['api_token'])
    is_completed = False
    try_count = 0
    retries = 12
    delay = 5  # seconds

    while not is_completed and try_count < retries:
        try:
            resp = requests.get(
                        url,
                        json=None,
                        auth=auth,
                        timeout=solace_config.vmr_timeout,
                        headers={'x-broker-name': solace_config.x_broker},
                        params=None
            )
            if sc.ENABLE_LOGGING:
                sc.log_http_roundtrip(resp)
            if resp.status_code != 200:
                return False, resp
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise AnsibleError("Solace Cloud: GET request status error: {}".format(str(e)))

        if resp.text:
            resp_body = json.loads(resp.text)
            is_completed = (resp_body['data']['adminProgress'] == 'completed')
            if is_completed:
                return True, resp_body
            else:
                ok, err = scu.parse_resp_body_for_errs(resp_body)
                if not ok:
                    return False, err
        else:
            raise AnsibleError("Solace Cloud: GET request status error: no body found in response")
        try_count += 1
        time.sleep(delay)
    # never gets here
    return True, None


def _parse_response(solace_config, resp):
    if sc.ENABLE_LOGGING:
        sc.log_http_roundtrip(resp)
    # Solace Cloud API returns 202: accepted if long running request
    if resp.status_code == 202 and is_broker_solace_cloud(solace_config):
        return _wait_solace_cloud_request_completed(solace_config, resp)
    elif resp.status_code != 200:
        return False, parse_bad_response(resp)
    return True, parse_good_response(resp)


def parse_good_response(resp):
    j = resp.json()
    if 'data' in j.keys():
        return j['data']
    return dict()


HTTP_CODE_REASON = dict(
    _401="Unauthorized",
    _404="Not Found"
)


def _get_reason(status_code):
    return HTTP_CODE_REASON.get("_" + str(status_code))


def _create_hint_bad_response(meta):
    # accessing solace cloud service using SEMPv2 API not allowed:
    # error.code == 89
    if 'error' in meta and 'code' in meta['error']:
        if meta['error']['code'] == 89:
            meta['hint'] = [
                "This might be a Solace Cloud service.",
                "If so, check the module's documentation on how to provide Solace Cloud parameters:",
                "ansible-doc <module-name>"
            ]
    return meta


def parse_bad_response(resp):
    if not resp.text:
        return resp
    j = resp.json()
    if 'meta' in j.keys() and \
            'error' in j['meta'].keys() and \
            'description' in j['meta']['error'].keys():
        # return j['meta']['error']['description']
        # we want to see the full message, including the code & request
        return _create_hint_bad_response(j['meta'])
    return dict(status_code=resp.status_code,
                reason=_get_reason(resp.status_code),
                body=json.loads(resp.text)
                )


def compose_path(path_array):
    return sc.compose_path(path_array)


def compose_solace_cloud_body(operation, type, data):
    return {
        'operation': operation,
        type: data
    }


def is_broker_solace_cloud(solace_config):
    if solace_config.solace_cloud_config is None:
        return False
    return True


if not SU_HAS_IMPORT_ERROR:
    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r


def _make_request(func, solace_config, path_array, json=None):

    path = compose_path(path_array)

    try:
        if(is_broker_solace_cloud(solace_config)):
            url = path
            auth = BearerAuth(solace_config.solace_cloud_config['api_token'])
        else:
            url = solace_config.vmr_url + path
            auth = solace_config.vmr_auth

        return _parse_response(
            solace_config,
            func(
                url,
                json=json,
                auth=auth,
                timeout=solace_config.vmr_timeout,
                headers={'x-broker-name': solace_config.x_broker},
                params=None
            )
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logging.debug("Request Error: %s", str(e))
        return False, str(e)


def make_get_request(solace_config, path_array):
    return _make_request(requests.get, solace_config, path_array)


def make_post_request(solace_config, path_array, json=None):
    return _make_request(requests.post, solace_config, path_array, json)


def make_delete_request(solace_config, path_array, json=None):
    return _make_request(requests.delete, solace_config, path_array, json)


def make_patch_request(solace_config, path_array, json=None):
    return _make_request(requests.patch, solace_config, path_array, json)

###
# The End.
