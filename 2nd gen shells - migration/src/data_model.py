from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadDetails, AutoLoadAttribute, \
    AutoLoadResource
from collections import defaultdict


class LegacyUtils(object):
    def __init__(self):
        self._datamodel_clss_dict = self.__generate_datamodel_classes_dict()

    def migrate_autoload_details(self, autoload_details, context):
        model_name = context.resource.model
        root_name = context.resource.name
        root = self.__create_resource_from_datamodel(model_name, root_name)
        attributes = self.__create_attributes_dict(autoload_details.attributes)
        self.__attach_attributes_to_resource(attributes, '', root)
        self.__build_sub_resoruces_hierarchy(root, autoload_details.resources, attributes)
        return root

    def __create_resource_from_datamodel(self, model_name, res_name):
        return self._datamodel_clss_dict[model_name](res_name)

    def __create_attributes_dict(self, attributes_lst):
        d = defaultdict(list)
        for attribute in attributes_lst:
            d[attribute.relative_address].append(attribute)
        return d

    def __build_sub_resoruces_hierarchy(self, root, sub_resources, attributes):
        d = defaultdict(list)
        for resource in sub_resources:
            splitted = resource.relative_address.split('/')
            parent = '' if len(splitted) == 1 else resource.relative_address.rsplit('/', 1)[0]
            rank = len(splitted)
            d[rank].append((parent, resource))

        self.__set_models_hierarchy_recursively(d, 1, root, '', attributes)

    def __set_models_hierarchy_recursively(self, dict, rank, manipulated_resource, resource_relative_addr, attributes):
        if rank not in dict: # validate if key exists
            pass

        for (parent, resource) in dict[rank]:
            if parent == resource_relative_addr:
                sub_resource = self.__create_resource_from_datamodel(
                    resource.model.replace(' ', ''),
                    resource.name)
                self.__attach_attributes_to_resource(attributes, resource.relative_address, sub_resource)
                manipulated_resource.add_sub_resource(
                    self.__slice_parent_from_relative_path(parent, resource.relative_address), sub_resource)
                self.__set_models_hierarchy_recursively(
                    dict,
                    rank + 1,
                    sub_resource,
                    resource.relative_address,
                    attributes)

    def __attach_attributes_to_resource(self, attributes, curr_relative_addr, resource):
        for attribute in attributes[curr_relative_addr]:
            setattr(resource, attribute.attribute_name.lower().replace(' ', '_'), attribute.attribute_value)
        del attributes[curr_relative_addr]

    def __slice_parent_from_relative_path(self, parent, relative_addr):
        if parent is '':
            return relative_addr
        return relative_addr[len(parent) + 1:] # + 1 because we want to remove the seperator also

    def __generate_datamodel_classes_dict(self):
        return dict(self.__collect_generated_classes())

    def __collect_generated_classes(self):
        import sys, inspect
        return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class MySwitchG2(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype MySwitchG2
        """
        result = MySwitchG2(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'MySwitchG2'

    @property
    def contact_name(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.Contact Name'] if 'MySwitchG2.Contact Name' in self.attributes else None

    @contact_name.setter
    def contact_name(self, value):
        """
        The name of a contact registered in the device.
        :type value: str
        """
        self.attributes['MySwitchG2.Contact Name'] = value

    @property
    def backup_location(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.Backup Location'] if 'MySwitchG2.Backup Location' in self.attributes else None

    @backup_location.setter
    def backup_location(self, value):
        """
        The location in which configuration files will be saved in case no backup location input is passed to the Save command.
        :type value: str
        """
        self.attributes['MySwitchG2.Backup Location'] = value

    @property
    def backup_type(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.Backup Type'] if 'MySwitchG2.Backup Type' in self.attributes else None

    @backup_type.setter
    def backup_type(self, value='File System'):
        """
        Supported protocols for saving and restoring of configuration and firmware files. Possible values are "File System", "FTP" and "TFTP". Default value is "File System"
        :type value: str
        """
        self.attributes['MySwitchG2.Backup Type'] = value

    @property
    def backup_user(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.Backup User'] if 'MySwitchG2.Backup User' in self.attributes else None

    @backup_user.setter
    def backup_user(self, value):
        """
        Username for the storage server used for saving and restoring of configuration and firmware files.
        :type value: str
        """
        self.attributes['MySwitchG2.Backup User'] = value

    @property
    def backup_password(self):
        """
        :rtype: string
        """
        return self.attributes['MySwitchG2.Backup Password'] if 'MySwitchG2.Backup Password' in self.attributes else None

    @backup_password.setter
    def backup_password(self, value):
        """
        Password for the storage server used for saving and restoring of configuration and firmware files.
        :type value: string
        """
        self.attributes['MySwitchG2.Backup Password'] = value

    @property
    def vrf_management_name(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.VRF Management Name'] if 'MySwitchG2.VRF Management Name' in self.attributes else None

    @vrf_management_name.setter
    def vrf_management_name(self, value):
        """
        The default VRF Management to use if configured in the network and no such input was passed to the Save or Restore command.
        :type value: str
        """
        self.attributes['MySwitchG2.VRF Management Name'] = value

    @property
    def user(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.User'] if 'MySwitchG2.User' in self.attributes else None

    @user.setter
    def user(self, value):
        """
        User with administrative privileges
        :type value: str
        """
        self.attributes['MySwitchG2.User'] = value

    @property
    def password(self):
        """
        :rtype: string
        """
        return self.attributes['MySwitchG2.Password'] if 'MySwitchG2.Password' in self.attributes else None

    @password.setter
    def password(self, value):
        """
        
        :type value: string
        """
        self.attributes['MySwitchG2.Password'] = value

    @property
    def enable_password(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.Enable Password'] if 'MySwitchG2.Enable Password' in self.attributes else None

    @enable_password.setter
    def enable_password(self, value):
        """
        The enable password is required by some CLI protocols such as Telnet and is required according to the device configuration.
        :type value: str
        """
        self.attributes['MySwitchG2.Enable Password'] = value

    @property
    def power_management(self):
        """
        :rtype: bool
        """
        return self.attributes['MySwitchG2.Power Management'] if 'MySwitchG2.Power Management' in self.attributes else None

    @power_management.setter
    def power_management(self, value):
        """
        Used by the power management orchestration, if enabled, to determine whether to automatically manage the device power status. Enabled by default.
        :type value: bool
        """
        self.attributes['MySwitchG2.Power Management'] = value

    @property
    def sessions_concurrency_limit(self):
        """
        :rtype: float
        """
        return self.attributes['MySwitchG2.Sessions Concurrency Limit'] if 'MySwitchG2.Sessions Concurrency Limit' in self.attributes else None

    @sessions_concurrency_limit.setter
    def sessions_concurrency_limit(self, value=1):
        """
        The maximum number of concurrent sessions that the driver will open to the device. Default is 1 (no concurrency).
        :type value: float
        """
        self.attributes['MySwitchG2.Sessions Concurrency Limit'] = value

    @property
    def snmp_read_community(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.SNMP Read Community'] if 'MySwitchG2.SNMP Read Community' in self.attributes else None

    @snmp_read_community.setter
    def snmp_read_community(self, value):
        """
        The SNMP Read-Only Community String is like a password. It is sent along with each SNMP Get-Request and allows (or denies) access to device.
        :type value: str
        """
        self.attributes['MySwitchG2.SNMP Read Community'] = value

    @property
    def snmp_write_community(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.SNMP Write Community'] if 'MySwitchG2.SNMP Write Community' in self.attributes else None

    @snmp_write_community.setter
    def snmp_write_community(self, value):
        """
        The SNMP Write Community String is like a password. It is sent along with each SNMP Set-Request and allows (or denies) chaning MIBs values.
        :type value: str
        """
        self.attributes['MySwitchG2.SNMP Write Community'] = value

    @property
    def snmp_v3_user(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.SNMP V3 User'] if 'MySwitchG2.SNMP V3 User' in self.attributes else None

    @snmp_v3_user.setter
    def snmp_v3_user(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['MySwitchG2.SNMP V3 User'] = value

    @property
    def snmp_v3_password(self):
        """
        :rtype: string
        """
        return self.attributes['MySwitchG2.SNMP V3 Password'] if 'MySwitchG2.SNMP V3 Password' in self.attributes else None

    @snmp_v3_password.setter
    def snmp_v3_password(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: string
        """
        self.attributes['MySwitchG2.SNMP V3 Password'] = value

    @property
    def snmp_v3_private_key(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.SNMP V3 Private Key'] if 'MySwitchG2.SNMP V3 Private Key' in self.attributes else None

    @snmp_v3_private_key.setter
    def snmp_v3_private_key(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['MySwitchG2.SNMP V3 Private Key'] = value

    @property
    def snmp_version(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.SNMP Version'] if 'MySwitchG2.SNMP Version' in self.attributes else None

    @snmp_version.setter
    def snmp_version(self, value=''):
        """
        The version of SNMP to use. Possible values are v1, v2c and v3.
        :type value: str
        """
        self.attributes['MySwitchG2.SNMP Version'] = value

    @property
    def enable_snmp(self):
        """
        :rtype: bool
        """
        return self.attributes['MySwitchG2.Enable SNMP'] if 'MySwitchG2.Enable SNMP' in self.attributes else None

    @enable_snmp.setter
    def enable_snmp(self, value=True):
        """
        If set to True and SNMP isn???t enabled yet in the device the Shell will automatically enable SNMP in the device when Autoload command is called. SNMP must be enabled on the device for the Autoload command to run successfully. True by default.
        :type value: bool
        """
        self.attributes['MySwitchG2.Enable SNMP'] = value

    @property
    def disable_snmp(self):
        """
        :rtype: bool
        """
        return self.attributes['MySwitchG2.Disable SNMP'] if 'MySwitchG2.Disable SNMP' in self.attributes else None

    @disable_snmp.setter
    def disable_snmp(self, value=False):
        """
        If set to True SNMP will be disabled automatically by the Shell after the Autoload command execution is completed. False by default.
        :type value: bool
        """
        self.attributes['MySwitchG2.Disable SNMP'] = value

    @property
    def console_server_ip_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.Console Server IP Address'] if 'MySwitchG2.Console Server IP Address' in self.attributes else None

    @console_server_ip_address.setter
    def console_server_ip_address(self, value):
        """
        The IP address of the console server, in IPv4 format.
        :type value: str
        """
        self.attributes['MySwitchG2.Console Server IP Address'] = value

    @property
    def console_user(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.Console User'] if 'MySwitchG2.Console User' in self.attributes else None

    @console_user.setter
    def console_user(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.Console User'] = value

    @property
    def console_port(self):
        """
        :rtype: float
        """
        return self.attributes['MySwitchG2.Console Port'] if 'MySwitchG2.Console Port' in self.attributes else None

    @console_port.setter
    def console_port(self, value):
        """
        The port on the console server, usually TCP port, which the device is associated with.
        :type value: float
        """
        self.attributes['MySwitchG2.Console Port'] = value

    @property
    def console_password(self):
        """
        :rtype: string
        """
        return self.attributes['MySwitchG2.Console Password'] if 'MySwitchG2.Console Password' in self.attributes else None

    @console_password.setter
    def console_password(self, value):
        """
        
        :type value: string
        """
        self.attributes['MySwitchG2.Console Password'] = value

    @property
    def cli_connection_type(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.CLI Connection Type'] if 'MySwitchG2.CLI Connection Type' in self.attributes else None

    @cli_connection_type.setter
    def cli_connection_type(self, value):
        """
        The CLI connection type that will be used by the driver. Possible values are Auto, Console, SSH, Telnet and TCP. If Auto is selected the driver will choose the available connection type automatically. Default value is Auto.
        :type value: str
        """
        self.attributes['MySwitchG2.CLI Connection Type'] = value

    @property
    def cli_tcp_port(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.CLI TCP Port'] if 'MySwitchG2.CLI TCP Port' in self.attributes else None

    @cli_tcp_port.setter
    def cli_tcp_port(self, value):
        """
        TCP Port to user for CLI connection. If kept empty a default CLI port will be used based on the chosen protocol, for example Telnet will use port 23.
        :type value: str
        """
        self.attributes['MySwitchG2.CLI TCP Port'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def os_version(self):
        """
        :rtype: str
        """
        return self.attributes['CS_Switch.OS Version'] if 'CS_Switch.OS Version' in self.attributes else None

    @os_version.setter
    def os_version(self, value):
        """
        Version of the Operating System.
        :type value: str
        """
        self.attributes['CS_Switch.OS Version'] = value

    @property
    def system_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_Switch.System Name'] if 'CS_Switch.System Name' in self.attributes else None

    @system_name.setter
    def system_name(self, value):
        """
        A unique identifier for the device, if exists in the device terminal/os.
        :type value: str
        """
        self.attributes['CS_Switch.System Name'] = value

    @property
    def vendor(self):
        """
        :rtype: str
        """
        return self.attributes['CS_Switch.Vendor'] if 'CS_Switch.Vendor' in self.attributes else None

    @vendor.setter
    def vendor(self, value=''):
        """
        The name of the device manufacture.
        :type value: str
        """
        self.attributes['CS_Switch.Vendor'] = value

    @property
    def location(self):
        """
        :rtype: str
        """
        return self.attributes['CS_Switch.Location'] if 'CS_Switch.Location' in self.attributes else None

    @location.setter
    def location(self, value=''):
        """
        The device physical location identifier. For example Lab1/Floor2/Row5/Slot4.
        :type value: str
        """
        self.attributes['CS_Switch.Location'] = value

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['CS_Switch.Model'] if 'CS_Switch.Model' in self.attributes else None

    @model.setter
    def model(self, value=''):
        """
        The device model. This information is typically used for abstract resource filtering.
        :type value: str
        """
        self.attributes['CS_Switch.Model'] = value


class GenericChassis(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2.GenericChassis'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericChassis
        """
        result = GenericChassis(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericChassis'

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericChassis.Model'] if 'MySwitchG2.GenericChassis.Model' in self.attributes else None

    @model.setter
    def model(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericChassis.Model'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericChassis.Serial Number'] if 'MySwitchG2.GenericChassis.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericChassis.Serial Number'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class GenericModule(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2.GenericModule'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericModule
        """
        result = GenericModule(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericModule'

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericModule.Model'] if 'MySwitchG2.GenericModule.Model' in self.attributes else None

    @model.setter
    def model(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericModule.Model'] = value

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericModule.Version'] if 'MySwitchG2.GenericModule.Version' in self.attributes else None

    @version.setter
    def version(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericModule.Version'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericModule.Serial Number'] if 'MySwitchG2.GenericModule.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericModule.Serial Number'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class GenericSubModule(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2.GenericSubModule'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericSubModule
        """
        result = GenericSubModule(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericSubModule'

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericSubModule.Model'] if 'MySwitchG2.GenericSubModule.Model' in self.attributes else None

    @model.setter
    def model(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericSubModule.Model'] = value

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericSubModule.Version'] if 'MySwitchG2.GenericSubModule.Version' in self.attributes else None

    @version.setter
    def version(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericSubModule.Version'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericSubModule.Serial Number'] if 'MySwitchG2.GenericSubModule.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericSubModule.Serial Number'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class GenericPort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2.GenericPort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericPort
        """
        result = GenericPort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericPort'

    @property
    def mac_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.MAC Address'] if 'MySwitchG2.GenericPort.MAC Address' in self.attributes else None

    @mac_address.setter
    def mac_address(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.MAC Address'] = value

    @property
    def l2_protocol_type(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.L2 Protocol Type'] if 'MySwitchG2.GenericPort.L2 Protocol Type' in self.attributes else None

    @l2_protocol_type.setter
    def l2_protocol_type(self, value):
        """
        Such as POS, Serial
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.L2 Protocol Type'] = value

    @property
    def ipv4_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.IPv4 Address'] if 'MySwitchG2.GenericPort.IPv4 Address' in self.attributes else None

    @ipv4_address.setter
    def ipv4_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.IPv4 Address'] = value

    @property
    def ipv6_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.IPv6 Address'] if 'MySwitchG2.GenericPort.IPv6 Address' in self.attributes else None

    @ipv6_address.setter
    def ipv6_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.IPv6 Address'] = value

    @property
    def port_description(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.Port Description'] if 'MySwitchG2.GenericPort.Port Description' in self.attributes else None

    @port_description.setter
    def port_description(self, value):
        """
        The description of the port as configured in the device.
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.Port Description'] = value

    @property
    def bandwidth(self):
        """
        :rtype: float
        """
        return self.attributes['MySwitchG2.GenericPort.Bandwidth'] if 'MySwitchG2.GenericPort.Bandwidth' in self.attributes else None

    @bandwidth.setter
    def bandwidth(self, value):
        """
        The current interface bandwidth, in MB.
        :type value: float
        """
        self.attributes['MySwitchG2.GenericPort.Bandwidth'] = value

    @property
    def mtu(self):
        """
        :rtype: float
        """
        return self.attributes['MySwitchG2.GenericPort.MTU'] if 'MySwitchG2.GenericPort.MTU' in self.attributes else None

    @mtu.setter
    def mtu(self, value):
        """
        The current MTU configured on the interface.
        :type value: float
        """
        self.attributes['MySwitchG2.GenericPort.MTU'] = value

    @property
    def duplex(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.Duplex'] if 'MySwitchG2.GenericPort.Duplex' in self.attributes else None

    @duplex.setter
    def duplex(self, value):
        """
        The current duplex configuration on the interface. Possible values are Half or Full.
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.Duplex'] = value

    @property
    def adjacent(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.Adjacent'] if 'MySwitchG2.GenericPort.Adjacent' in self.attributes else None

    @adjacent.setter
    def adjacent(self, value):
        """
        The adjacent device (system name) and port, based on LLDP or CDP protocol.
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.Adjacent'] = value

    @property
    def protocol_type(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPort.Protocol Type'] if 'MySwitchG2.GenericPort.Protocol Type' in self.attributes else None

    @protocol_type.setter
    def protocol_type(self, value='0'):
        """
        Default values is Transparent (="0")
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPort.Protocol Type'] = value

    @property
    def auto_negotiation(self):
        """
        :rtype: bool
        """
        return self.attributes['MySwitchG2.GenericPort.Auto Negotiation'] if 'MySwitchG2.GenericPort.Auto Negotiation' in self.attributes else None

    @auto_negotiation.setter
    def auto_negotiation(self, value):
        """
        The current auto negotiation configuration on the interface.
        :type value: bool
        """
        self.attributes['MySwitchG2.GenericPort.Auto Negotiation'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class GenericPowerPort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2.GenericPowerPort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericPowerPort
        """
        result = GenericPowerPort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericPowerPort'

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPowerPort.Model'] if 'MySwitchG2.GenericPowerPort.Model' in self.attributes else None

    @model.setter
    def model(self, value):
        """
        The device model. This information is typically used for abstract resource filtering.
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPowerPort.Model'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPowerPort.Serial Number'] if 'MySwitchG2.GenericPowerPort.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPowerPort.Serial Number'] = value

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPowerPort.Version'] if 'MySwitchG2.GenericPowerPort.Version' in self.attributes else None

    @version.setter
    def version(self, value):
        """
        The firmware version of the resource.
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPowerPort.Version'] = value

    @property
    def port_description(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPowerPort.Port Description'] if 'MySwitchG2.GenericPowerPort.Port Description' in self.attributes else None

    @port_description.setter
    def port_description(self, value):
        """
        The description of the port as configured in the device.
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPowerPort.Port Description'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class GenericPortChannel(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2.GenericPortChannel'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericPortChannel
        """
        result = GenericPortChannel(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericPortChannel'

    @property
    def associated_ports(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPortChannel.Associated Ports'] if 'MySwitchG2.GenericPortChannel.Associated Ports' in self.attributes else None

    @associated_ports.setter
    def associated_ports(self, value):
        """
        Ports associated with this port channel. The value is in the format ???[portResourceName],??????, for example ???GE0-0-0-1,GE0-0-0-2???
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPortChannel.Associated Ports'] = value

    @property
    def ipv4_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPortChannel.IPv4 Address'] if 'MySwitchG2.GenericPortChannel.IPv4 Address' in self.attributes else None

    @ipv4_address.setter
    def ipv4_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPortChannel.IPv4 Address'] = value

    @property
    def ipv6_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPortChannel.IPv6 Address'] if 'MySwitchG2.GenericPortChannel.IPv6 Address' in self.attributes else None

    @ipv6_address.setter
    def ipv6_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPortChannel.IPv6 Address'] = value

    @property
    def port_description(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPortChannel.Port Description'] if 'MySwitchG2.GenericPortChannel.Port Description' in self.attributes else None

    @port_description.setter
    def port_description(self, value):
        """
        The description of the port as configured in the device.
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPortChannel.Port Description'] = value

    @property
    def protocol_type(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.GenericPortChannel.Protocol Type'] if 'MySwitchG2.GenericPortChannel.Protocol Type' in self.attributes else None

    @protocol_type.setter
    def protocol_type(self, value='0s'):
        """
        Default values is Transparent (="0")
        :type value: str
        """
        self.attributes['MySwitchG2.GenericPortChannel.Protocol Type'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class ResourcePort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'MySwitchG2.ResourcePort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype ResourcePort
        """
        result = ResourcePort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'ResourcePort'

    @property
    def mac_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.ResourcePort.MAC Address'] if 'MySwitchG2.ResourcePort.MAC Address' in self.attributes else None

    @mac_address.setter
    def mac_address(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.ResourcePort.MAC Address'] = value

    @property
    def ipv4_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.ResourcePort.IPv4 Address'] if 'MySwitchG2.ResourcePort.IPv4 Address' in self.attributes else None

    @ipv4_address.setter
    def ipv4_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.ResourcePort.IPv4 Address'] = value

    @property
    def ipv6_address(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.ResourcePort.IPv6 Address'] if 'MySwitchG2.ResourcePort.IPv6 Address' in self.attributes else None

    @ipv6_address.setter
    def ipv6_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['MySwitchG2.ResourcePort.IPv6 Address'] = value

    @property
    def port_speed(self):
        """
        :rtype: str
        """
        return self.attributes['MySwitchG2.ResourcePort.Port Speed'] if 'MySwitchG2.ResourcePort.Port Speed' in self.attributes else None

    @port_speed.setter
    def port_speed(self, value):
        """
        The port speed (e.g 10Gb/s, 40Gb/s, 100Mb/s)
        :type value: str
        """
        self.attributes['MySwitchG2.ResourcePort.Port Speed'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value



