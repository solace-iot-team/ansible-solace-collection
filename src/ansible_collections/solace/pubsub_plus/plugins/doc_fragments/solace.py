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
- "Sempv2 Config Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/)."

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
  sempv2_version:
    description:
      - The SEMP V2 API version of the broker. See M(solace_get_facts) for info on how to retrieve the version from the broker.
      - "Note: If the module requires it and not provided, the module will fetch it using the SEMP call 'about/api'."
    required: false
    type: str
    aliases: [semp_version]
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
'''

    SOLACE_CLOUD_SERVICE_CONFIG = r'''
options:
  api_token:
    description:
      - The API Token.
      - Generate using Solace Cloud console with the appropriate permissions for the operations you want to enable.
    type: str
    required: true
  timeout:
    description: Connection timeout in seconds for the http/s request.
    required: false
    default: 60
    type: int
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

    SETTINGS = r'''
options:
  settings:
    description: JSON dictionary of additional configuration, see Reference documentation.
    required: false
    type: dict
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
