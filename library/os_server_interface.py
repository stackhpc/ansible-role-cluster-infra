#!/usr/bin/env python
#
# Copyright (c) 2018 StackHPC Ltd.
# Apache 2 Licence

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: os_server_interface
short_description: Create, update and delete server interface.
author: bharat@stackhpc.com
version_added: "1.0"
description:
    -  Create, update and delete server interface using Openstack Nova API.
notes:
    - This module returns C(network_interface) fact, which
      contains information about server network interfaces.
requirements:
    - "python >= 2.6"
    - "openstacksdk"
    - "python-novaclient"
options:
   cloud:
     description:
       - Cloud name inside cloud.yaml file.
     type: str
   state:
     description:
       - Must be `present`, `query` or `absent`.
     type: str
   server_id:
     description:
        - Server name or uuid.
     type: str
   interfaces:
     description:
        - List of network interface names.
     type: list of str
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Attach interfaces to <server_id>:
- os_container_infra:
    cloud: mycloud
    state: present
    server_id: xxxxx-xxxxx-xxxx-xxxx
    interfaces:
    - p3-lln
    - p3-bdn
  register: result
- debug:
    var: result
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.utils.display import Display
from novaclient.client import Client
from novaclient.exceptions import NotFound
import openstack
import time

class OpenStackAuthConfig(Exception):
    pass

class ServerInterface(object):
    def __init__(self, **kwargs):
        self.server_id = kwargs['server_id']
        self.state = kwargs['state']
    
        self.connect(**kwargs)
        self.interfaces = []
        for interface in kwargs['interfaces']:
            network = self.cloud.network.find_network(interface)
            if not network:
                raise Exception("Unable to find network '%s'" % interface)
            self.interfaces.append(network)

    def connect(self, **kwargs):
        if kwargs['auth_type'] == 'password':
            if kwargs['cloud']:
                self.cloud = openstack.connect(cloud=kwargs['cloud'])
            elif kwargs['auth']:
                self.cloud = openstack.connect(**kwargs['auth'])
            else:
                self.cloud = openstack.connect()
        else:
            raise OpenStackAuthConfig('Only `password` auth_type is supported.')
        self.cloud.authorize()
        self.client = Client('2', session=self.cloud.session)

    def get_server(self):
        try:
            server = self.client.servers.find(id=self.server_id)
        except NotFound:
            server = self.client.servers.find(name=self.server_id)
        return server

    def apply(self):
        changed = False
        self.server = server = self.get_server()
        if self.state != 'query':
            attached_interfaces = server.interface_list()
            for interface in self.interfaces:
                interface_exists = False
                for attached_interface in attached_interfaces:
                    if interface.id == attached_interface.net_id:
                        if self.state == 'absent':
                            server.interface_detach(port_id=attached_interface.port_id)
                            changed = True
                        elif self.state == 'present':
                            interface_exists = True
                if interface_exists == False and self.state == 'present':
                    server.interface_attach(port_id=None, net_id=interface.id, fixed_ip=None)
                    changed = True
            if changed:
                self.server = self.get_server()
        return changed

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec = dict(
            cloud=dict(required=False, type='str'),
            auth=dict(required=False, type='dict'),
            auth_type=dict(default='password', required=False, type='str'),
            state=dict(default='present', choices=['present','absent', 'query']),
            server_id=dict(required=True, type='str'),
            interfaces=dict(default=[], type='list'),
        ),
        supports_check_mode=False
    )

    display = Display()

    try:
        server_interface = ServerInterface(**module.params)
        changed = server_interface.apply()
    except Exception as e:
        module.fail_json(msg=repr(e))

    server = server_interface.server

    module.exit_json(
        changed=changed,
        server_name=server.name,
        server_networks=server.networks,
    )
