# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceInternalErrorAbstractMethod, SolaceApiError, SolaceInternalError, SolaceFeatureNotSupportedError, SolaceModuleUsageError
import json
import logging
from urllib.parse import urlparse


class SingleConnectionDetails(object):
    def __init__(self):
        self.enabled = False
        self.uri = None
        self.uri_components = None

    def set_enabled(self, value: bool):
        self.enabled = value

    def set_uri(self, uri: str):
        uri_components = urlparse(uri)
        self.uri = uri
        self.uri_components = {
            "protocol": uri_components.scheme,
            "host": uri_components.hostname,
            "port": uri_components.port
        }

    def set_uri_protocol(self, protocol: str):
        if not self.uri_components:
            self.uri_components = {}
        self.uri_components['protocol'] = protocol

    def set_uri_host(self, host: str):
        if not self.uri_components:
            self.uri_components = {}
        self.uri_components['host'] = host

    def set_uri_port(self, port: int):
        if not self.uri_components:
            self.uri_components = {}
        self.uri_components['port'] = port

    def get(self) -> dict:
        return {
            "enabled": self.enabled,
            "uri": self.uri,
            "uri_components": self.uri_components
        }


class ProtocolConnectionDetails(object):
    def __init__(self):
        self.enabled = False
        self.authentication = None
        self.plain = None
        self.secured = None
        self.compressed = None
        self.ws_plain = None
        self.ws_secured = None

    def set_enabled(self, value: bool):
        self.enabled = value

    def set_authentication(self, username: str, password: str):
        self.authentication = {
            "username": username,
            "password": password
        }

    def set_plain(self, connectionDetails: SingleConnectionDetails):
        self.plain = connectionDetails

    def set_ws_plain(self, connectionDetails: SingleConnectionDetails):
        self.ws_plain = connectionDetails

    def set_secured(self, connectionDetails: SingleConnectionDetails):
        self.secured = connectionDetails

    def set_ws_secured(self, connectionDetails: SingleConnectionDetails):
        self.ws_secured = connectionDetails

    def set_compressed(self, connectionDetails: SingleConnectionDetails):
        self.compressed = connectionDetails

    def get(self) -> dict:
        return {
            "enabled": self.enabled,
            "authentication": self.authentication,
            "plain": self.plain.get() if self.plain else None,
            "ws_plain": self.ws_plain.get() if self.ws_plain else None,
            "secured": self.secured.get() if self.secured else None,
            "ws_secured": self.ws_secured.get() if self.ws_secured else None,
            "compressed": self.compressed.get() if self.compressed else None
        }


