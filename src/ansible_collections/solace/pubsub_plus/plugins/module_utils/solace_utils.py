# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError
from ansible.module_utils.basic import AnsibleModule
import urllib.parse
import json
import logging
import re


SOLACE_UTILS_HAS_IMPORT_ERROR = False
SOLACE_UTILS_IMPORT_ERR_TRACEBACK = None
import traceback
try:
    import xmltodict
except ImportError:
    SOLACE_UTILS_HAS_IMPORT_ERROR = True
    SOLACE_UTILS_IMPORT_ERR_TRACEBACK = traceback.format_exc()

class SolaceUtils(object):

    @staticmethod
    def module_fail_on_import_error(module: AnsibleModule, is_error: bool, import_error_traceback: str=None):
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
        except KeyError:
            raise SolaceInternalError(f"KeyError: dict has no key '{k}'")
    
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