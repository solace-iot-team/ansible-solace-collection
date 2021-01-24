#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_get_facts

short_description: get facts from M(solace_gather_facts)

description: >
  Provides convenience functions to access solace facts retrieved from broker service using M(solace_gather_facts) from 'ansible_facts.solace'.

notes:
- In order to access other hosts' (other than the current 'inventory_host') facts, you must not use the 'serial' strategy for the playbook.

options:
  hostvars:
    description: The playbook's 'hostvars'.
    required: True
    type: dict
  host:
    description: The playbook host to retrieve the facts from.
    required: True
    type: str
  msg_vpn:
    description: The message vpn.
    required: False
    type: str
  fields:
    description: "List of field names to retrieve from hostvars. Note: Retrieves the first occurrence of the field name only."
    required: False
    type: list
    default: []
    elements: str
  field_funcs:
    description: List of pre-built field functions that retrieve values from hostvars.
    required: False
    type: list
    default: []
    elements: str
    suboptions:
        get_serviceSmfPlainTextListenPort:
            description: Retrieve the smf plain listen port
            type: str
            required: no
        get_serviceSmfCompressionListenPort:
            description: Retrieve the smf compressed listen port
            type: str
            required: no
        get_serviceSmfTlsListenPort:
            description: Retrieve the smf tls listen port
            type: str
            required: no
        get_virtualRouterName:
            description: Retrieve the virtual router name
            type: str
            required: no
        get_serviceSMFMessagingEndpoints:
            description: Retrieve the all smf messaging endpoints
            type: str
            required: no
        get_bridge_remoteMsgVpnLocations:
            description:
                - "Retrieve enabled remote message vpn locations (plain, secured, compressed) for the service/broker."
                - "For Solace Cloud: {hostname}:{port}."
                - "For broker: v:{virtualRouterName}."
            type: str
            required: no
        get_allClientConnectionDetails:
            description:
                - "Retrieve all enabled client connection details for the various protocols for the service/broker."
            type: str
            required: no
        get_dmrClusterConnectionDetails:
        


seealso:
- module: solace_gather_facts

author: Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''

  name: "Example for solace_get_facts"
  hosts: all
  gather_facts: no
  any_errors_fatal: true
  collections:
    - solace.pubsub_plus
  module_defaults:
    solace_gather_facts:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      solace_cloud_api_token: "{{ solace_cloud_api_token | default(omit) }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"

  tasks:
    - name: Gather Solace Facts
      solace_gather_facts:

    - name: "Get Host SMF Messaging Endpoints Facts: solace-cloud-1"
      solace_get_facts:
        hostvars: "{{ hostvars }}"
        host: solace-cloud-1
        fields:
        field_funcs:
          - get_serviceSMFMessagingEndpoints
      register: solace_cloud_1_smf_enpoints_facts

    - name: "Get Host Service Items: local"
      solace_get_facts:
        hostvars: "{{ hostvars }}"
        host: local
        fields:
        field_funcs:
          - get_serviceSmfPlainTextListenPort
          - get_serviceSmfCompressionListenPort
          - get_serviceSmfTlsListenPort
          - get_virtualRouterName
      register: local_service_facts

    - name: "Get Host Service Items: solace-cloud-1"
      solace_get_facts:
        hostvars: "{{ hostvars }}"
        host: solace-cloud-1
        field_funcs:
          - get_serviceSmfPlainTextListenPort
          - get_serviceSmfCompressionListenPort
          - get_serviceSmfTlsListenPort
          - get_virtualRouterName
      register: solace_cloud_1_service_facts

    - name: "Show Host Service Facts"
      debug:
        msg:
          - "local_service_facts:"
          - "{{ local_service_facts }}"
          - "solace_cloud_1_service_facts:"
          - "{{ solace_cloud_1_service_facts }}"
'''

RETURN = '''

facts:
    description: The facts requested.
    type: dict
    returned: success
    elements: dict
    sample:
        facts:
            serviceSmfCompressionListenPort: 55003
            serviceSmfPlainTextListenPort: 55555
            serviceSmfTlsListenPort: 55443
            virtualRouterName: "single-aws-eu-west-6e-4ftdf"

'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceReadFactsTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError, SolaceInternalError
from ansible.module_utils.basic import AnsibleModule
from urllib.parse import urlparse
import json
from json.decoder import JSONDecodeError


