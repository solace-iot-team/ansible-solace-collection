# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
import traceback
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalErrorAbstractMethod, SolaceInternalError, SolaceParamsValidationError
import urllib.parse

SOLACE_TASK_CONFIG_HAS_IMPORT_ERROR = False
SOLACE_TASK_CONFIG_ERR_TRACEBACK = None
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

    def get_module(self):
        return self.module

    def validate_params(self):
        pass

    def get_params(self) -> list:
        return self.module.params

    def get_timeout(self) -> float:
        raise SolaceInternalErrorAbstractMethod()

    def get_validate_certs(self) -> bool:
        raise SolaceInternalErrorAbstractMethod()

    def get_headers(self, op: str) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_reverse_proxy(self) -> dict:
        return None

    def get_reverse_proxy_query_params(self) -> dict:
        return None

    def get_reverse_proxy_headers(self, op: str) -> dict:
        return None

    @staticmethod
    def arg_spec_state():
        return dict(
            state=dict(
                type='str',
                default='present',
                choices=['absent', 'present'])
        )

    @staticmethod
    def arg_spec_state_crud_list():
        return dict(
            state=dict(
                type='str',
                default='present',
                choices=['absent', 'present', 'exactly'])
        )

    @ staticmethod
    def arg_spec_sempv2_settings():
        return dict(
            sempv2_settings=dict(
                type='dict', required=False, aliases=['settings'])
        )

    @ staticmethod
    def arg_spec_sempv1_settings():
        return dict(
            sempv1_settings=dict(type='dict', required=False)
        )

    @ staticmethod
    def arg_spec_solace_cloud_settings():
        return dict(
            solace_cloud_settings=dict(
                type='dict', required=False, aliases=['settings'])
        )


