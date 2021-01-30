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
    def __init__(self, resp):
        self.resp = resp

    def get_ansible_msg(self):
        return self.resp

    def get_resp(self):
        return self.resp


class SolaceParamsValidationError(Exception):
    def __init__(self, param, value, msg):
        super().__init__(f"arg '{param}={value}': {msg}")


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
