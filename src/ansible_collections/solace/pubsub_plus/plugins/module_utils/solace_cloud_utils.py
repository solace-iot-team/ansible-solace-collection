#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

"""Collection of utility classes and functions to aid the solace_cloud_* modules."""

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
if not sc.HAS_IMPORT_ERROR:
    import logging
    import json
    import requests

""" Solace Cloud resources """
SOLACE_CLOUD_API_BASE_PATH = "https://api.solace.cloud/api/v0"
SOLACE_CLOUD_API_DATA_CENTERS = SOLACE_CLOUD_API_BASE_PATH + "/datacenters"
SOLACE_CLOUD_API_SERVICES_BASE_PATH = SOLACE_CLOUD_API_BASE_PATH + "/services"
""" Default Whitelist Keys """
DEFAULT_WHITELIST_KEYS = []  # Solace Cloud returns everything, including passwords


class SolaceCloudConfig(object):
    def __init__(self,
                 api_token,
                 timeout):
        self.auth = sc.BearerAuth(api_token)
        self.timeout = float(timeout)
        return


class SolaceCloudTask:

    WHITELIST_KEYS = []
    REQUIRED_TOGETHER_KEYS = dict()

    def __init__(self, module):
        sc.module_fail_on_import_error(module, sc.HAS_IMPORT_ERROR, sc.IMPORT_ERR_TRACEBACK)
        self.module = module
        self.sc_config = SolaceCloudConfig(
            api_token=self.module.params['api_token'],
            timeout=self.module.params['timeout']
        )
        return

    def do_task(self):

        result = dict(
            changed=False,
            rc=0,
            response=dict()
        )
        settings = self.module.params['settings']
        if settings:
            settings = sc.type_conversion(settings, True)

        ok, resp = self.get_func(self.sc_config, *self.crud_args())
        if not ok:
            result['rc'] = 1
            self.module.fail_json(msg=resp, **result)

        current_configuration = resp
        # whitelist of configuration items that are not returned by GET
        whitelist = DEFAULT_WHITELIST_KEYS
        whitelist.extend(self.get_whitelist_keys())
        # keys that must come together
        required_together_keys_list = self.get_required_together_keys()

        if current_configuration is not None:
            if self.module.params['state'] == 'absent':
                if not self.module.check_mode:
                    ok, resp = self.delete_func(self.sc_config, *self.crud_args())
                    if not ok:
                        result['rc'] = 1
                        self.module.fail_json(msg=resp, **result)
                    else:
                        result['response'] = resp
                result['changed'] = True
            else:
                # state=present
                if settings and len(settings.keys()):
                    # compare new settings against configuration
                    current_settings = current_configuration
                    bad_keys = [key for key in settings if key not in current_settings.keys()]
                    # remove whitelist items from bad_keys
                    bad_keys = [item for item in bad_keys if item not in whitelist]
                    # removed keys
                    removed_keys = [item for item in settings if item in whitelist]
                    # fail if any unexpected settings found
                    if len(bad_keys):
                        msg = "invalid key(s) found in 'settings'"
                        result['rc'] = 1
                        result['response'] = dict(
                            invalid_keys=', '.join(bad_keys),
                            hint=[
                                    "possible causes:",
                                    "- wrong spelling or wrong key: check the Solace Cloud API reference documentation",
                                    "- module's 'whitelist' isn't up to date: pls raise an issue"
                                ],
                            valid_keys=list(current_settings) + removed_keys
                        )
                        self.module.fail_json(msg=msg, **result)
                    # changed keys are those that exist in settings and don't match current settings

                    # does not do a deep comparison and returns wrong results for nested dicts
                    # changed_keys = [x for x in settings if x in current_settings.keys()
                    #                 and settings[x] != current_settings[x]]
                    # # logging.debug("\n\n\nchanged_keys=\n%s\n\n\n", str(changed_keys))

                    # walk recursively through the dict
                    changed_settings = sc.do_deep_compare(settings, current_settings)
                    # logging.debug("\n\n\nchanged_settings=\n%s", json.dumps(changed_settings, indent=2))
                    changed_keys = [*changed_settings]
                    # logging.debug("changed_keys=\n%s\n\n\n", str(changed_keys))

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
                        # original
                        # delta_settings = {key: settings[key] for key in changed_keys}
                        delta_settings = changed_settings
                        shallow_delta = {key: settings[key] for key in changed_keys if not isinstance(settings[key], dict)}
                        delta_settings.update(shallow_delta)
                        crud_args = self.crud_args()
                        crud_args.append(delta_settings)
                        result['delta'] = delta_settings
                        if not self.module.check_mode:
                            ok, resp = self.update_func(self.sc_config, *crud_args)
                            if not ok:
                                result['rc'] = 1
                                self.module.fail_json(msg=resp, **result)
                            else:
                                result['response'] = resp
                        result['changed'] = True
                    else:
                        result['response'] = current_configuration
                else:
                    result['response'] = current_configuration
        else:
            if self.module.params['state'] == 'present':
                if not self.module.check_mode:
                    crud_args = self.crud_args()
                    if settings:
                        crud_args.append(settings)
                    ok, resp = self.create_func(self.sc_config, *crud_args)
                    if ok:
                        result['response'] = resp
                    else:
                        result['rc'] = 1
                        self.module.fail_json(msg=resp, **result)
                result['changed'] = True

        return result

    def get_func(self, solace_config, *args):
        raise NotImplementedError("implementation missing in derived class")

    def create_func(self, solace_config, *args):
        raise NotImplementedError("implementation missing in derived class")

    def update_func(self, solace_config, *args):
        raise NotImplementedError("implementation missing in derived class")

    def delete_func(self, solace_config, *args):
        raise NotImplementedError("implementation missing in derived class")

    def lookup_item_kv(self):
        raise NotImplementedError("implementation missing in derived class")

    def get_args(self):
        return []

    def crud_args(self):
        return self.get_args() + self.lookup_item_kv()

    def get_whitelist_keys(self):
        whitelist = DEFAULT_WHITELIST_KEYS
        whitelist.extend(self.WHITELIST_KEYS)
        return whitelist

    def get_required_together_keys(self):
        return self.REQUIRED_TOGETHER_KEYS

