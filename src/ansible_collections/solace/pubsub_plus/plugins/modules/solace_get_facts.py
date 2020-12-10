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

short_description: Provides convenience functions to access solace facts gathered with M(solace_gather_facts).

description: >
  Provides convenience functions to access solace facts from 'ansible_facts.solace'.
  Call M(solace_gather_facts) first.

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
  fields:
    description: List of field names to retrieve from hostvars.
    note: Retrieves the first occurrence of the field name only.
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
    choices:
      - get_serviceSmfPlainTextListenPort
      - get_serviceSmfCompressionListenPort
      - get_serviceSmfTlsListenPort
      - get_virtualRouterName
      - get_serviceSMFMessagingEndpoints
      - get_bridge_remoteMsgVpnLocations
      - get_allClientConnectionDetails
    functions:
      get_bridge_remoteMsgVpnLocations:
        description:
            - "Retrieve enabled remote message vpn locations (plain, secured, compressed) for the service/broker."
            - "For Solace Cloud: {hostname}:{port}."
            - "For broker: v:{virtualRouterName}."
      get_allClientConnectionDetails:
        description:
            - "Retrieve all enabled client connection details for the various protocols for the service/broker."

seealso:
- module: solace_gather_facts

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

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
    returned: on success
    elements: complex
    samples:

        "facts": {
            "serviceSmfCompressionListenPort": 55003,
            "serviceSmfPlainTextListenPort": 55555,
            "serviceSmfTlsListenPort": 55443,
            "virtualRouterName": "single-aws-eu-west-6e-4ftdf"
        }

        "facts": {
                "serviceMessagingEndpoints": {
                    "SMF": {
                        "CompressedSMF": {
                            "uri": "tcp://mr4yqbkp31vav.messaging.solace.cloud:55003",
                            "uriComponents": {
                                "host": "mr4yqbkp31vav.messaging.solace.cloud",
                                "port": 55003,
                                "protocol": "tcp"
                            }
                        },
                        "SMF": {
                            "uri": "tcp://mr4yqbkp31vav.messaging.solace.cloud:55555",
                            "uriComponents": {
                                "host": "mr4yqbkp31vav.messaging.solace.cloud",
                                "port": 55555,
                                "protocol": "tcp"
                            }
                        },
                        "SecuredSMF": {
                            "uri": "tcps://mr4yqbkp31vav.messaging.solace.cloud:55443",
                            "uriComponents": {
                                "host": "mr4yqbkp31vav.messaging.solace.cloud",
                                "port": 55443,
                                "protocol": "tcps"
                            }
                        }
                    }
                }
            }