class SolaceTaskBrokerConfig(SolaceTaskConfig):
    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        is_secure = module.params['secure_connection']
        host = module.params['host']
        port = module.params['port']
        self.broker_url = ('https' if is_secure else 'http') + \
            '://' + host + ':' + str(port)
        self.timeout = float(module.params['timeout'])
        self.validate_certs = bool(module.params['validate_certs'])
        self.x_broker = module.params.get('x_broker', None)
        solace_cloud_api_token = module.params.get(
            'solace_cloud_api_token', None)
        solace_cloud_service_id = module.params.get(
            'solace_cloud_service_id', None)
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
            self.solace_cloud_auth = BearerAuth(
                self.solace_cloud_config['api_token'])

        self.semp_auth = (module.params['username'], module.params['password'])

        # reverse proxy
        self.reverse_proxy = module.params.get('reverse_proxy', None)
        if self.reverse_proxy:
            if self.solace_cloud_config:
                result = SolaceUtils.create_result(rc=1)
                msg = "No support for reverse proxy for Solace Cloud, remove 'reverse_proxy' from module arguments."
                module.fail_json(msg=msg, **result)
            semp_base_path = self.reverse_proxy.get('semp_base_path', None)
            if semp_base_path:
                self.broker_url += '/' + semp_base_path
            use_basic_auth = self.reverse_proxy.get('use_basic_auth', False)
            if not use_basic_auth:
                self.semp_auth = None
            _reverse_proxy_headers = self.reverse_proxy.get('headers', None)
            if _reverse_proxy_headers:
                _reverse_proxy_headers_include_x_asc_module = _reverse_proxy_headers.get(
                    'x-asc-module', False)
                if not isinstance(_reverse_proxy_headers_include_x_asc_module, bool):
                    result = SolaceUtils.create_result(rc=1)
                    msg = f"argument: 'reverse_proxy.headers.x-asc-module={_reverse_proxy_headers_include_x_asc_module}, is not of type 'bool'; use True/False or yes/no"
                    module.fail_json(msg=msg, **result)
                _reverse_proxy_headers_include_x_asc_module_op = _reverse_proxy_headers.get(
                    'x-asc-module-op', False)
                if not isinstance(_reverse_proxy_headers_include_x_asc_module_op, bool):
                    result = SolaceUtils.create_result(rc=1)
                    msg = f"argument: 'reverse_proxy.headers.x-asc-module-op={_reverse_proxy_headers_include_x_asc_module_op}, is not of type 'bool'; use True/False or yes/no"
                    module.fail_json(msg=msg, **result)
                self.reverse_proxy['headers']['x-asc-module'] = _reverse_proxy_headers_include_x_asc_module
                self.reverse_proxy['headers']['x-asc-module-op'] = _reverse_proxy_headers_include_x_asc_module_op
        return

    def is_solace_cloud(self) -> bool:
        return (self.solace_cloud_config is not None)

    def get_broker_netloc(self):
        parse_result = urllib.parse.urlparse(self.broker_url)
        return parse_result.netloc

    def get_broker_semp_base_path(self):
        if self.reverse_proxy:
            return self.reverse_proxy.get('semp_base_path', '')
        else:
            return ''

    def get_semp_url(self, path: str) -> str:
        return self.broker_url + path

    def get_reverse_proxy(self) -> dict:
        return self.reverse_proxy

    def get_reverse_proxy_query_params(self) -> dict:
        if self.reverse_proxy:
            return self.reverse_proxy.get('query_params', None)
        return None

    def get_reverse_proxy_headers(self, op: str) -> dict:
        if self.reverse_proxy:
            _headers = self.reverse_proxy.get('headers', None)
            if _headers:
                _headers['x-asc-module'] = self.module._name if _headers['x-asc-module'] else None
                _headers['x-asc-module-op'] = op if _headers['x-asc-module-op'] else None
            return _headers
        return None

    def get_solace_cloud_url(self, path: str) -> str:
        return path

    def get_semp_auth(self) -> str:
        return self.semp_auth

    def get_solace_cloud_auth(self) -> str:
        if not self.is_solace_cloud:
            raise SolaceInternalError(
                "config does not contain solace cloud parameters")
        return self.solace_cloud_auth

    def get_timeout(self) -> float:
        return self.timeout

    def get_validate_certs(self) -> bool:
        return self.validate_certs

    def get_headers(self, op) -> dict:
        _headers = {
            'x-broker-name': self.x_broker
        }
        _reverse_proxy_headers = self.get_reverse_proxy_headers(op)
        if _reverse_proxy_headers:
            _headers.update(_reverse_proxy_headers)
        return _headers

    @ staticmethod
    def arg_spec_broker_config() -> dict:
        return dict(
            host=dict(type='str', default='localhost'),
            port=dict(type='int', default=8080),
            secure_connection=dict(type='bool', default=False),
            validate_certs=dict(type='bool', default=True),
            username=dict(type='str', default='admin'),
            password=dict(type='str', default='admin', no_log=True),
            timeout=dict(type='int', default='10', required=False),
            x_broker=dict(type='str', default=None),
            reverse_proxy=dict(
                type='dict', required=False,
                options=dict(
                    semp_base_path=dict(
                        type='str', required=False, default=None),
                    use_basic_auth=dict(
                        type='bool', required=False, default=False),
                    query_params=dict(
                        type='dict', required=False, default=None),
                    headers=dict(type='dict', required=False, default=None)
                )
            )
        )

    @ staticmethod
    def arg_spec_solace_cloud() -> dict:
        return dict(
            solace_cloud_home=dict(type='str', required=False, default=None, choices=['us', 'au', 'US', 'AU', '']),
            solace_cloud_api_token=dict(
                type='str', required=False, no_log=True, default=None),
            solace_cloud_service_id=dict(
                type='str', required=False, default=None)
        )

    @ staticmethod
    def arg_spec_solace_cloud_mandatory() -> dict:
        return dict(
            solace_cloud_api_token=dict(type='str',
                                        required=True,
                                        no_log=True),
            solace_cloud_service_id=dict(type='str',
                                         required=True)
        )

    @ staticmethod
    def arg_spec_vpn() -> dict:
        return dict(
            msg_vpn=dict(type='str', required=True)
        )

    @ staticmethod
    def arg_spec_virtual_router():
        return dict(
            virtual_router=dict(type='str', default='primary',
                                choices=['primary', 'backup'])
        )

    @ staticmethod
    def arg_spec_name():
        return dict(
            name=dict(type='str', required=True)
        )

    @ staticmethod
    def arg_spec_names():
        return dict(
            names=dict(type='list',
                       required=True,
                       elements='str'
                       )
        )

    @ staticmethod
    def arg_spec_crud():
        arg_spec = SolaceTaskBrokerConfig.arg_spec_name()
        arg_spec.update(SolaceTaskBrokerConfig.arg_spec_sempv2_settings())
        arg_spec.update(SolaceTaskBrokerConfig.arg_spec_state())
        return arg_spec

    @ staticmethod
    def arg_spec_crud_list():
        arg_spec = SolaceTaskBrokerConfig.arg_spec_names()
        arg_spec.update(SolaceTaskBrokerConfig.arg_spec_sempv2_settings())
        arg_spec.update(SolaceTaskBrokerConfig.arg_spec_state_crud_list())
        return arg_spec

    @ staticmethod
    def _arg_spec_get_query_params():
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

    @ staticmethod
    def _arg_spec_get_object_list_page_count():
        return dict(
            page_count=dict(type='int', default=100, required=False)
        )

    @ staticmethod
    def arg_spec_get_object_list_config_montor():
        d = dict(
            api=dict(type='str', default='config',
                     choices=['config', 'monitor'])
        )
        d.update(SolaceTaskBrokerConfig._arg_spec_get_object_list_page_count())
        d.update(SolaceTaskBrokerConfig._arg_spec_get_query_params())
        return d

    @ staticmethod
    def arg_spec_get_object_list_monitor():
        d = dict(
            api=dict(type='str', default='monitor', choices=['monitor'])
        )
        d.update(SolaceTaskBrokerConfig._arg_spec_get_object_list_page_count())
        d.update(SolaceTaskBrokerConfig._arg_spec_get_query_params())
        return d


