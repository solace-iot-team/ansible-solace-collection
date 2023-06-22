# solace_cloud_inventory.py

# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
  name: solace_cloud_inventory.py
  author: Ulrich Herbst <ulrich.herbst@solace.com>
  version_added: "0.1"  # for collections, use the collection version, not the Ansible version FIXME
  short_description: Get all services from a Solace Cloud org and return as ansible inventory
  description: Get all services from a Solace Cloud org and return as ansible inventory
  options:
    plugin:
        description: name of plugin.
        required: true
        choices: ['solace.pubsub_plus.solace_cloud_inventory']
    solace_cloud_api_token:
        description: A token to identiy by Solace cloud. You can get your tokens in Solace cloud console.
        required: True
        env:
          - name: SOLACE_CLOUD_TOKEN
    solace_cloud_home:
        description: Location of Solace cloud home base
        default: us
    service_filter:
       description: If given, then all service_names will filtered with that regex
'''

import requests,re, urllib
from pprint import pformat, pprint

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError

class InventoryModule(BaseInventoryPlugin):

    NAME = 'solace.pubsub_plus.solace_cloud_inventory'

    def verify_file(self, path):
        '''Return true/false if this is possibly a valid file for solace_cloud_inventory. A token is absolutely necessary

        '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('.yaml', '.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        self._read_config_data(path)
        self.token          = self.get_option('solace_cloud_api_token')
        self.homecloud      = self.get_option('solace_cloud_home')
        self.service_filter = self.get_option('service_filter')
        self.debug=False
        
        self._generate_inventory(self.token,self.homecloud, self.debug)


    def _get_service_list(self, token, debug):
        "query Solace Cloud API to get a list of all services in this environment"

        solace_cloud_base_url     = 'https://api.solace.cloud/api/v0'
        solace_cloud_auth_headers = {'Authorization' : f'Bearer {token}'}

        try:
            servicelist=requests.get(f'{solace_cloud_base_url}/services',
                                     headers = solace_cloud_auth_headers)
            servicelist.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Unexpected HTTP response from server:")
            print(str(e))            
        except requests.ConnectionError as e:
            print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
            print(str(e))
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
        except KeyboardInterrupt:
            print("Someone closed the program")
            
        if debug:
            print(
                f'Services-List from Cloud-API:\n'
                f'{pformat(servicelist.json())}'
            )
              
        return servicelist.json()['data']


    def _get_service_detail(self, serviceId, token, debug):
        "query Solace Cloud API to get details for a specific a list of all services in this environment"

        solace_cloud_base_url     = 'https://api.solace.cloud/api/v0'
        solace_cloud_auth_headers = {'Authorization' : f'Bearer {token}'}

        try:
            service_detail=requests.get(f'{solace_cloud_base_url}/services/{serviceId}',
                                        headers = solace_cloud_auth_headers)
            service_detail.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Unexpected HTTP response from server:")
            print(str(e))            
        except requests.ConnectionError as e:
            print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
            print(str(e))
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
        except KeyboardInterrupt:
            print("Someone closed the program")
            
        if debug:
            print(
                f'Service Details for {serviceId}:\n'
                f'{pformat(service_detail.json())}'
            )

        return service_detail.json()['data']

    def _create_pod_name(self,routername):
        "translate the routername into a pod name"

        # Input:  kiloproductioniiclitmopwysolaceprimary0
        # Output: kilo-production-iiclitmopwy-solace-primary-0

        # <size> - 'production' - <serviceID> - 'solace' - '<primary|backup|monitor>' - <number>

        m=re.fullmatch(r"(?P<sizing>.*)production(?P<serviceid>.*)solace(?P<node>primary|backup|monitor)(?P<counter>\d+)", routername)
        if m:
            return f"{m['sizing']}-production-{m['serviceid']}-solace-{m['node']}-{m['counter']}"
        else:
            return routername
        

    def _generate_inventory(self, token,homecloud, debug):
        
        for service in self._get_service_list(token, debug):
            service_name   = service['name']

            if self.service_filter and not re.search(self.service_filter, service_name):
                continue

            serviceId      = service['serviceId']
            service_detail = self._get_service_detail(serviceId, token, debug)

            self.inventory.add_host(host=service_name)
            self.inventory.set_variable(service_name, 'ansible_connection', 'local')
            self.inventory.set_variable(service_name, 'broker_type', 'solace_cloud')
            self.inventory.set_variable(service_name, 'sempv2_username', service_detail['msgVpnAttributes']['vpnAdminUsername'])
            self.inventory.set_variable(service_name, 'sempv2_password', service_detail['msgVpnAttributes']['vpnAdminPassword'])
            self.inventory.set_variable(service_name, 'sempv2_timeout', '60' )
            self.inventory.set_variable(service_name, 'solace_cloud_service_id', service_detail['serviceId'] )
            self.inventory.set_variable(service_name, 'solace_cloud_api_token', token)
            self.inventory.set_variable(service_name, 'virtual_router', 'primary' )
            self.inventory.set_variable(service_name, 'vpn', service_detail['msgVpnName'])
            self.inventory.set_variable(service_name, 'podname_primary', self._create_pod_name(service_detail['cluster']['primaryRouterName']))
            self.inventory.set_variable(service_name, 'podname_backup', self._create_pod_name(service_detail['cluster']['backupRouterName']))
            self.inventory.set_variable(service_name, 'podname_monitor', self._create_pod_name(service_detail['cluster']['monitoringRouterName']))
            self.inventory.set_variable(service_name, 'clusterName', service_detail['cluster']['name'])
            self.inventory.set_variable(service_name, 'clusterPassword', service_detail['cluster']['password'])

            # To get the SEMPv2 URI from the service_details is a bit complex:
            # in managementProtocols, there are multiple entries, one of it with the same "SolAdmin"
            # (for those known to Solace products for years... the name has historical reasons).
            # THe SolAdmin-entry has multiple endpoints defined, one of those with the name "Secured Management"
            endpoints=[mp for mp in service_detail['managementProtocols'] if mp['name']=='SolAdmin'][0]['endPoints']
            uri=[ep for ep in endpoints if ep['name'] == 'Secured Management'][0]['uris'][0]
            parsed_uri=urllib.parse.urlparse(uri)
            self.inventory.set_variable(service_name, 'sempv2_host', parsed_uri.hostname )
            self.inventory.set_variable(service_name, 'sempv2_port', parsed_uri.port)
            self.inventory.set_variable(service_name, 'sempv2_is_secure_connection', True )
