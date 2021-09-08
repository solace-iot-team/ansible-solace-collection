# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


class ModuleDocFragment(object):

    # Documentation fragments for Solace modules
    BROKER = r'''
---
notes:
- "Sempv2 Config Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/"
- "Sempv2 Monitor Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/"
- "Sempv2 Action Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/action/index.html#/"

options:
  host:
    description: Hostname of Solace Broker.
    required: false
    default: "localhost"
    type: str
  port:
    description: Management port of Solace Broker.
    required: false
    default: 8080
    type: int
  secure_connection:
    description: If true, use https rather than http.
    required: false
    default: false
    type: bool
  validate_certs:
    description: Flag to switch validation of client certificates on/off when using a secure connection.
    required: false
    default: true
    type: bool
  username:
    description: Administrator username for Solace Broker.
    required: false
    default: "admin"
    type: str
  password:
    description: Administrator password for Solace Broker.
    required: false
    default: "admin"
    type: str
  timeout:
    description: Connection timeout in seconds for the http request.
    required: false
    default: 10
    type: int
  x_broker:
    description: Custom HTTP header with the broker virtual router id, if using a SEMPv2 Proxy/agent infrastructure.
    required: false
    type: str
  reverse_proxy:
    description: "Use a reverse proxy / api gateway. Note: B(Experimental. Not permitted for Solace Cloud API)."
    required: false
    type: dict
    suboptions:
      semp_base_path:
        description: "Base path prepended to all SEMP calls. Example: 'my/base/path'. Resulting URL will be: http(s)://{host}:{port}/{semp_base_path}/{module-semp-call-path}"
        type: str
        required: false
      use_basic_auth:
        description: Flag to use basic authentication in the http(s) call or not. Uses 'username'/'password'.
        type: bool
        required: false
        default: false
      query_params:
        description: "Additional query paramters to add to the URL. Example: 'apiCode: {my-api-code}'."
        type: dict
        required: false
      headers:
        description: "Additional headers to add to the http call. Example: 'apiKey: {my-api-key}'."
        type: dict
        required: false
        suboptions:
          x-asc-module:
            description: "Flag for the module to add the header 'x-asc-module:{module-name}' to the http call with it's module name."
            type: bool
            required: false
            default: false
          x-asc-module-op:
            description: "Flag for the module to add the header 'x-asc-module-op:{module operation}' to the http call with the module's operation."
            type: bool
            required: false
            default: false
'''

    VPN = r'''
options:
  msg_vpn:
    description: The message vpn.
    required: true
    type: str
'''

    BROKER_CONFIG_SOLACE_CLOUD = r'''
options:
  solace_cloud_api_token:
    description:
      - The API Token.
      - Generate using Solace Cloud console with the appropriate permissions for the operations you want to enable.
      - Either both (solace_cloud_api_token AND solace_cloud_service_id) must be provided or none.
    type: str
    required: false
  solace_cloud_service_id:
    description:
      - The service id in Solace Cloud.
      - Click on the service in Solace Cloud - the service id is in the URL.
      - Either both (solace_cloud_api_token AND solace_cloud_service_id) must be provided or none.
    type: str
    required: false
'''

    BROKER_CONFIG_SOLACE_CLOUD_MANDATORY = r'''
options:
  solace_cloud_api_token:
    description:
      - The API Token.
      - Generate using Solace Cloud console with the appropriate permissions for the operations you want to enable.
      - Either both (solace_cloud_api_token AND solace_cloud_service_id) must be provided or none.
    type: str
    required: true
  solace_cloud_service_id:
    description:
      - The service id in Solace Cloud.
      - Click on the service in Solace Cloud - the service id is in the URL.
      - Either both (solace_cloud_api_token AND solace_cloud_service_id) must be provided or none.
    type: str
    required: true
'''

    SOLACE_CLOUD_CONFIG_SOLACE_CLOUD = r'''
options:
  solace_cloud_api_token:
    description:
      - The API Token.
      - Generate using Solace Cloud console with the appropriate permissions for the operations you want to enable.
    type: str
    required: true
    aliases: [api_token]
  timeout:
    description: Connection timeout in seconds for the http request.
    required: false
    default: 60
    type: int
  validate_certs:
    description: Flag to switch validation of client certificates on/off when using a secure connection.
    required: false
    default: true
    type: bool
'''

    SOLACE_CLOUD_SERVICE_CONFIG_SERVICE_ID = r'''
options:
  solace_cloud_service_id:
    description:
      - The service id of a service in Solace Cloud.
      - Click on the service in Solace Cloud - the service id is in the URL.
    type: str
    required: false
    aliases: [service_id]
'''

    VIRTUAL_ROUTER = r'''
options:
  virtual_router:
    description: The virtual router.
    required: false
    type: str
    default: primary
    choices:
      - primary
      - backup
'''

    SEMPV2_SETTINGS = r'''
options:
  sempv2_settings:
    description: JSON dictionary of additional configuration for the SEMP V2 API. See Reference documentation.
    required: false
    type: dict
    aliases: [settings]
'''

    SEMPV1_SETTINGS = r'''
options:
  sempv1_settings:
    description: JSON dictionary of additional configuration for the SEMP V1 API. Converted automatically to RPC XML. See Reference documentation.
    required: false
    type: dict
'''

    SOLACE_CLOUD_SETTINGS = r'''
options:
  solace_cloud_settings:
    description: JSON dictionary of additional configuration for the Solace Cloud API. See Reference documentation.
    required: false
    type: dict
    aliases: [settings]
'''

    STATE = r'''
options:
  state:
    description: Target state.
    required: false
    default: present
    type: str
    choices:
      - present
      - absent
'''

    STATE_CRUD_LIST = r'''
options:
  state:
    description: Target state for CRUD list operation.
    required: false
    default: present
    type: str
    choices:
      - present
      - absent
      - exactly
'''

    GET_LIST = r'''
description:
- "Implements the config and monitor API."
- "Retrieves all objects that match the criteria defined in the 'where' clause and returns the fields defined in the 'select' parameter."
options:
  api:
    description: The API the query should run against.
    required: false
    type: str
    default: config
    choices:
      - config
      - monitor
  page_count:
    description: "The number of results to be fetched from broker in single call. Note: always returns the entire result set by following the cursor."
    required: false
    type: int
    default: 100
  query_params:
    description: The query parameters.
    required: false
    type: dict
    default: {}
    suboptions:
        select:
          description: Include in the response only selected attributes of the object, or exclude from the response selected attributes of the object. See the documentation for the select parameter.
          type: list
          default: []
          elements: str
        where:
          description:
            - Include in the response only objects where certain conditions are true. See the the documentation for the where parameter.
            - "Note: URL encoded automatically, you can safely use '/, <, <=, >, >=, != .. '"
          type: list
          default: []
          elements: str
'''

    GET_LIST_MONITOR = r'''
description:
- "Implements the monitor API."
- "Retrieves all objects that match the criteria defined in the 'where' clause and returns the fields defined in the 'select' parameter."
options:
  api:
    description: The API the query should run against.
    required: false
    type: str
    default: monitor
    choices:
      - monitor
  page_count:
    description: "The number of results to be fetched from broker in single call. Note: always returns the entire result set by following the cursor."
    required: false
    type: int
    default: 100
  query_params:
    description: The query parameters.
    required: false
    type: dict
    default: {}
    suboptions:
        select:
          description: Include in the response only selected attributes of the object, or exclude from the response selected attributes of the object. See the documentation for the select parameter.
          type: list
          default: []
          elements: str
        where:
          description:
            - Include in the response only objects where certain conditions are true. See the the documentation for the where parameter.
            - "Note: URL encoded automatically, you can safely use '/, <, <=, >, >=, != .. '"
          type: list
          default: []
          elements: str
'''
