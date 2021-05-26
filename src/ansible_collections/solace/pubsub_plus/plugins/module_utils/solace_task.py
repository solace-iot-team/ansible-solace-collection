# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalError, SolaceInternalErrorAbstractMethod, SolaceApiError, SolaceModuleUsageError, SolaceParamsValidationError, SolaceError, SolaceFeatureNotSupportedError, SolaceSempv1VersionNotSupportedError, SolaceNoModuleSupportForSolaceCloudError, SolaceNoModuleStateSupportError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskConfig, SolaceTaskBrokerConfig, SolaceTaskSolaceCloudServiceConfig, SolaceTaskSolaceCloudConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceCloudApi, SolaceSempV2PagingGetApi
from ansible.module_utils.basic import AnsibleModule
import logging
import json

SOLACE_TASK_HAS_IMPORT_ERROR = False
SOLACE_TASK_ERR_TRACEBACK = None
import traceback
try:
    import requests
    import certifi
except ImportError:
    SOLACE_TASK_HAS_IMPORT_ERROR = True
    SOLACE_TASK_ERR_TRACEBACK = traceback.format_exc()

if not SOLACE_TASK_HAS_IMPORT_ERROR:
    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r


class SolaceTask(object):
    def __init__(self, module: AnsibleModule):
        SolaceUtils.module_fail_on_import_error(module, SOLACE_TASK_HAS_IMPORT_ERROR, SOLACE_TASK_ERR_TRACEBACK)
        self.module = module
        self.changed = False
        self.result = SolaceUtils.create_result()
        self.current_operation = 'this-is-the-current-operation'
        return

    def get_module(self) -> AnsibleModule:
        return self.module

    def get_settings_arg_name(self) -> str:
        raise SolaceInternalErrorAbstractMethod()

    def get_config(self) -> SolaceTaskConfig:
        raise SolaceInternalErrorAbstractMethod()

    def get_result(self) -> dict:
        return self.result

    def set_result(self, result):
        self.result = result

    def update_result(self, update):
        self.result.update(update)

    def create_result(self, rc=0, changed=False) -> dict:
        return SolaceUtils.create_result(rc, changed)

    def validate_params(self):
        return

    def do_task(self):
        # return: msg(dict) and result(dict)
        raise SolaceInternalErrorAbstractMethod()

    def _logException(self, logging_func, message, e) -> list:
        ex = traceback.format_exc()
        ex_msg_list = [str(e)]
        log_msg = [f"{message}"] + ex_msg_list + ex.split('\n')
        logging_func("%s", json.dumps(log_msg, indent=2))

    def logExceptionAsError(self, message, e) -> list:
        self._logException(logging.error, message, e)

    def logExceptionAsDebug(self, message, e) -> list:
        self._logException(logging.debug, message, e)

    def execute(self):
        try:
            config = self.get_config()
            if config:
                config.validate_params()
            msg, result = self.do_task()
            self.module.exit_json(msg=msg, **result)
        except SolaceError as e:
            self.logExceptionAsError(type(e), e)
            self.update_result(dict(rc=1, changed=self.changed))
            result_update = e.get_result_update()
            if result_update:
                self.update_result(result_update)
            self.module.exit_json(msg=e.to_list(), **self.get_result())
        except SolaceApiError as e:
            self.logExceptionAsError(type(e), e)
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=e.get_ansible_msg(), **self.get_result())
        except SolaceInternalError as e:
            self.logExceptionAsError(type(e), e)
            ex = traceback.format_exc()
            ex_msg_list = e.to_list()
            usr_msg = ["Pls raise an issue including the full traceback. (hint: use -vvv)"] + ex_msg_list + ex.split('\n')
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except SolaceParamsValidationError as e:
            self.logExceptionAsError(type(e), e)
            usr_msg = ["module arg validation failed", str(e)]
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except SolaceFeatureNotSupportedError as e:
            self.logExceptionAsError(type(e), e)
            usr_msg = ["Feature currently not supported. Pls raise an new feature request if required.", str(e)]
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except SolaceNoModuleStateSupportError as e:
            usr_msg = [
                "combination not supported:",
                f" module: '{e.module_name}'",
                f" broker_type: '{e.broker_type}'",
                f" state: '{e.state}'"
            ]
            if e.msg:
                usr_msg.append(e.msg)
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except SolaceModuleUsageError as e:
            usr_msg = [
                "module usage error:",
                f" module: '{e.module_name}'",
                f" state: '{e.state}'"
            ]
            if e.msg:
                usr_msg.append(e.msg)
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except SolaceSempv1VersionNotSupportedError as e:
            self.logExceptionAsError(type(e), e)
            usr_msg = [str(e)]
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except SolaceNoModuleSupportForSolaceCloudError as e:
            self.logExceptionAsError(type(e), e)
            usr_msg = [str(e), "Solace Cloud not supported", "raise a feature request if required"]
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except (requests.exceptions.SSLError) as e:
            # these paths do not seem to work
            # logging.debug("ssl verify paths: %s", SolaceUtils.get_ssl_default_verify_paths())
            log_msg = [type(e)] + [f"certificate authority (CA) bundle used:{certifi.where()}"]
            self.logExceptionAsError(log_msg, e)
            self.update_result(dict(rc=1, changed=self.changed))
            usr_msg = ["Check SSL configuration & certificate required for host"] + \
                      [f"Certificate authority (CA) bundle used: {certifi.where()}"] + \
                      [str(e)]
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            self.logExceptionAsError(type(e), e)
            self.update_result(dict(rc=1, changed=self.changed))
            usr_msg = str(e)
            self.module.exit_json(msg=usr_msg, **self.get_result())
        except Exception as e:
            self.logExceptionAsError(type(e), e)
            ex = traceback.format_exc()
            ex_msg_list = [str(e)]
            usr_msg = ["Pls raise an issue including the full traceback. (hint: use -vvv)"] + ex_msg_list + ex.split('\n')
            self.update_result(dict(rc=1, changed=self.changed))
            self.module.exit_json(msg=usr_msg, **self.get_result())