###
# End Class SolaceCloudTask


# composable argument specs
def arg_spec_solace_cloud():
    return dict(
        api_token=dict(type='str', required=True, no_log=True),
        timeout=dict(type='int', default='60', required=False)
    )


def arg_spec_settings():
    return dict(
        settings=dict(type='dict', required=False)
    )


def arg_spec_state():
    return dict(
        state=dict(type='str', default='present', choices=['absent', 'present'])
    )


def _build_config_dict(resp, key):
    if not type(resp) is dict:
        raise TypeError("argument 'resp' is not a 'dict' but {}.".format(type(resp)))
    # wrong LOOKUP_ITEM_KEY in module
    if key not in resp:
        raise ValueError("wrong 'LOOKUP_ITEM_KEY' in module. semp GET response does not contain key='{}'".format(key))
    # resp is a single dict, not an array
    # return an array with 1 element
    d = dict()
    d[resp[key]] = resp
    return d

# request/response handling


def parse_resp_body_for_errs(resp_body):
    if resp_body['data'] and 'error' in resp_body['data']:
        return False, resp_body['data']
    return True, None


def _parse_response(solace_config, resp):
    if sc.ENABLE_LOGGING:
        sc.log_http_roundtrip(resp)
    # POST: https://api.solace.cloud/api/v0/services: returns 201
    if resp.status_code == 201:
        return True, _parse_good_response(resp)
    if resp.status_code != 200:
        return False, _parse_bad_response(resp)
    return True, _parse_good_response(resp)


def _parse_good_response(resp):
    if resp.text:
        j = resp.json()
        # return the array for GET calls if exists
        if 'data' in j.keys():
            return j['data']
    return dict()


def _parse_bad_response(resp):
    if not resp.text:
        return resp
    return dict(status_code=resp.status_code,
                body=json.loads(resp.text)
                )


def _make_request(func, solace_config, path_array, json=None):
    try:
        return _parse_response(
            solace_config,
            func(
                url=sc.compose_path(path_array),
                json=json,
                auth=solace_config.auth,
                timeout=solace_config.timeout,
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
