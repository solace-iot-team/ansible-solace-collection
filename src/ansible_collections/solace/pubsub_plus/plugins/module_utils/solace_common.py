#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

"""Common functions."""

HAS_IMPORT_ERROR = False
IMPORT_ERR_TRACEBACK = None
import traceback
try:
    import re  
    import logging
    import json
    import os
    import sys
    from distutils.util import strtobool
    import copy
    from json.decoder import JSONDecodeError
    import requests
    import xmltodict
    import urllib.parse
    from ansible.errors import AnsibleError
except ImportError:
    HAS_IMPORT_ERROR = True
    IMPORT_ERR_TRACEBACK = traceback.format_exc()

_SC_SYSTEM_ERR_RC = -1
# check python version
_PY3_MIN = sys.version_info[:2] >= (3, 6)
if not _PY3_MIN:
    print(
        '\n{"failed": true, "rc": %d, "msg_hint": "Set ANSIBLE_PYTHON_INTERPRETER=path-to-python-3", '
        '"msg": "solace.pubsub_plus requires a minimum of Python3 version 3.6. Current version: %s."}' % (_SC_SYSTEM_ERR_RC, ''.join(sys.version.splitlines()))
    )
    sys.exit(1)

def module_fail_on_import_error(module, is_error, import_error_traceback=None):
    if is_error:
        if import_error_traceback is not None:
            exceptiondata = import_error_traceback.splitlines()
            exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
            module.fail_json(msg="Missing module: %s" % exceptionarray[0], rc=_SC_SYSTEM_ERR_RC, exception=import_error_traceback)
        else:
            module.fail_json(msg="Missing module: unknown", rc=_SC_SYSTEM_ERR_RC)
    return

################################################################################################
# initialize logging

ENABLE_LOGGING = False  # False to disable
enableLoggingEnvVal = os.getenv('ANSIBLE_SOLACE_ENABLE_LOGGING')
loggingPathEnvVal = os.getenv('ANSIBLE_SOLACE_LOG_PATH')
if enableLoggingEnvVal is not None and enableLoggingEnvVal != '':
    try:
        ENABLE_LOGGING = bool(strtobool(enableLoggingEnvVal))
    except ValueError:
        raise ValueError("failed: invalid value for env var: 'ANSIBLE_SOLACE_ENABLE_LOGGING={}'. use 'true' or 'false' instead.".format(enableLoggingEnvVal))

if ENABLE_LOGGING:
    logFile = './ansible-solace.log'
    if loggingPathEnvVal is not None and loggingPathEnvVal != '':
        logFile = loggingPathEnvVal
    logging.basicConfig(filename=logFile,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s(): %(message)s')
    logging.info('Module start #############################################################################################')

################################################################################################


def log_http_roundtrip(resp):
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
        except JSONDecodeError:
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
            'headers': dict(resp.request.headers),
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


if not HAS_IMPORT_ERROR:
    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r

# solace cloud: cast everything to string
# broker: cast strings to ints & floats, string booleans to boolean
def type_conversion(d, is_solace_cloud):
    for k, i in d.items():
        t = type(i)
        if is_solace_cloud:
            if t == int or t == float:
                d[k] = str(i)
            elif t == bool:
                d[k] = str(i).lower()
        else:
            if (t == str) and re.search(r'^[0-9]+$', i):
                d[k] = int(i)
            elif (t == str) and re.search(r'^[0-9]+\.[0-9]$', i):
                d[k] = float(i)
            elif t == dict:
                d[k] = type_conversion(i, is_solace_cloud)
    return d


def merge_dicts(*argv):
    data = dict()
    for arg in argv:
        if arg:
            data.update(arg)
    return data


def compose_path(path_array):
    if not type(path_array) is list:
        raise TypeError("argument 'path_array' is not an array but {}".format(type(path_array)))
    # ensure elements are 'url encoded'
    # except first one: SEMP_V2_CONFIG or SOLACE_CLOUD_API_SERVICES_BASE_PATH
    paths = []
    for i, path_elem in enumerate(path_array):
        if path_elem == '':
            raise ValueError("path_elem='{}' is empty in path_array='{}'.".format(path_elem, str(path_array)))
        if i > 0:
            # deals with wildcards in topic strings
            # e.g. for MQTT subscriptions: '#' and '+'
            new_path_elem = urllib.parse.quote_plus(path_elem, safe=',')
            paths.append(new_path_elem)
        else:
            paths.append(path_elem)
    return '/'.join(paths)


def do_deep_compare(new, old, changes=dict()):
    for k in new.keys():
        if not isinstance(new[k], dict):
            if new[k] != old.get(k, None):
                changes[k] = new[k]
        else:
            # changes[k] = dict()
            if k in old:
                c = do_deep_compare(new[k], old[k], dict())
                # logging.debug("\n\nc=\n{}\n\n".format(json.dumps(c, indent=2)))
                if c:
                    # logging.debug("\n\nc not empty: c=\n{}\n\n".format(json.dumps(c, indent=2)))
                    changes[k] = c
                    # changes[k].update(c)
            else:
                changes[k] = copy.deepcopy(new[k])
    # logging.debug("\n\nreturning changes =\n{}\n\n".format(json.dumps(changes, indent=2)))
    return changes


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
    if ENABLE_LOGGING:
        log_http_roundtrip(resp)
    if resp.status_code != 200:
        raise AnsibleError("SEMP v1 call not successful. Pls check the log and raise an issue.")
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


def execute_sempv1_get_list(solace_config, xml_dict, list_path_array):

    if not isinstance(xml_dict, dict):
        raise TypeError("argument 'xml_dict' is not a dict, but {}".format(type(xml_dict)))
    if not isinstance(list_path_array, list):
        raise TypeError("argument 'list_path_array' is not a list, but {}".format(type(list_path_array)))

    xml_data = xmltodict.unparse(xml_dict)

    result_list = []

    hasNextPage = True

    while hasNextPage:

        try:
            ok, semp_resp = make_sempv1_post_request(solace_config, xml_data)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            return False, str(e)

        if not ok:
            resp = dict(request=xml_data, response=semp_resp)
            return False, resp

        # get the list
        _d = semp_resp
        for path in list_path_array:
            if _d and path in _d:
                _d = _d[path]
            else:
                # empty list / not found
                return True, []
        if isinstance(_d, dict):
            resp = [_d]
        elif isinstance(_d, list):
            resp = _d
        else:
            raise ValueError("unknown SEMP v1 return type: {}".format(type(_d)))

        result_list.extend(resp)

        # see if there is more
        more_cookie = None
        if 'more-cookie' in semp_resp['rpc-reply']:
            more_cookie = semp_resp['rpc-reply']['more-cookie']
        if more_cookie:
            xml_data = xmltodict.unparse(more_cookie)
            hasNextPage = True
        else:
            hasNextPage = False

    return True, result_list


###
# The End.