class SolaceGetFactsTask(SolaceReadFactsTask):

    FIELD_FUNCS = [
        "get_serviceSmfPlainTextListenPort",
        "get_serviceSmfCompressionListenPort",
        "get_serviceSmfTlsListenPort",
        "get_virtualRouterName",
        "get_serviceSMFMessagingEndpoints",
        "get_bridge_remoteMsgVpnLocations",
        "get_allClientConnectionDetails",
        "get_dmrClusterConnectionDetails"
    ]

    def __init__(self, module):
        super().__init__(module)

    def validate_params(self):
        params = self.get_module().params
        hostvars = params['hostvars']
        host = params['host']
        # check hostvars
        if host not in hostvars:
            raise SolaceParamsValidationError("hostvars, host", host, f"cannot find host={host} in hostvars - cross check spelling with inventory file")
        if 'ansible_facts' not in hostvars[host]:
            raise SolaceParamsValidationError(f"hostvars[{host}]", hostvars[host], f"cannot find 'ansible_facts'")
        if 'solace' not in hostvars[host]['ansible_facts']:
            raise SolaceParamsValidationError(f"hostvars[{host}]['ansible_facts']", hostvars[host]['ansible_facts'], f"cannot find 'solace'")
        # field funcs
        has_get_funcs = self.validate_param_field_funcs(self.FIELD_FUNCS, params['field_funcs'])
        if not has_get_funcs:
            raise SolaceParamsValidationError("field_funcs", params['field_funcs'], "no get functions found - specify at least one")        
        # check vpn exists 
        search_dict = hostvars[host]['ansible_facts']['solace']
        vpn_name = params['msg_vpn']
        vpns = self.get_vpns(search_dict)
        if not vpn_name:
            if len(vpns) == 1:
                self.get_module().params['msg_vpn'] = vpns[0]
            else:    
                raise SolaceParamsValidationError("msg_vpn", params['msg_vpn'], f"select one of {vpns}")     
        if not self.get_module().params['msg_vpn'] in vpns:
            raise SolaceParamsValidationError("msg_vpn", params['msg_vpn'], f"vpn does not exist - select one of {vpns}")     

    def do_task(self):    
        self.validate_params()
        
        params = self.get_module().params
        hostvars = params['hostvars']
        host = params['host']
        vpn_name = params['msg_vpn']
        search_dict = hostvars[host]['ansible_facts']['solace']
        field_funcs = params['field_funcs']
        facts = dict()

        if field_funcs and len(field_funcs) > 0:
            for field_func in field_funcs:
                field, value = self.call_dynamic_func(field_func, search_dict, vpn_name)
                facts[field] = value

        result = self.create_result(rc=0, changed=False)
        result['facts'] = facts
        return None, result

    def get_vpns(self, search_dict: dict) -> list:
        return list(search_dict['vpns'].keys())

    def get_broker_service_dict(self, search_dict: dict, field: str, value: str, strict=True):
        service_dict = self.get_nested_dict(search_dict, field, value)
        if service_dict is None:
            if strict:
                raise SolaceInternalError(f"Could not find '{field}={value}' in search_dict in broker service ansible_facts.")
            else:
                service_dict = dict(enabled=False)
        return service_dict

    def get_sc_messaging_protocol_endpoint(self, search_dict: dict, field: str, value: str):
        end_points = self.get_field(search_dict, "endPoints")
        end_point_dict = self.get_nested_dict(end_points, field, value)
        return end_point_dict

    def get_sc_messaging_protocols(self, search_dict: dict):  
        mps = self.get_field(search_dict, "messagingProtocols")
        if not mps:
            raise SolaceInternalError(f"Could not find 'messagingProtocols' in 'ansible_facts.solace'. API may have changed.")
        return mps  

    def get_sc_messaging_protocol_dict(self, search_dict: dict, protocol: str):
        protocol_dict = self.get_nested_dict(search_dict, field="name", value=protocol) 
        if not protocol_dict:
            protocol_dict = dict(
                enabled=False
            )
        else:
            protocol_dict['enabled'] = True
        return protocol_dict

    def get_allClientConnectionDetails(self, search_dict: dict, vpn: str):
        ccds = dict()
        if search_dict['isSolaceCloud']:
            messaging_protocols = self.get_sc_messaging_protocols(search_dict)

            smf_dict    = self.get_sc_messaging_protocol_dict(messaging_protocols, 'SMF')    
            mqtt_dict   = self.get_sc_messaging_protocol_dict(messaging_protocols, 'MQTT')
            amqp_dict   = self.get_sc_messaging_protocol_dict(messaging_protocols, 'AMQP')
            rest_dict   = self.get_sc_messaging_protocol_dict(messaging_protocols, 'REST')
            jms_dict    = self.get_sc_messaging_protocol_dict(messaging_protocols, 'JMS')
            web_dict    = self.get_sc_messaging_protocol_dict(messaging_protocols, 'Web Messaging')

            vpn_attributes = self.get_field(search_dict, "msgVpnAttributes")
            if not vpn_attributes:
                raise SolaceInternalError(f"Could not find 'msgVpnAttributes' in 'ansible_facts.solace'. API may have changed.")
            trust_store_uri = vpn_attributes['truststoreUri']
        else:
            vpn_dict = search_dict['vpns'][vpn]
            _smf_dict = self.get_broker_service_dict(search_dict, field="name", value='SMF', strict=False)
            smf_dict = dict(
                serviceSmfMaxConnectionCount=vpn_dict['serviceSmfMaxConnectionCount'],
                serviceSmfPlainTextEnabled=vpn_dict['serviceSmfPlainTextEnabled'],
                serviceSmfTlsEnabled=vpn_dict['serviceSmfTlsEnabled'],
                serviceSmfCompressionEnabled=int(_smf_dict['compression-listen-port']) > 0,
                serviceSmfPlainTextListenPort=int(_smf_dict['listen-port']),
                serviceSmfCompressionListenPort=int(_smf_dict['compression-listen-port']),
                serviceSmfTlsListenPort=int(_smf_dict['ssl']['listen-port'])
            )
            # mqtt_dict = self.get_broker_service_dict(search_dict, field="name", value='MQTT', strict=False)
            mqtt_dict = dict(
                serviceMqttMaxConnectionCount=vpn_dict['serviceMqttMaxConnectionCount'],
                serviceMqttPlainTextEnabled=vpn_dict['serviceMqttPlainTextEnabled'],
                serviceMqttPlainTextListenPort=vpn_dict['serviceMqttPlainTextListenPort'],
                serviceMqttTlsEnabled=vpn_dict['serviceMqttTlsEnabled'],
                serviceMqttTlsListenPort=vpn_dict['serviceMqttTlsListenPort'],
                serviceMqttTlsWebSocketEnabled=vpn_dict['serviceMqttTlsWebSocketEnabled'],
                serviceMqttTlsWebSocketListenPort=vpn_dict['serviceMqttTlsWebSocketListenPort'],
                serviceMqttWebSocketEnabled=vpn_dict['serviceMqttWebSocketEnabled'],
                serviceMqttWebSocketListenPort=vpn_dict['serviceMqttWebSocketListenPort']
            )
            # amqp_dict = self.get_broker_service_dict(search_dict, field="name", value='AMQP', strict=False)
            amqp_dict = dict(
                serviceAmqpMaxConnectionCount=vpn_dict['serviceAmqpMaxConnectionCount'],
                serviceAmqpPlainTextEnabled=vpn_dict['serviceAmqpPlainTextEnabled'],
                serviceAmqpPlainTextListenPort=vpn_dict['serviceAmqpPlainTextListenPort'],
                serviceAmqpTlsEnabled=vpn_dict['serviceAmqpTlsEnabled'],
                serviceAmqpTlsListenPort=vpn_dict['serviceAmqpTlsListenPort']
            )
            # rest_dict = self.get_broker_service_dict(search_dict, field="name", value='REST', strict=False)
            rest_dict = dict(
                serviceRestIncomingMaxConnectionCount=vpn_dict['serviceRestIncomingMaxConnectionCount'],
                serviceRestIncomingPlainTextEnabled=vpn_dict['serviceRestIncomingPlainTextEnabled'],
                serviceRestIncomingPlainTextListenPort=vpn_dict['serviceRestIncomingPlainTextListenPort'],
                serviceRestIncomingTlsEnabled=vpn_dict['serviceRestIncomingTlsEnabled'],
                serviceRestIncomingTlsListenPort=vpn_dict['serviceRestIncomingTlsListenPort'],
                serviceRestMode=vpn_dict['serviceRestMode'],
                serviceRestOutgoingMaxConnectionCount=vpn_dict['serviceRestOutgoingMaxConnectionCount']
            )
            jms_dict = None
            web_dict = self.get_broker_service_dict(search_dict, field="name", value='WEB', strict=False)
            trust_store_uri = None

        ccds['SMF'] = smf_dict
        ccds['MQTT'] = mqtt_dict
        ccds['AMQP'] = amqp_dict
        ccds['REST'] = rest_dict
        ccds['JMS'] = jms_dict
        ccds['WebMessaging'] = web_dict
        if trust_store_uri:
            ccds['TrustStore'] = dict(uri=trust_store_uri)
        return 'clientConnectionDetails', ccds

    def get_bridge_remoteMsgVpnLocations(self, search_dict: dict, vpn: str=None):
        locs = dict(
            plain=None,
            compressed=None,
            secured=None
        )
        if search_dict['isSolaceCloud']:
            _f, smf_end_point_dict = self.get_serviceSMFMessagingEndpoints(search_dict)
            if smf_end_point_dict['SMF']['SMF']['uriComponents']['host']:
                locs['plain'] = (str(smf_end_point_dict['SMF']['SMF']['uriComponents']['host'])
                                + ":" + str(smf_end_point_dict['SMF']['SMF']['uriComponents']['port']))
            else:
                locs['plain'] = None
            if smf_end_point_dict['SMF']['CompressedSMF']['uriComponents']['host']:
                locs['compressed'] = (str(smf_end_point_dict['SMF']['CompressedSMF']['uriComponents']['host'])
                                      + ":" + str(smf_end_point_dict['SMF']['CompressedSMF']['uriComponents']['port']))
            else:
                locs['compressed'] = None
            if smf_end_point_dict['SMF']['SecuredSMF']['uriComponents']['host']:
                locs['secured'] = (str(smf_end_point_dict['SMF']['SecuredSMF']['uriComponents']['host'])
                                  + ":" + str(smf_end_point_dict['SMF']['SecuredSMF']['uriComponents']['port']))
            else:
                locs['secured'] = None
        else:
            _f, virtual_router = self.get_virtualRouterName(search_dict, vpn)
            loc = "v:" + virtual_router
            locs['plain'] = loc
            locs['compressed'] = loc
            locs['secured'] = loc

        return 'bridge_remoteMsgVpnLocations', locs

    def get_serviceSMFMessagingEndpoints(self, search_dict: dict, vpn: str=None):
        eps = dict(
            SMF=dict(
                SMF=dict(),
                SecuredSMF=dict(),
                CompressedSMF=dict()
            )
        )
        smf_protocol = None
        smf_host = None
        smf_port = None
        smf_uri = None

        sec_smf_protocol = None
        sec_smf_host = None
        sec_smf_port = None
        sec_smf_uri = None

        cmp_smf_protocol = None
        cmp_smf_host = None
        cmp_smf_port = None
        cmp_smf_uri = None

        if search_dict['isSolaceCloud']:
            messaging_protocols = self.get_sc_messaging_protocols(search_dict)
            smf_dict    = self.get_sc_messaging_protocol_dict(messaging_protocols, 'SMF') 
            # if endPoint is not enabled, API omits it
            end_points = self.get_field(smf_dict, "endPoints")
            smf_end_point_dict = self.get_nested_dict(end_points, field='name', value='SMF')
            if smf_end_point_dict:
                smf_uri = smf_end_point_dict['uris'][0]
                t = urlparse(smf_uri)
                smf_protocol = t.scheme
                smf_host = t.hostname
            sec_smf_end_point_dict = self.get_nested_dict(end_points, field='name', value='Secured SMF')
            if sec_smf_end_point_dict:
                sec_smf_uri = sec_smf_end_point_dict['uris'][0]
                t = urlparse(sec_smf_uri)
                sec_smf_protocol = t.scheme
                sec_smf_host = t.hostname
            cmp_smf_end_point_dict = self.get_nested_dict(end_points, field='name', value='Compressed SMF')
            if cmp_smf_end_point_dict:
                cmp_smf_uri = cmp_smf_end_point_dict['uris'][0]
                t = urlparse(cmp_smf_uri)
                cmp_smf_protocol = t.scheme
                cmp_smf_host = t.hostname

        _f, smf_port = self.get_serviceSmfPlainTextListenPort(search_dict, vpn)
        _f, sec_smf_port = self.get_serviceSmfTlsListenPort(search_dict, vpn)
        _f, cmp_smf_port = self.get_serviceSmfCompressionListenPort(search_dict, vpn)
        # put the dict together
        # smf
        smf = dict()
        smf_ucs = dict()
        smf_ucs['protocol'] = smf_protocol
        smf_ucs['host'] = smf_host
        smf_ucs['port'] = smf_port
        smf['uriComponents'] = smf_ucs
        smf['uri'] = smf_uri
        eps['SMF']['SMF'] = smf
        # secured smf
        sec_smf = dict()
        sec_smf_ucs = dict()
        sec_smf_ucs['protocol'] = sec_smf_protocol
        sec_smf_ucs['host'] = sec_smf_host
        sec_smf_ucs['port'] = sec_smf_port
        sec_smf['uriComponents'] = sec_smf_ucs
        sec_smf['uri'] = sec_smf_uri
        eps['SMF']['SecuredSMF'] = sec_smf
        # compressed smf
        cmp_smf = dict()
        cmp_smf_ucs = dict()
        cmp_smf_ucs['protocol'] = cmp_smf_protocol
        cmp_smf_ucs['host'] = cmp_smf_host
        cmp_smf_ucs['port'] = cmp_smf_port
        cmp_smf['uriComponents'] = cmp_smf_ucs
        cmp_smf['uri'] = cmp_smf_uri
        eps['SMF']['CompressedSMF'] = cmp_smf
        return 'serviceMessagingEndpoints', eps

    def get_serviceSmfPlainTextListenPort(self, search_dict: dict, vpn: str):
        if search_dict['isSolaceCloud']:
            messaging_protocols = self.get_sc_messaging_protocols(search_dict)
            smf_dict = self.get_sc_messaging_protocol_dict(messaging_protocols, 'SMF')
            end_point_dict = self.get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='SMF')
            if end_point_dict:
                uri = end_point_dict['uris'][0]
                value = urlparse(uri).port
            else:
                value = None
        else:
            smf_dict = self.get_broker_service_dict(search_dict, field="name", value="SMF")
            value = smf_dict['listen-port']
        return 'serviceSmfPlainTextListenPort', value

    def get_serviceSmfCompressionListenPort(self, search_dict: dict, vpn: str):
        if search_dict['isSolaceCloud']:
            messaging_protocols = self.get_sc_messaging_protocols(search_dict)
            smf_dict = self.get_sc_messaging_protocol_dict(messaging_protocols, 'SMF')
            end_point_dict = self.get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='Compressed SMF')
            if end_point_dict:
                uri = end_point_dict['uris'][0]
                value = urlparse(uri).port
            else:
                value = None
        else:
            smf_dict = self.get_broker_service_dict(search_dict, field="name", value="SMF")
            value = smf_dict['compression-listen-port']
        return 'serviceSmfCompressionListenPort', value

    def get_serviceSmfTlsListenPort(self, search_dict: dict, vpn: str):
        if search_dict['isSolaceCloud']:
            messaging_protocols = self.get_sc_messaging_protocols(search_dict)
            smf_dict = self.get_sc_messaging_protocol_dict(messaging_protocols, 'SMF')
            end_point_dict = self.get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='Secured SMF')
            if end_point_dict:
                uri = end_point_dict['uris'][0]
                value = urlparse(uri).port
            else:
                value = None
        else:
            smf_dict = self.get_broker_service_dict(search_dict, field="name", value="SMF")
            value = smf_dict['ssl']['listen-port']
        return 'serviceSmfTlsListenPort', value

    def get_virtualRouterName(self, search_dict: dict, vpn: str):
        if search_dict['isSolaceCloud']:
            value = self.get_field(search_dict, 'primaryRouterName')
        else:
            value = self.get_field(search_dict, 'virtualRouterName')
        return 'virtualRouterName', value

    def get_dmrClusterConnectionDetails(self, search_dict: dict, vpn: str):
        if search_dict['isSolaceCloud']:
            value = self.get_field(search_dict, 'cluster')
        else:
            raise SolaceInternalError('standalone broker not supported, only solace cloud.')
        return 'dmrClusterConnectionDetails', value

def run_module():
    module_args = dict(
        hostvars=dict(type='dict', required=True),
        host=dict(type='str', required=True),
        field_funcs=dict(type='list', required=False, default=[], elements='str'),
        # fields=dict(type='list', required=False, default=[], elements='str'),
        msg_vpn=dict(type='str', required=False, default=None)
    )
    arg_spec = dict()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGetFactsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
