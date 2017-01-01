import datetime
import json


from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext


from data_model import *

class ImplementingDiscoveryDriver (ResourceDriverInterface):


    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """

        resource = ImplementingDiscovery.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'

        chassis1 = GenericChassis('Chassis 1')
        chassis1.model = 'WS-X4232-GB-RJ'
        chassis1.serial_number = 'JAE053002JD'
        resource.add_sub_resource('1', chassis1)

        module1 = GenericModule('Module 1')
        module1.model = 'WS-X5561-GB-AB'
        module1.serial_number = 'TGA053972JD'
        chassis1.add_sub_resource('1', module1)

        port1 = GenericPort('Port 1')
        port1.mac_address = 'fe80::e10c:f055:f7f1:bb7t16'
        port1.ipv4_address = '192.168.10.7'
        module1.add_sub_resource('1', port1)

        return resource.create_autoload_details()
