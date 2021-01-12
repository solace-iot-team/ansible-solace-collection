# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalErrorAbstractMethod, SolaceInternalError
import logging

SOLACE_TASK_CONFIG_HAS_IMPORT_ERROR = False
SOLACE_TASK_CONFIG_ERR_TRACEBACK = None
import traceback
try:
    import requests
except ImportError:
    SOLACE_TASK_CONFIG_HAS_IMPORT_ERROR = True
    SOLACE_TASK_CONFIG_ERR_TRACEBACK = traceback.format_exc()


if not SOLACE_TASK_CONFIG_HAS_IMPORT_ERROR:
    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r

class SolaceTaskConfig(object):    
    def __init__(self, module: AnsibleModule):
        self.module = module

    def get_params(self) -> list:
        return self.module.params

    def get_timeout(self) -> float:
        raise SolaceInternalErrorAbstractMethod()

    def get_headers(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    @staticmethod
    def arg_spec_state():
        return dict(
            state=dict(type='str', default='present', choices=['absent', 'present'])
        )

    @staticmethod
    def arg_spec_settings():
        return dict(
            settings=dict(type='dict', required=False)
        )


class SolaceTaskBrokerConfig(SolaceTaskConfig):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        is_secure=module.params['secure_connection']
        host=module.params['host']
        port=module.params['port']
        self.broker_url = ('https' if is_secure else 'http') + '://' + host + ':' + str(port)
        self.timeout = float(module.params['timeout'])
        self.x_broker = module.params.get('x_broker', None)
        self.sempv2_version=module.params.get('sempv2_version', None)

        solace_cloud_api_token = module.params.get('solace_cloud_api_token', None)
        solace_cloud_service_id = module.params.get('solace_cloud_service_id', None)
        # either both are provided or none
        ok = ((solace_cloud_api_token and solace_cloud_service_id)
              or (not solace_cloud_api_token and not solace_cloud_service_id))
        if not ok:
            result = SolaceUtils.create_result(rc=1)
            msg = f"must provide either both or none for Solace Cloud: solace_cloud_api_token={solace_cloud_api_token}, solace_cloud_service_id={solace_cloud_service_id}."
            module.fail_json(msg=msg, **result)
        if ok and solace_cloud_api_token and solace_cloud_service_id:
            self.solace_cloud_config = dict(
                api_token=solace_cloud_api_token,
                service_id=solace_cloud_service_id
            )
        else:
            self.solace_cloud_config = None

        self.solace_cloud_auth = None    
        if self.solace_cloud_config is not None:
            self.solace_cloud_auth = BearerAuth(self.solace_cloud_config['api_token'])
        self.semp_auth = (module.params['username'], module.params['password'])
        return
    
    def set_sempv2_version(self, sempv2_version: str):
        self.sempv2_version = sempv2_version

    def is_solace_cloud(self) -> bool:
        return (self.solace_cloud_config is not None)

    def get_semp_url(self, path: str) -> str:
        return self.broker_url + path
    
    def get_solace_cloud_url(self, path: str) -> str:
        return path

    def get_semp_auth(self) -> str:
        return self.semp_auth

    def get_solace_cloud_auth(self) -> str:
        if not self.is_solace_cloud:
            raise SolaceInternalError("config does not contain solace cloud parameters")
        return self.solace_cloud_auth

    def get_timeout(self) -> float:
        return self.timeout

    def get_headers(self) -> dict:
        return {'x-broker-name': self.x_broker}

    @staticmethod
    def arg_spec_broker_config() -> dict:
        return dict(
            host=dict(type='str', default='localhost'),
            port=dict(type='int', default=8080),
            secure_connection=dict(type='bool', default=False),
            username=dict(type='str', default='admin'),
            password=dict(type='str', default='admin', no_log=True),
            timeout=dict(type='int', default='10', required=False),
            x_broker=dict(type='str', default=None),
            sempv2_version=dict(type='str', required=False, default=None, aliases=['semp_version'])
        )

    @staticmethod
    def arg_spec_solace_cloud() -> dict:
        return dict(
            solace_cloud_api_token=dict(type='str', required=False, no_log=True, default=None),
            solace_cloud_service_id=dict(type='str', required=False, default=None)
        )

    @staticmethod
    def arg_spec_vpn() -> dict:
        return dict(
            msg_vpn=dict(type='str', required=True)
        )

    @staticmethod
    def arg_spec_name():
        return dict(
            name=dict(type='str', required=True)
        )
    
    @staticmethod
    def arg_spec_crud():
        arg_spec = SolaceTaskBrokerConfig.arg_spec_name()
        arg_spec.update(SolaceTaskBrokerConfig.arg_spec_settings())
        arg_spec.update(SolaceTaskBrokerConfig.arg_spec_state())
        return arg_spec

    @staticmethod
    def arg_spec_get_object_list_config_montor():
        return dict(
            api=dict(type='str', default='config', choices=['config', 'monitor']),
            query_params=dict(
                type='dict',
                required=False,
                options=dict(
                    select=dict(type='list', default=[], elements='str'),
                    where=dict(type='list', default=[], elements='str')
                )
            )
        )

    @staticmethod
    def arg_spec_get_object_list_monitor():
        return dict(
            query_params=dict(
                type='dict',
                required=False,
                options=dict(
                    select=dict(type='list', default=[], elements='str'),
                    where=dict(type='list', default=[], elements='str')
                )
            )
        )


class SolaceTaskSolaceCloudConfig(SolaceTaskConfig):

    PARAM_API_TOKEN = 'solace_cloud_api_token'

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.solace_cloud_api_token = module.params[self.PARAM_API_TOKEN]
        self.timeout = float(module.params['timeout'])
        self.auth = BearerAuth(self.solace_cloud_api_token)

    def is_solace_cloud(self) -> bool:
        return True

    def get_solace_cloud_url(self, path: str) -> str:
        return path

    def get_solace_cloud_auth(self) -> str:
        return self.auth
    
    def get_timeout(self) -> float:
        return self.timeout

    def get_headers(self) -> dict:
        return dict()

    @staticmethod
    def arg_spec_solace_cloud() -> dict:
        return dict(
            solace_cloud_api_token=dict(type='str', required=True, no_log=True, default=None, aliases=['api_token']),
            timeout=dict(type='int', default='60', required=False)
        )


class SolaceTaskSolaceCloudServiceConfig(SolaceTaskSolaceCloudConfig):
    
    PARAM_SERVICE_ID = 'solace_cloud_service_id'

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.solace_cloud_service_id = module.params.get(self.PARAM_SERVICE_ID, None)

    @staticmethod
    def arg_spec_solace_cloud_service() -> dict:
        return dict(
            solace_cloud_service_id=dict(type='str', required=False, default=None, aliases=['service_id'])
        )