'''


MODULE_HAS_IMPORT_ERROR = False
MODULE_IMPORT_ERR_TRACEBACK = None
import traceback
try:
    import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_common as sc
    from ansible.module_utils.basic import AnsibleModule
    from ansible.errors import AnsibleError
    from urllib.parse import urlparse
    import json
    from json.decoder import JSONDecodeError
except ImportError:
    MODULE_HAS_IMPORT_ERROR = True
    MODULE_IMPORT_ERR_TRACEBACK = traceback.format_exc()

class SolaceGetFactsTask():

    def __init__(self, module):
        sc.module_fail_on_import_error(module, MODULE_HAS_IMPORT_ERROR, MODULE_IMPORT_ERR_TRACEBACK)
        self.module = module
        return

    def get_facts(self):

        hostvars = self.module.params['hostvars']
        host = self.module.params['host']
        vpn = self.module.params['msg_vpn']
        fields = self.module.params['fields']
        field_funcs = self.module.params['field_funcs']
        # either fields or field_funcs must have at least one element
        field_params_ok = False
        if fields is not None and len(fields) > 0:
            field_params_ok = True
        if not field_params_ok and field_funcs is not None and len(field_funcs) > 0:
            field_params_ok = True
        if not field_params_ok:
            fail_reason = "Either 'fields' or 'field_funcs' must be provided."
            return False, fail_reason

        # get {host}.ansible_facts.solace from hostvars
        if host not in hostvars:
            fail_reason = "Could not find host:'{}' in hostvars. Hint: Cross check spelling with inventory file.".format(host)
            return False, fail_reason
        if 'ansible_facts' not in hostvars[host]:
            fail_reason = "Could not find 'ansible_facts' hostvars['{}']. Hint: Call 'solace_gather_facts' module first.".format(host)
            return False, fail_reason
        if 'solace' not in hostvars[host]['ansible_facts']:
            fail_reason = "Could not find 'solace' in hostvars['{}']['ansible_facts']. Hint: Call 'solace_gather_facts' module first.".format(host)
            return False, fail_reason

        search_object = hostvars[host]['ansible_facts']['solace']

        if not _check_vpn_exists(search_object, vpn):
            fail_reason = "Could not find vpn: '{}' in 'ansible_facts.solace' for host: '{}'.".format(vpn, host)
            return False, fail_reason

        facts = dict()

        if fields is not None and len(fields) > 0:
            for field in fields:
                value = _get_field(search_object, field)
                if value is None:
                    fail_reason = "Could not find field: '{}' in 'ansible_facts.solace' for host: '{}'. Pls check spelling.".format(field, host)
                    return False, fail_reason
                facts[field] = value

        if field_funcs is not None and len(field_funcs) > 0:
            try:
                for field_func in field_funcs:
                    if field_func == 'get_serviceSmfPlainTextListenPort':
                        field, value = _get_serviceSmfPlainTextListenPort(search_object)
                    elif field_func == 'get_serviceSmfCompressionListenPort':
                        field, value = _get_serviceSmfCompressionListenPort(search_object)
                    elif field_func == 'get_serviceSmfTlsListenPort':
                        field, value = _get_serviceSmfTlsListenPort(search_object)
                    elif field_func == 'get_virtualRouterName':
                        field, value = _get_virtualRouterName(search_object)
                    elif field_func == 'get_serviceSMFMessagingEndpoints':
                        field, value = _get_serviceSMFMessagingEndpoints(search_object)
                    elif field_func == 'get_bridge_remoteMsgVpnLocations':
                        field, value = _get_bridge_remoteMsgVpnLocations(search_object)
                    elif field_func == 'get_allClientConnectionDetails':
                        field, value = _get_allClientConnectionDetails(search_object, vpn)
                    else:
                        fail_reason = "Unknown field_func: '{}'. Pls check the documentation for supported field functions: 'ansible-doc solace_get_facts'.".format(field_func)
                        return False, fail_reason
                    if field is None or value is None:
                        fail_reason = "Function '{}()' could not find value in 'ansible_facts.solace' for host: '{}'. Pls raise an issue.".format(field_func, host)
                        return False, fail_reason
                    facts[field] = value
            except AnsibleError as e:
                try:
                    e_msg = json.loads(str(e))
                except JSONDecodeError:
                    e_msg = [str(e)]
                ex_msg = [
                    "field_func:'{}'".format(field_func),
                    e_msg
                ]
                raise AnsibleError(json.dumps(ex_msg))

        return True, facts

#
# field funcs
#


def _check_vpn_exists(search_dict, search_vpn):
    if not search_vpn:
        return True
    if search_dict['isSolaceCloud']:
        message_vpn_attributes_dict = _get_sc_message_vpn_attributes_dict(search_dict)
        vpn = message_vpn_attributes_dict['vpnName']
        return (vpn == search_vpn)
    else:
        # for SEMPv1:
        vpns = search_dict['about']['user']['msgVpns']
        for vpn in vpns:
            if vpn['msgVpnName'] == search_vpn:
                return True
        # TODO: for SEMPv2:
        # once solace_gather_facts is extended
    return False


def _get_allClientConnectionDetails(search_dict, vpn=None):
    ccds = dict()
    if search_dict['isSolaceCloud']:
        # msg_vpn_name = _get_field(search_dict, field='msgVpnName'):
        # TODO: needs to find it for all vpns: "vpn-name": "default",
        smf_dict = _get_sc_messaging_protocol_dict(search_dict, 'SMF')
        mqtt_dict = _get_sc_messaging_protocol_dict(search_dict, 'MQTT')
        amqp_dict = _get_sc_messaging_protocol_dict(search_dict, 'AMQP')
        rest_dict = _get_sc_messaging_protocol_dict(search_dict, 'REST')
        jms_dict = _get_sc_messaging_protocol_dict(search_dict, 'JMS')
        web_msg_dict = _get_sc_messaging_protocol_dict(search_dict, 'Web Messaging')
        message_vpn_attributes_dict = _get_sc_message_vpn_attributes_dict(search_dict)
        trust_store_uri = message_vpn_attributes_dict['truststoreUri']
    else:
        # logging.debug("\n\n broker: search_dict=\n%s\n\n", json.dumps(search_dict, indent=2))
        # TODO: needs to find it for all vpns: "vpn-name": "default",
        # TODO: only retrieve if vpn-name exists (relevant for AMQP)

        smf_dict = _get_broker_service_dict(search_dict, field="name", value='SMF', strict=False)
        mqtt_dict = _get_broker_service_dict(search_dict, field="name", value='MQTT', strict=False)
        amqp_dict = _get_broker_service_dict(search_dict, field="name", value='AMQP', strict=False)
        rest_dict = _get_broker_service_dict(search_dict, field="name", value='REST', strict=False)
        # using SEMPv1: assuming same as SMF, check with SEMPv2
        # jms_dict = _get_broker_service_dict(search_dict, field="name", value='JMS', strict=False)
        jms_dict = None
        web_msg_dict = _get_broker_service_dict(search_dict, field="name", value='WEB', strict=False)
        trust_store_uri = None

    ccds['SMF'] = smf_dict
    ccds['MQTT'] = mqtt_dict
    ccds['AMQP'] = amqp_dict
    ccds['REST'] = rest_dict
    ccds['JMS'] = jms_dict
    ccds['WebMessaging'] = web_msg_dict
    if trust_store_uri:
        ccds['TrustStore'] = dict(uri=trust_store_uri)
    return 'clientConnectionDetails', ccds


def _get_bridge_remoteMsgVpnLocations(search_dict):
    locs = dict(
        plain=None,
        compressed=None,
        secured=None
    )
    if search_dict['isSolaceCloud']:
        _f, smfMessagingEndpoints = _get_serviceSMFMessagingEndpoints(search_dict)
        if smfMessagingEndpoints['SMF']['SMF']['uriComponents']['host']:
            locs['plain'] = (str(smfMessagingEndpoints['SMF']['SMF']['uriComponents']['host'])
                             + ":" + str(smfMessagingEndpoints['SMF']['SMF']['uriComponents']['port']))
        else:
            locs['plain'] = None
        if smfMessagingEndpoints['SMF']['CompressedSMF']['uriComponents']['host']:
            locs['compressed'] = (str(smfMessagingEndpoints['SMF']['CompressedSMF']['uriComponents']['host'])
                                  + ":" + str(smfMessagingEndpoints['SMF']['CompressedSMF']['uriComponents']['port']))
        else:
            locs['compressed'] = None
        if smfMessagingEndpoints['SMF']['SecuredSMF']['uriComponents']['host']:
            locs['secured'] = (str(smfMessagingEndpoints['SMF']['SecuredSMF']['uriComponents']['host'])
                               + ":" + str(smfMessagingEndpoints['SMF']['SecuredSMF']['uriComponents']['port']))
        else:
            locs['secured'] = None
    else:
        _f, virtual_router = _get_virtualRouterName(search_dict)
        loc = "v:" + virtual_router
        locs['plain'] = loc
        locs['compressed'] = loc
        locs['secured'] = loc

    return 'bridge_remoteMsgVpnLocations', locs


def _get_serviceSMFMessagingEndpoints(search_dict):
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
        smf_dict = _get_sc_messaging_protocols_smf_dict(search_dict)
        # if endPoint is not enabled, API omits it
        smf_end_point_dict = _get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='SMF')
        if smf_end_point_dict:
            smf_uri = _get_sc_messaging_protocol_endpoint_uri(smf_end_point_dict)
            t = urlparse(smf_uri)
            smf_protocol = t.scheme
            smf_host = t.hostname
        sec_smf_end_point_dict = _get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='Secured SMF')
        if sec_smf_end_point_dict:
            sec_smf_uri = _get_sc_messaging_protocol_endpoint_uri(sec_smf_end_point_dict)
            t = urlparse(sec_smf_uri)
            sec_smf_protocol = t.scheme
            sec_smf_host = t.hostname
        cmp_smf_end_point_dict = _get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='Compressed SMF')
        if cmp_smf_end_point_dict:
            cmp_smf_uri = _get_sc_messaging_protocol_endpoint_uri(cmp_smf_end_point_dict)
            t = urlparse(cmp_smf_uri)
            cmp_smf_protocol = t.scheme
            cmp_smf_host = t.hostname

    _f, smf_port = _get_serviceSmfPlainTextListenPort(search_dict)
    f, sec_smf_port = _get_serviceSmfTlsListenPort(search_dict)
    f, cmp_smf_port = _get_serviceSmfCompressionListenPort(search_dict)
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


def _get_serviceSmfPlainTextListenPort(search_dict):
    if search_dict['isSolaceCloud']:
        smf_dict = _get_sc_messaging_protocols_smf_dict(search_dict)
        end_point_dict = _get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='SMF')
        if end_point_dict:
            uri = _get_sc_messaging_protocol_endpoint_uri(end_point_dict)
            value = _get_port_from_uri(uri)
        else:
            value = None
    else:
        smf_dict = _get_broker_service_dict(search_dict, field="name", value="SMF")
        value = smf_dict['listen-port']
    return 'serviceSmfPlainTextListenPort', value


def _get_serviceSmfCompressionListenPort(search_dict):
    if search_dict['isSolaceCloud']:
        smf_dict = _get_sc_messaging_protocols_smf_dict(search_dict)
        end_point_dict = _get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='Compressed SMF')
        if end_point_dict:
            uri = _get_sc_messaging_protocol_endpoint_uri(end_point_dict)
            value = _get_port_from_uri(uri)
        else:
            value = None
    else:
        smf_dict = _get_broker_service_dict(search_dict, field="name", value="SMF")
        value = smf_dict['compression-listen-port']
    return 'serviceSmfCompressionListenPort', value


def _get_serviceSmfTlsListenPort(search_dict):
    if search_dict['isSolaceCloud']:
        smf_dict = _get_sc_messaging_protocols_smf_dict(search_dict)
        end_point_dict = _get_sc_messaging_protocol_endpoint(smf_dict, field='name', value='Secured SMF')
        if end_point_dict:
            uri = _get_sc_messaging_protocol_endpoint_uri(end_point_dict)
            value = _get_port_from_uri(uri)
        else:
            value = None
    else:
        smf_dict = _get_broker_service_dict(search_dict, field="name", value="SMF")
        value = smf_dict['ssl']['listen-port']
    return 'serviceSmfTlsListenPort', value


def _get_virtualRouterName(search_dict):
    if search_dict['isSolaceCloud']:
        value = _get_field(search_dict, 'primaryRouterName')
    else:
        value = _get_field(search_dict, 'virtualRouterName')
    return 'virtualRouterName', value


#
# field func helpers
#

def _get_broker_service_dict(search_dict, field, value, strict=True):
    service_dict = _find_nested_dict(search_dict, field, value)
    if service_dict is None:
        if strict:
            raise AnsibleError("Could not find '{}={}' in search_dict in broker service ansible_facts. Pls raise an issue.".format(field, value))
        else:
            service_dict = dict(enabled=False)
    return service_dict


def _get_sc_message_vpn_attributes_dict(search_dict):
    element = "msgVpnAttributes"
    message_vpn_attributes_dict = _get_field(search_dict, element)
    if message_vpn_attributes_dict is None:
        raise AnsibleError("Could not find '{}' in Solace Cloud service ansible_facts. API may have changed. Pls raise an issue.".format(element))
    return message_vpn_attributes_dict


def _get_sc_messaging_protocols_dict(search_dict):
    element = "messagingProtocols"
    messaging_protocols_dict = _get_field(search_dict, element)
    if messaging_protocols_dict is None:
        raise AnsibleError("Could not find '{}' in Solace Cloud service ansible_facts. API may have changed. Pls raise an issue.".format(element))
    return messaging_protocols_dict


def _get_sc_messaging_protocol_dict(search_dict, protocol):
    messaging_protocols_dict = _get_sc_messaging_protocols_dict(search_dict)
    protocol_dict = _find_nested_dict(messaging_protocols_dict, field="name", value=protocol)
    if protocol_dict is None:
        protocol_dict = dict(
            enabled=False
        )
    else:
        protocol_dict['enabled'] = True
    return protocol_dict


def _get_sc_messaging_protocols_smf_dict(search_dict):
    messaging_protocols_dict = _get_sc_messaging_protocols_dict(search_dict)
    search_value = 'SMF'
    smf_dict = _find_nested_dict(messaging_protocols_dict, field="name", value=search_value)
    if smf_dict is None:
        raise AnsibleError("Could not find 'name={}' in messaging protocols in Solace Cloud service ansible_facts. Check if it is enabled.".format(search_value))
    return smf_dict


def _get_sc_messaging_protocol_endpoint(search_dict, field, value):
    element = 'endPoints'
    if element not in search_dict:
        raise AnsibleError("Could not find '{}' in dict:{} messaging protocols in Solace Cloud service ansible_facts. API may have changed. Pls raise an issue.".format(element, json.dumps(search_dict)))
    end_points = search_dict[element]
    if len(end_points) == 0:
        raise AnsibleError("List:'{}' in dict:{} in Solace Cloud service ansible_facts. API may have changed. Pls raise an issue.".format(element, json.dumps(search_dict)))
    end_point_dict = _find_nested_dict(end_points, field, value)
    # endPoint may not be enabled
    # if end_point_dict is None:
    #     # might not be enabled
    #     raise AnsibleError("Could not find messaging protocol end point with '{}={}' in Solace Cloud service ansible_facts. Check if it is enabled.".format(field, value))
    return end_point_dict


def _get_sc_messaging_protocol_endpoint_uri(search_dict):
    element = 'uris'
    if element not in search_dict:
        errs = [
            "Could not find '{}' in messaging protocol end point:".format(element),
            search_dict,
            "in Solace Cloud service ansible_facts."
        ]
        return dict()
        # raise AnsibleError(json.dumps(errs))
    if len(search_dict['uris']) != 1:
        errs = [
            "'{}' list contains != 1 elements in messaging protocol end point:".format(element),
            "{}".format(json.dumps(search_dict)),
            "in Solace Cloud service ansible_facts. API may have changed. Pls raise an issue.",
        ]
        raise AnsibleError(errs)
    return search_dict['uris'][0]


def _get_port_from_uri(uri):
    t = urlparse(uri)
    return t.port


def _find_nested_dict(search_dict, field, value):
    if isinstance(search_dict, dict):
        if field in search_dict and search_dict[field] == value:
            return search_dict
        for key in search_dict:
            item = _find_nested_dict(search_dict[key], field, value)
            if item is not None:
                return item
    elif isinstance(search_dict, list):
        for element in search_dict:
            item = _find_nested_dict(element, field, value)
            if item is not None:
                return item
    return None


def _get_field(search_dict, field):
    if isinstance(search_dict, dict):
        if field in search_dict:
            return search_dict[field]
        for key in search_dict:
            item = _get_field(search_dict[key], field)
            if item is not None:
                return item
    elif isinstance(search_dict, list):
        for element in search_dict:
            item = _get_field(element, field)
            if item is not None:
                return item
    return None


def run_module():
    module_args = dict(
        hostvars=dict(type='dict', required=True),
        host=dict(type='str', required=True),
        fields=dict(type='list', required=False, default=[], elements='str'),
        field_funcs=dict(type='list', required=False, default=[], elements='str'),
        msg_vpn=dict(type='str', required=False, default=None)
    )
    arg_spec = dict()
    # TODO: check if we need the msg_vpn with multi-vpn brokers
    # arg_spec = su.arg_spec_vpn()
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        facts=dict(),
        rc=0
    )

    solace_task = SolaceGetFactsTask(module)
    try:
        ok, resp = solace_task.get_facts()
        if not ok:
            result['rc'] = 1
            module.fail_json(msg=resp, **result)
    except AnsibleError as e:
        ex = traceback.format_exc()
        try:
            ex_msg = json.loads(str(e))
        except JSONDecodeError:
            ex_msg = [str(e)]
        msg = ["Pls raise an issue including the full traceback. (hint: use -vvv)"] + ex_msg + ex.split('\n')
        module.fail_json(msg=msg, exception=ex)

    result['facts'] = resp
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
