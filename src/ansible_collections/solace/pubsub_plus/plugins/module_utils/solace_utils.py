# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError, SolaceFeatureNotSupportedError
from ansible.module_utils.basic import AnsibleModule
import json
import re
import copy
import ssl
from copy import deepcopy
import xml.etree.ElementTree as ET

SOLACE_UTILS_HAS_IMPORT_ERROR = False
SOLACE_UTILS_IMPORT_ERR_TRACEBACK = None
import traceback
try:
    import xmltodict
    import packaging
except ImportError:
    SOLACE_UTILS_HAS_IMPORT_ERROR = True
    SOLACE_UTILS_IMPORT_ERR_TRACEBACK = traceback.format_exc()


class SolaceUtils(object):

    @staticmethod
    def get_ssl_default_verify_paths():
        return ssl.get_default_verify_paths()

    @staticmethod
    def module_fail_on_import_error(module: AnsibleModule, is_error: bool, import_error_traceback: str = None):
        if is_error:
            if import_error_traceback is not None:
                exceptiondata = import_error_traceback.splitlines()
                exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
                module.fail_json(msg="Missing module: %s" % exceptionarray[0], rc=solace_sys._SC_SYSTEM_ERR_RC, exception=import_error_traceback)
            else:
                module.fail_json(msg="Missing module: unknown", rc=solace_sys._SC_SYSTEM_ERR_RC)
        return

    @staticmethod
    def create_result(rc=0, changed=False) -> dict:
        result = dict(
            changed=changed,
            rc=rc
        )
        return result

    @staticmethod
    def get_key(d: dict, k: str):
        try:
            return d[k]
        except KeyError as e:
            raise SolaceInternalError(f"KeyError: dict has no key '{k}'") from e

    @staticmethod
    def type_conversion(d, is_solace_cloud):
        # solace cloud: cast everything to string
        # broker: cast strings to ints & floats, string booleans to boolean
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
                    d[k] = SolaceUtils.type_conversion(i, is_solace_cloud)
        return d

    @staticmethod
    def deep_dict_convert_strs_to_types(d: dict):
        for k, i in d.items():
            t = type(i)
            if t == str:
                if i.lower() in ['true', 'yes']:
                    d[k] = True
                elif i.lower() in ['false', 'no']:
                    d[k] = False
                elif re.search(r'^[0-9]+$', i):
                    d[k] = int(i)
                elif re.search(r'^[0-9]+\.[0-9]$', i):
                    d[k] = float(i)
            elif t == dict:
                d[k] = SolaceUtils.deep_dict_convert_strs_to_types(i)
        return d

    @staticmethod
    def deep_dict_diff(new: dict, old: dict, changes: dict = dict()):
        for k in new.keys():
            if not isinstance(new[k], dict):
                _old = old.get(k, None) if hasattr(old, 'get') else old
                # BEFORE: (DELETE_ME)
                # if new[k] != old.get(k, None):
                if new[k] != _old:
                    changes[k] = new[k]
            else:
                # changes[k] = dict()
                if k in old:
                    c = SolaceUtils.deep_dict_diff(new[k], old[k], dict())
                    # logging.debug("\n\nc=\n{}\n\n".format(json.dumps(c, indent=2)))
                    if c:
                        # logging.debug("\n\nc not empty: c=\n{}\n\n".format(json.dumps(c, indent=2)))
                        changes[k] = c
                        # changes[k].update(c)
                else:
                    changes[k] = copy.deepcopy(new[k])
        # logging.debug("\n\nreturning changes =\n{}\n\n".format(json.dumps(changes, indent=2)))
        return changes

    @staticmethod
    def parse_response_text(resp_text: str):
        resp_body = None
        if resp_text:
            try:
                resp_body = json.loads(resp_text)
            except json.JSONDecodeError:
                try:
                    resp_body = xmltodict.parse(resp_text)
                except Exception:
                    resp_body = resp_text
        return resp_body

    @staticmethod
    def merge_dicts_recursive(one: dict, two: dict) -> dict:
        merged = {}
        overlapping_keys = one.keys() & two.keys()
        for key in overlapping_keys:
            merged[key] = SolaceUtils.merge_dicts_recursive(one[key], two[key])
        for key in one.keys() - overlapping_keys:
            merged[key] = deepcopy(one[key])
        for key in two.keys() - overlapping_keys:
            merged[key] = deepcopy(two[key])
        return merged

    @staticmethod
    def convertDict2XmlElem(tag: str, d: dict) -> ET.Element:
        elem = ET.Element(tag)
        for key, val in d.items():
            if isinstance(val, dict):
                child = SolaceUtils.convertDict2XmlElem(key, val)
            elif isinstance(val, list):
                raise SolaceFeatureNotSupportedError('arrays/list handling')
            else:
                child = ET.Element(key)
                if str(val) != 'None':
                    child.text = str(val)
            elem.append(child)
        return elem

    @staticmethod
    def stringContainsAnyChars(str: str, set: str) -> bool:
        return 1 in [c in str for c in set]

    @staticmethod
    def create_version(s: str):
        try:
            v = packaging.version.Version(s)
        except packaging.version.InvalidVersion as e:
            raise SolaceInternalError(f"version parsing failed: {s}") from e
        return v