class SolaceReadFactsTask(SolaceTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)

    def get_config(self):
        return None

    def validate_param_get_functions(self, valid_get_funcs: list, param_get_funcs: list) -> bool:
        if param_get_funcs and len(param_get_funcs) > 0:
            for get_func in param_get_funcs:
                exists = (True if get_func in valid_get_funcs else False)
                if not exists:
                    raise SolaceParamsValidationError("unknown get_function", get_func, f"valid get functions are: {valid_get_funcs}")
            return True
        return False

    def call_dynamic_func(self, func_name, *args):
        try:
            return getattr(self, func_name)(*args)
        except AttributeError as e:
            raise SolaceInternalError(f"function '{func_name}' not found") from e


class SolaceBrokerActionTask(SolaceTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config

    def get_args(self) -> list:
        raise SolaceInternalErrorAbstractMethod()


class SolaceCRUDTask(SolaceTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)

    def get_args(self) -> list:
        raise SolaceInternalErrorAbstractMethod()

    def get_new_settings(self) -> dict:
        s = self.get_module().params[self.get_settings_arg_name()]
        if s:
            SolaceUtils.type_conversion(s, self.get_config().is_solace_cloud())
        return s

    def normalize_current_settings(self, current_settings: dict, new_settings: dict) -> dict:
        return current_settings

    def get_func(self, *args) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def create_func(self, *args) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def update_func(self, *args) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def delete_func(self, *args) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def do_task_extension(self, args, new_state, new_settings, current_settings):
        raise SolaceInternalError(f"unhandled task-state combination, state={new_state}")

    def do_task(self):
        self.validate_params()
        args = self.get_args()
        new_settings = self.get_new_settings()
        _current_settings = self.get_func(*args)
        current_settings = self.normalize_current_settings(_current_settings, new_settings)
        new_state = self.get_module().params['state']
        # delete if exists
        if new_state == 'absent':
            if current_settings is None:
                return None, self.create_result(rc=0, changed=False)
            result = self.create_result(rc=0, changed=True)
            if not self.get_module().check_mode:
                result['response'] = self.delete_func(*args)
            return None, result
        # create if not exist
        if new_state == 'present' and current_settings is None:
            result = self.create_result(rc=0, changed=True)
            if not self.get_module().check_mode:
                args.append(new_settings)
                result['response'] = self.create_func(*args)
            return None, result
        # update if any changes
        if new_state == 'present' and current_settings is not None:
            update_settings = None
            if new_settings is not None:
                update_settings = SolaceUtils.deep_dict_diff(new_settings, current_settings)
            if not update_settings:
                result = self.create_result(rc=0, changed=False)
                result['response'] = current_settings
                return None, result
            if update_settings:
                result = self.create_result(rc=0, changed=True)
                if not self.get_module().check_mode:
                    # sending all settings to update ==> no missing together or required check necessary
                    args.append(new_settings)
                    args.append(update_settings)
                    result['response'] = self.update_func(*args)
            return None, result
        return self.do_task_extension(args, new_state, new_settings, current_settings)


class SolaceBrokerCRUDTask(SolaceCRUDTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)

    def get_settings_arg_name(self) -> str:
        return 'sempv2_settings'

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config


class SolaceCloudCRUDTask(SolaceCRUDTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.config = SolaceTaskSolaceCloudServiceConfig(module)

    def get_settings_arg_name(self) -> str:
        return 'solace_cloud_settings'

    def get_config(self) -> SolaceTaskSolaceCloudServiceConfig:
        return self.config


class SolaceGetTask(SolaceTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)

    def create_result_with_list(self, result_list: list, rc=0, changed=False) -> dict:
        result = super().create_result(rc, changed)
        result.update(dict(
            result_list=result_list,
            result_list_count=len(result_list)
        ))
        return result


class SolaceBrokerGetTask(SolaceGetTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config

    def get_settings_arg_name(self) -> str:
        return 'sempv2_settings'

    def get_sempv2_api(self) -> SolaceSempV2Api:
        return self.sempv2_api


class SolaceBrokerGetPagingTask(SolaceGetTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)
        self.sempv2_get_paging_api = SolaceSempV2PagingGetApi(module, self.is_supports_paging())

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config

    def is_supports_paging(self):
        return True

    def get_settings_arg_name(self) -> str:
        return 'sempv2_settings'

    def get_sempv2_get_paging_api(self) -> SolaceSempV2Api:
        return self.sempv2_get_paging_api

    def get_monitor_api_base(self) -> str:
        return SolaceSempV2Api.API_BASE_SEMPV2_MONITOR

    def get_path_array(self, params: dict) -> list:
        raise SolaceInternalErrorAbstractMethod()

    def do_task(self):
        params = self.get_config().get_params()
        api = params['api']
        query_params = params['query_params']
        objects = self.get_sempv2_get_paging_api().get_objects(self.get_config(), api, self.get_path_array(params), query_params, self.get_monitor_api_base)
        result = self.create_result_with_list(objects)
        return None, result


class SolaceCloudGetTask(SolaceGetTask):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.config = SolaceTaskSolaceCloudConfig(module)
        self.solace_cloud_api = SolaceCloudApi(module)

    def get_config(self) -> SolaceTaskSolaceCloudConfig:
        return self.config

    def get_settings_arg_name(self) -> str:
        return 'solace_cloud_settings'

    def get_solace_cloud_api(self) -> SolaceCloudApi:
        return self.solace_cloud_api