class SolaceBrokerFacts(object):
    def __init__(self, module_name: str, input_dict: dict, vpn: str):
        self.module_name = module_name
        self.input_dict = input_dict
        self.msg_vpn = vpn

    @staticmethod
    def get_field(search_object, field: str):
        if isinstance(search_object, dict):
            if field in search_object:
                return search_object[field]
            for key in search_object:
                item = SolaceBrokerFacts.get_field(search_object[key], field)
                if item:
                    return item
        elif isinstance(search_object, list):
            for element in search_object:
                item = SolaceBrokerFacts.get_field(element, field)
                if item:
                    return item
        return None

    @staticmethod
    def get_nested_dict(search_object, field: str, value: str) -> dict:
        if isinstance(search_object, dict):
            if field in search_object and search_object[field] == value:
                return search_object
            for key in search_object:
                item = SolaceBrokerFacts.get_nested_dict(
                    search_object[key], field, value)
                if item:
                    return item
        elif isinstance(search_object, list):
            for element in search_object:
                item = SolaceBrokerFacts.get_nested_dict(element, field, value)
                if item:
                    return item
        return None

    def _get_broker_mgmt_type(self) -> str:
        raise SolaceInternalErrorAbstractMethod()

    def _extract_formatted_virtual_router_name(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_virtual_router_name(self) -> dict:
        return self._extract_formatted_virtual_router_name()

    def _extract_formatted_bridge_remote_msg_vpn_locations(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_bridge_remote_msg_vpn_locations(self) -> dict:
        return self._extract_formatted_bridge_remote_msg_vpn_locations()

    def _extract_formatted_dmr_cluster_connection_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_dmr_cluster_connection_details(self) -> dict:
        return self._extract_formatted_dmr_cluster_connection_details()

    def _extract_formatted_msg_vpn_attributes(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_msg_vpn_attributes(self) -> dict:
        return self._extract_formatted_msg_vpn_attributes()

    def _extract_formatted_trust_store_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_trust_store_details(self) -> dict:
        return self._extract_formatted_trust_store_details()

    def _extract_formatted_amqp_client_connection_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_amqp_client_connection_details(self) -> dict:
        return self._extract_formatted_amqp_client_connection_details()

    def _extract_formatted_jms_client_connection_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_jms_client_connection_details(self) -> dict:
        return self._extract_formatted_jms_client_connection_details()

    def _extract_formatted_mqtt_client_connection_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_mqtt_client_connection_details(self) -> dict:
        return self._extract_formatted_mqtt_client_connection_details()

    def _extract_formatted_rest_client_connection_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_rest_client_connection_details(self) -> dict:
        return self._extract_formatted_rest_client_connection_details()

    def _extract_formatted_semp_client_connection_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_semp_client_connection_details(self) -> dict:
        return self._extract_formatted_semp_client_connection_details()

    def _extract_formatted_smf_client_connection_details(self) -> dict:
        raise SolaceInternalErrorAbstractMethod()

    def get_smf_client_connection_details(self) -> dict:
        return self._extract_formatted_smf_client_connection_details()

    def get_all_client_connection_details(self) -> dict:
        res = {
            "brokerMgmtType": self._get_broker_mgmt_type(),
            "msgVpn": self.msg_vpn,
            "trustStore": self.get_trust_store_details(),
            "AMQP": self.get_amqp_client_connection_details(),
            "MQTT": self.get_mqtt_client_connection_details(),
            "REST": self.get_rest_client_connection_details(),
            "SMF": self.get_smf_client_connection_details(),
            "JMS": self.get_jms_client_connection_details()
        }
        return res


class SolaceCloudBrokerFacts(SolaceBrokerFacts):
    def __init__(self, module_name: str, input_dict: dict, vpn: str):
        super().__init__(module_name, input_dict, vpn)
        self.messaging_protocols = None

    def _get_broker_mgmt_type(self) -> str:
        return "solace_cloud"

    def _extract_formatted_msg_vpn_attributes(self) -> dict:
        msg_vpn_attributes = SolaceBrokerFacts.get_field(
            self.input_dict, 'msgVpnAttributes')
        formatted_res = {
            'msgVpn': msg_vpn_attributes['vpnName']
        }
        return formatted_res

    def _extract_formatted_dmr_cluster_connection_details(self) -> dict:
        # Note: this probably needs refinement
        cluster_details = SolaceBrokerFacts.get_field(
            self.input_dict, 'cluster')
        formatted_res = {
            "clusterName": cluster_details['name'],
            "password": cluster_details['password'],
            "remoteAddress": cluster_details['remoteAddress'],
            "primaryRouterName": cluster_details['primaryRouterName']
        }
        return formatted_res

    def _extract_formatted_virtual_router_name(self) -> dict:
        return SolaceBrokerFacts.get_field(self.input_dict, "primaryRouterName")

    def _extract_formatted_bridge_remote_msg_vpn_locations(self) -> dict:
        smf_client_connection_details = self.get_smf_client_connection_details()
        formatted_res = {
            "enabled": False,
            "plain": None,
            "compressed": None,
            "secured": None
        }
        if not smf_client_connection_details['enabled']:
            return formatted_res
        else:
            formatted_res['enabled'] = True
        if smf_client_connection_details['plain']['enabled']:
            formatted_res.update({
                "plain": smf_client_connection_details['plain']['uri_components']['host'] + ":" + str(smf_client_connection_details['plain']['uri_components']['port'])
            })
        if smf_client_connection_details['compressed']['enabled']:
            formatted_res.update({
                "compressed": smf_client_connection_details['compressed']['uri_components']['host'] + ":" + str(smf_client_connection_details['compressed']['uri_components']['port'])
            })
        if smf_client_connection_details['secured']['enabled']:
            formatted_res.update({
                "secured": smf_client_connection_details['secured']['uri_components']['host'] + ":" + str(smf_client_connection_details['secured']['uri_components']['port'])
            })
        return formatted_res

    def _extract_msg_vpn_attributes(self) -> dict:
        vpn_attributes = SolaceBrokerFacts.get_field(
            self.input_dict, "msgVpnAttributes")
        if not vpn_attributes:
            raise SolaceInternalError(
                "Could not find 'msgVpnAttributes' in 'ansible_facts.solace'. API may have changed.")
        return vpn_attributes

    def _extract_messaging_protocols(self) -> dict:
        if self.messaging_protocols:
            return self.messaging_protocols
        mps = self.get_field(self.input_dict, "messagingProtocols")
        if not mps:
            raise SolaceInternalError(
                "Could not find 'messagingProtocols' in 'ansible_facts.solace'. API may have changed.")
        self.messaging_protocols = mps
        return self.messaging_protocols

    def _extract_messaging_protocol(self, protocol: str) -> dict:
        protocol_dict = self.get_nested_dict(
            self._extract_messaging_protocols(), field="name", value=protocol)
        if not protocol_dict:
            protocol_dict = dict(
                enabled=False
            )
        else:
            protocol_dict['enabled'] = True
        return protocol_dict

    def _extract_formatted_trust_store_details(self) -> dict:
        vpn_attributes = self._extract_msg_vpn_attributes()
        return {
            "enabled": True,
            "uri": vpn_attributes['truststoreUri']
        }

    def _extract_formatted_protocol_client_connection_details(self, protocol: str, plain: str, secured: str, compressed: str) -> dict:
        input_dict = self._extract_messaging_protocol(protocol)
        res = ProtocolConnectionDetails()
        if not input_dict['enabled']:
            return res.get()
        # plain
        res_plain = SingleConnectionDetails()
        plainText_dict = self.get_nested_dict(
            input_dict['endPoints'], field="name", value=plain)
        # logging.debug(f"plainText_dict=\n{json.dumps(plainText_dict, indent=2)}")
        if plainText_dict:
            res_plain.set_enabled(True)
            res_plain.set_uri(plainText_dict['uris'][0])
        # tls
        res_secured = SingleConnectionDetails()
        secured_dict = self.get_nested_dict(
            input_dict, field="name", value=secured)
        if secured_dict:
            res_secured.set_enabled(True)
            res_secured.set_uri(secured_dict['uris'][0])
        # compressed
        res_compressed = SingleConnectionDetails()
        compressed_dict = self.get_nested_dict(
            input_dict, field="name", value=compressed)
        if compressed_dict:
            res_compressed.set_enabled(True)
            res_compressed.set_uri(compressed_dict['uris'][0])
        res.set_enabled(True)
        res.set_authentication(input_dict['username'], input_dict['password'])
        res.set_plain(res_plain)
        res.set_secured(res_secured)
        res.set_compressed(res_compressed)
        return res.get()

    def _extract_formatted_amqp_client_connection_details(self) -> dict:
        return self._extract_formatted_protocol_client_connection_details(protocol="AMQP", plain="AMQP", secured="Secured AMQP", compressed=None)

    def _extract_formatted_jms_client_connection_details(self) -> dict:
        return self._extract_formatted_protocol_client_connection_details(protocol="JMS", plain="JMS", secured="Secured JMS", compressed=None)

    def _extract_formatted_mqtt_client_connection_details(self) -> dict:
        return self._extract_formatted_protocol_client_connection_details(protocol="MQTT", plain="MQTT", secured="Secured MQTT", compressed=None)

    def _extract_formatted_rest_client_connection_details(self) -> dict:
        return self._extract_formatted_protocol_client_connection_details(protocol="REST", plain="REST", secured="Secured REST", compressed=None)

    def _extract_formatted_semp_client_connection_details(self) -> dict:
        mgmt_protocols = self.get_field(self.input_dict, "managementProtocols")
        semp_protocol = self.get_nested_dict(
            mgmt_protocols, field='name', value='SEMP')
        username = semp_protocol['username']
        password = semp_protocol['password']
        secured_semp_endpoint = self.get_nested_dict(
            semp_protocol['endPoints'], field='name', value='Secured SEMP Config')
        res_secured = SingleConnectionDetails()
        res_secured.set_enabled(True)
        res_secured.set_uri(secured_semp_endpoint['uris'][0])
        res = ProtocolConnectionDetails()
        res.set_enabled(True)
        res.set_secured(res_secured)
        res.set_authentication(username, password)
        return res.get()

    def _extract_formatted_smf_client_connection_details(self) -> dict:
        return self._extract_formatted_protocol_client_connection_details(protocol="SMF", plain="SMF", secured="Secured SMF", compressed="Compressed SMF")


class SolaceSelfHostedBrokerFacts(SolaceBrokerFacts):
    def __init__(self, module_name: str, input_dict: dict, vpn: str):
        super().__init__(module_name, input_dict, vpn)

    def _get_broker_mgmt_type(self) -> str:
        return "self_hosted"

    def _extract_formatted_trust_store_details(self) -> dict:
        return {
            "enabled": False,
            "details": "not implemented"
        }

    def _extract_formatted_msg_vpn_attributes(self) -> dict:
        vpn_dict = self.input_dict['vpns'][self.msg_vpn]
        formatted_res = {
            # may need more attributes in future
            'msgVpn': vpn_dict['msgVpnName']
        }
        return formatted_res

    def _extract_formatted_dmr_cluster_connection_details(self) -> dict:
        raise SolaceFeatureNotSupportedError(
            f"extract dmr cluster connection details for broker-type={self._get_broker_mgmt_type()}")

    def _extract_formatted_virtual_router_name(self) -> dict:
        value = SolaceBrokerFacts.get_field(self.input_dict,
                                            "virtualRouterName")
        if not value:
            msg = [
                "'virtualRouterName' not found in solace facts",
                "hint: use sempv1 in solace_gather_facts"
            ]
            raise SolaceModuleUsageError(self.module_name, 'n/a', msg)
        return value

    def _extract_formatted_amqp_client_connection_details(self) -> dict:
        vpn_dict = self.input_dict['vpns'][self.msg_vpn]
        is_enabled = vpn_dict['serviceAmqpPlainTextEnabled'] or vpn_dict['serviceAmqpTlsEnabled']
        res = ProtocolConnectionDetails()
        if not is_enabled:
            return res.get()
        res_plain = SingleConnectionDetails()
        res_plain.set_enabled(vpn_dict['serviceAmqpPlainTextEnabled'])
        res_plain.set_uri_port(vpn_dict['serviceAmqpPlainTextListenPort'])
        res_secured = SingleConnectionDetails()
        res_secured.set_enabled(vpn_dict['serviceAmqpTlsEnabled'])
        res_secured.set_uri_port(vpn_dict['serviceAmqpTlsListenPort'])

        res.set_enabled(True)
        res.set_plain(res_plain)
        res.set_secured(res_secured)
        return res.get()

    def _extract_formatted_jms_client_connection_details(self) -> dict:
        res = self._extract_formatted_smf_client_connection_details()
        res['ws_plain'] = None
        res['ws_secured'] = None
        return res

    def _extract_formatted_mqtt_client_connection_details(self) -> dict:
        vpn_dict = self.input_dict['vpns'][self.msg_vpn]
        is_enabled = vpn_dict['serviceMqttPlainTextEnabled'] or vpn_dict['serviceMqttTlsEnabled'] or vpn_dict[
            'serviceMqttTlsWebSocketEnabled'] or vpn_dict['serviceMqttWebSocketEnabled']
        res = ProtocolConnectionDetails()
        if not is_enabled:
            return res.get()
        res_plain = SingleConnectionDetails()
        res_plain.set_enabled(vpn_dict['serviceMqttPlainTextEnabled'])
        res_plain.set_uri_port(vpn_dict['serviceMqttPlainTextListenPort'])
        res_ws_plain = SingleConnectionDetails()
        res_ws_plain.set_enabled(vpn_dict['serviceMqttWebSocketEnabled'])
        res_ws_plain.set_uri_port(vpn_dict['serviceMqttWebSocketListenPort'])
        res_secured = SingleConnectionDetails()
        res_secured.set_enabled(vpn_dict['serviceMqttTlsEnabled'])
        res_secured.set_uri_port(vpn_dict['serviceMqttTlsListenPort'])
        res_ws_secured = SingleConnectionDetails()
        res_ws_secured.set_enabled(vpn_dict['serviceMqttTlsWebSocketEnabled'])
        res_ws_secured.set_uri_port(
            vpn_dict['serviceMqttTlsWebSocketListenPort'])

        res.set_enabled(True)
        res.set_plain(res_plain)
        res.set_secured(res_secured)
        res.set_ws_plain(res_ws_plain)
        res.set_ws_secured(res_ws_secured)
        return res.get()

    def _extract_formatted_rest_client_connection_details(self) -> dict:
        vpn_dict = self.input_dict['vpns'][self.msg_vpn]
        is_enabled = vpn_dict['serviceRestIncomingPlainTextEnabled'] or vpn_dict['serviceRestIncomingTlsEnabled']
        res = ProtocolConnectionDetails()
        if not is_enabled:
            return res.get()
        res_plain = SingleConnectionDetails()
        res_plain.set_enabled(vpn_dict['serviceRestIncomingPlainTextEnabled'])
        res_plain.set_uri_port(
            vpn_dict['serviceRestIncomingPlainTextListenPort'])
        res_secured = SingleConnectionDetails()
        res_secured.set_enabled(vpn_dict['serviceRestIncomingTlsEnabled'])
        res_secured.set_uri_port(vpn_dict['serviceRestIncomingTlsListenPort'])

        res.set_enabled(True)
        res.set_plain(res_plain)
        res.set_secured(res_secured)
        return res.get()

    def _extract_formatted_smf_client_connection_details(self) -> dict:
        service_dict = self.input_dict['sempv2_service']
        is_enabled = service_dict['serviceSmfEnabled']
        res = ProtocolConnectionDetails()
        if not is_enabled:
            return res.get()

        res_plain = SingleConnectionDetails()
        res_plain.set_enabled(True)
        res_plain.set_uri_protocol('tcp')
        res_plain.set_uri_port(service_dict['serviceSmfPlainTextListenPort'])

        res_secured = SingleConnectionDetails()
        res_secured.set_enabled(True)
        res_secured.set_uri_protocol('tcps')
        res_secured.set_uri_port(service_dict['serviceSmfTlsListenPort'])

        res_compressed = SingleConnectionDetails()
        res_compressed.set_enabled(True)
        res_compressed.set_uri_protocol('tcp')
        res_compressed.set_uri_port(
            service_dict['serviceSmfCompressionListenPort'])

        # res_routing = SingleConnectionDetails()
        # res_routing.set_enabled(True)
        # res_routing.set_uri_protocol('tcp')
        # res_routing.set_uri_port(
        #     service_dict['serviceSmfRoutingControlListenPort'])

        res.set_enabled(True)
        res.set_plain(res_plain)
        res.set_secured(res_secured)
        res.set_compressed(res_compressed)
        return res.get()

    # def _extract_formatted_smf_client_connection_details(self) -> dict:
    #     vpn_dict = self.input_dict['vpns'][self.msg_vpn]
    #     service_dict = self.input_dict['service']['service']
    #     smf_service_dict = self.get_nested_dict(service_dict, 'name', 'SMF')
    #     web_service_dict = self.get_nested_dict(service_dict, 'name', 'WEB')
    #     is_compression_enabled = smf_service_dict['compression-listen-port-operational-status'] == "Up"
    #     is_ws_enabled = vpn_dict['serviceWebPlainTextEnabled'] or vpn_dict['serviceWebTlsEnabled']
    #     is_enabled = vpn_dict['serviceSmfPlainTextEnabled'] or vpn_dict['serviceSmfTlsEnabled'] or vpn_dict[
    #         'serviceWebPlainTextEnabled'] or vpn_dict['serviceWebTlsEnabled']
    #     is_enabled = is_enabled or is_compression_enabled or is_ws_enabled
    #     res = ProtocolConnectionDetails()
    #     if not is_enabled:
    #         return res.get()
    #     res_plain = SingleConnectionDetails()
    #     res_plain.set_enabled(vpn_dict['serviceSmfPlainTextEnabled'])
    #     res_plain.set_uri_port(int(smf_service_dict['listen-port']))
    #     res_ws_plain = SingleConnectionDetails()
    #     res_ws_plain.set_enabled(vpn_dict['serviceWebPlainTextEnabled'])
    #     res_ws_plain.set_uri_port(web_service_dict['listen-port'])
    #     res_secured = SingleConnectionDetails()
    #     res_secured.set_enabled(vpn_dict['serviceSmfTlsEnabled'])
    #     res_secured.set_uri_port(int(smf_service_dict['ssl']['listen-port']))
    #     res_ws_secured = SingleConnectionDetails()
    #     res_ws_secured.set_enabled(vpn_dict['serviceWebTlsEnabled'])
    #     res_ws_secured.set_uri_port(
    #         int(web_service_dict['ssl']['listen-port']))
    #     res_compressed = SingleConnectionDetails()
    #     res_compressed.set_enabled(is_compression_enabled)
    #     res_compressed.set_uri_port(
    #         int(smf_service_dict['compression-listen-port']))

    #     res.set_enabled(True)
    #     res.set_plain(res_plain)
    #     res.set_secured(res_secured)
    #     res.set_ws_plain(res_ws_plain)
    #     res.set_ws_secured(res_ws_secured)
    #     res.set_compressed(res_compressed)
    #     return res.get()

    def _extract_formatted_bridge_remote_msg_vpn_locations(self) -> dict:
        virtual_router = "v:" + self._extract_formatted_virtual_router_name()
        smf_client_connection_details = self.get_smf_client_connection_details()
        formatted_res = {
            "enabled": False,
            "plain": None,
            "compressed": None,
            "secured": None
        }
        if not smf_client_connection_details['enabled']:
            return formatted_res
        else:
            formatted_res['enabled'] = True
        if smf_client_connection_details['plain']['enabled']:
            formatted_res.update({
                "plain": virtual_router
            })
        if smf_client_connection_details['compressed']['enabled']:
            formatted_res.update({
                "compressed": virtual_router
            })
        if smf_client_connection_details['secured']['enabled']:
            formatted_res.update({
                "secured": virtual_router
            })
        return formatted_res
