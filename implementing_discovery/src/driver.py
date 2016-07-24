from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails


class ImplementingDiscoveryDriver (ResourceDriverInterface):

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass


    # When the auto load function is triggered, CloudShell will call the get_inventory function
    # The function should discover the resource hierarchy and return back to CloudShell an instance of AutoLoadDetails
    # which includes details about the resource hierarchy and attributes
    def get_inventory(self, context):
        """
        :type context: drivercontext.AutoLoadCommandContext
        """
        # Add sub resources details
        sub_resources = [ AutoLoadResource(model ='Generic Chassis',name= 'Chassis 1', address='1'),
          AutoLoadResource(model='Generic Module',name= 'Module 1',address= '1/1'),
          AutoLoadResource(model='Generic Port',name= 'Port 1', address='1/1/1'),
          AutoLoadResource(model='Generic Port', name='Port 2', address='1/1/2'),
          AutoLoadResource(model='Generic Power Port', name='Power Port', address='1/PP1')]


        attributes = [ AutoLoadAttribute(relative_address='', attribute_name='Location', attribute_value='Santa Clara Lab'),
                       AutoLoadAttribute('', 'Model', 'Catalyst 3850'),
                       AutoLoadAttribute('', 'Vendor', 'Cisco'),
                       AutoLoadAttribute('1', 'Serial Number', 'JAE053002JD'),
                       AutoLoadAttribute('1', 'Model', 'WS-X4232-GB-RJ'),
                       AutoLoadAttribute('1/1', 'Model', 'WS-X4233-GB-EJ'),
                       AutoLoadAttribute('1/1', 'Serial Number', 'RVE056702UD'),
                       AutoLoadAttribute('1/1/1', 'Mac_Address', 'fe80::e10c:f055:f7f1:bb7t16'),
                       AutoLoadAttribute('1/1/1', 'IPv4 Address', '192.168.10.7'),
                       AutoLoadAttribute('1/1/2', 'Mac_Address', 'te67::e40c:g755:f55y:gh7w36'),
                       AutoLoadAttribute('1/1/2', 'IPv4 Address', '192.168.10.9'),
                       AutoLoadAttribute('1/PP1', 'Model', 'WS-X4232-GB-RJ'),
                       AutoLoadAttribute('1/PP1', 'Port Description', 'Power'),
                       AutoLoadAttribute('1/PP1', 'Serial Number', 'RVE056702UD')]

        result = AutoLoadDetails(sub_resources,attributes)
        return result