class SolaceTaskSolaceCloudConfig(SolaceTaskConfig):

    PARAM_API_TOKEN = 'solace_cloud_api_token'

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.solace_cloud_api_token = module.params[self.PARAM_API_TOKEN]
        self.timeout = float(module.params['timeout'])
        self.validate_certs = bool(module.params['validate_certs'])
        self.auth = BearerAuth(self.solace_cloud_api_token)
        self.solace_cloud_home = module.params['solace_cloud_home']

    def is_solace_cloud(self) -> bool:
        return True

    def get_solace_cloud_url(self, path: str) -> str:
        return path

    def get_solace_cloud_auth(self) -> str:
        return self.auth

    def get_timeout(self) -> float:
        return self.timeout

    def get_validate_certs(self) -> bool:
        return self.validate_certs

    def get_headers(self, op) -> dict:
        return {}

    @ staticmethod
    def arg_spec_solace_cloud() -> dict:
        return dict(
            solace_cloud_home=dict(type='str', required=False, default=None, choices=['us', 'au', 'US', 'AU', '']),
            solace_cloud_api_token=dict(
                type='str', required=True, no_log=True, aliases=['api_token']),
            timeout=dict(type='int', default='60', required=False),
            validate_certs=dict(type='bool', default=True)
        )


class SolaceTaskSolaceCloudServiceConfig(SolaceTaskSolaceCloudConfig):

    PARAM_SERVICE_ID = 'solace_cloud_service_id'

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.solace_cloud_service_id = module.params.get(
            self.PARAM_SERVICE_ID, None)

    @ staticmethod
    def arg_spec_solace_cloud_service_id() -> dict:
        return dict(
            solace_cloud_service_id=dict(
                type='str', required=False, default=None, aliases=['service_id'])
        )
