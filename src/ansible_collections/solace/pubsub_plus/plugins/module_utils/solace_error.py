# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class SolaceInternalError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def to_list(self):
        if isinstance(self.message, list):
            return self.message
        return [str(self.message)]


class SolaceInternalErrorAbstractMethod(SolaceInternalError):
    def __init__(self):
        self.message = "abstract method - must implement in derived class"
        super().__init__(self.message)


class SolaceApiError(Exception):
    def __init__(self, http_resp, resp, module_name, module_op):
        self.http_resp = http_resp
        self.resp = resp
        self.module_name = module_name
        self.module_op = module_op

    def get_ansible_msg(self):
        return self.resp

    def get_resp(self):
        return self.resp

    def get_http_resp(self):
        return self.http_resp

    def get_module_name(self):
        return self.module_name

    def get_module_op(self):
        return self.module_op

    def is_broker_error(self):
        if not self.resp or not isinstance(self.resp, dict):
            return False
        try:
            _meta = self.resp['body']['meta']
            return True
        except KeyError:
            return False

    def get_sempv2_error_code(self):
        if not self.resp or not isinstance(self.resp, dict):
            return None
        try:
            sempv2_error_code = self.resp['body']['meta']['error']['code']
            return sempv2_error_code
        except KeyError:
            return None

    def get_solace_cloud_error_code(self):
        if not self.resp or not isinstance(self.resp, dict):
            return None
        try:
            solace_cloud_error_code = self.resp['body']['subCode']
            return solace_cloud_error_code
        except KeyError:
            return None


class SolaceParamsValidationError(Exception):
    def __init__(self, param, value, msg):
        super().__init__(f"arg '{param}={value}': {msg}")


class SolaceEnvVarError(Exception):
    def __init__(self, name, value, msg):
        super().__init__(f"invalid env var: '{name}={value}'. {msg}.")


class SolaceFeatureNotSupportedError(Exception):
    def __init__(self, feature):
        super().__init__(f"feature: '{feature}")


class SolaceNoModuleSupportForSolaceCloudError(Exception):
    def __init__(self, module_name):
        super().__init__(f"module '{module_name}'")


class SolaceNoModuleStateSupportError(Exception):
    def __init__(self, module_name, state, broker_type, msg=None):
        super().__init__()
        self.module_name = module_name
        self.state = state
        self.broker_type = broker_type
        self.msg = msg


class SolaceModuleUsageError(Exception):
    def __init__(self, module_name, state, msg=None):
        super().__init__()
        self.module_name = module_name
        self.state = state
        self.msg = msg


class SolaceCloudApiError(Exception):
    def __init__(self, module_name, msg=None):
        super().__init__()
        self.module_name = module_name
        self.msg = msg


class SolaceModuleDeprecatedError(Exception):
    def __init__(self, module_name, msg):
        super().__init__(f"module '{module_name}': {msg}")
        self.module_name = module_name
        self.msg = msg


class SolaceSempv1VersionNotSupportedError(Exception):
    def __init__(self, module_name, sempv1_version_float, min_sempv1_version_float):
        super().__init__(
            f"module '{module_name}': service SEMP V1 version: {sempv1_version_float}; minimum version required: {min_sempv1_version_float}")


class SolaceMinSempv2VersionSupportedError(Exception):
    def __init__(self, module_name, actual_sempv2_version, min_sempv2_version):
        super().__init__(
            f"module '{module_name}': service SEMP V2 version: {actual_sempv2_version}; minimum version required: {min_sempv2_version}")


class SolaceMaxSempv2VersionSupportedError(Exception):
    def __init__(self, module_name, actual_sempv2_version, max_sempv2_version):
        super().__init__(
            f"module '{module_name}': service SEMP V2 version: {actual_sempv2_version}; max version supported: {max_sempv2_version}")


class SolaceCloudApiResponseDataError(Exception):
    def __init__(self, module_name, msg, details):
        super().__init__(f"module '{module_name}': {msg}")
        self.module_name = module_name
        self.msg = msg
        self.details = details

    def to_list(self):
        if isinstance(self.msg, list):
            return self.msg
        return [str(self.msg)]


class SolaceError(Exception):
    def __init__(self, message, result_update: dict = None):
        self.message = message
        self.result_update = result_update
        super().__init__(self.message)

    def to_list(self):
        if isinstance(self.message, list):
            return self.message
        return [str(self.message)]

    def get_result_update(self):
        return self.result_update
