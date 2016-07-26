from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.snmp.quali_snmp import QualiSnmp, QualiMibTable
from cloudshell.networking.autoload.networking_autoload_resource_attributes import NetworkingStandardRootAttributes
from cloudshell.shell.core.driver_context import ResourceCommandContext
from cloudshell.networking.autoload.networking_autoload_resource_structure import Port, Chassis, Module
from cloudshell.shell.core.driver_context import AutoLoadDetails
import re


class SNMPParams:

    def __init__(self, snmp_version, snmp_read_community,
                 snmp_v3_user = None,
                 snmp_v3_password = None,
                 snmp_v3_privatekey=None):

        self.snmp_version = snmp_version
        self.snmp_read_community=snmp_read_community
        self.snmp_v3_user=snmp_v3_user
        self.snmp_v3_password=snmp_v3_password
        self.snmp_v3_privatekey=snmp_v3_privatekey


class GenericSNMPDiscovery:

    def discover(self, ip, model, vendor, snmp_params):
        """
        :param str ip: The device IP address
        :param str model: The device model in CloudShell
        :param str vendor: The device vendor
        :param SNMPParams snmp_params: The device vendor
        :return: The loaded resources and attributes
        :rtype: AutoLoadDetails
        """

        logger = get_qs_logger()

        self.snmp = QualiSnmp(ip=ip, snmp_version=snmp_params.snmp_version,
                              snmp_user=snmp_params.snmp_v3_user,
                              snmp_password=snmp_params.snmp_v3_password,
                              snmp_community=snmp_params.snmp_read_community,
                              snmp_private_key=snmp_params.snmp_v3_privatekey,
                              logger=logger)


        self.attributes=[]
        self.exclusion_list=[]
        self.chassis_list=[]
        self.port_exclude_pattern='TEST'
        self.port_mapping ={}
        self.port_list =[]
        self.power_supply_list=[]
        self.entity_table_black_list=[]
        self._excluded_models = []
        self.relative_path = {}
        self.module_list = []
        self.resources = []

        self._get_device_details(model, vendor)
        self._load_snmp_tables()

        if(len(self.chassis_list)<1):
            print 'Empty Chasis List Found'
            exit(1)

        for chassis in self.chassis_list:
            if chassis not in self.exclusion_list:
                chassis_id = self._get_resource_id(chassis)
                if chassis_id == '-1':
                    chassis_id = '0'
                self.relative_path[chassis] = chassis_id
        # to add custom MIBSs
        #snmp_handler.update_mib_sources()

        self._filter_lower_bay_containers()
        self.get_module_list()
        self.add_relative_paths()
        self._get_chassis_attributes(self.chassis_list)
        self._get_ports_attributes()
        self._get_module_attributes()

        result = AutoLoadDetails(resources=self.resources, attributes=self.attributes)

        print result #an Object you can play with it

    def _get_device_details(self, model, vendor):
        """Get root element attributes
           :param ResourceCommandContext attributes_dictionary:

        """

        result = {'system_name': self.snmp.get_property('SNMPv2-MIB', 'sysName', 0),
                  'vendor': vendor,
                  'model': model,
                  'location': self.snmp.get_property('SNMPv2-MIB', 'sysLocation', 0),
                  'contact': self.snmp.get_property('SNMPv2-MIB', 'sysContact', 0),
                  'version': ''}

        match_version = re.search(r'Version\s+(?P<software_version>\S+)\S*\s+',
                                  self.snmp.get_property('SNMPv2-MIB', 'sysDescr', 0))

        if match_version:
            result['version'] = match_version.groupdict()['software_version'].replace(',', '')

        root = NetworkingStandardRootAttributes(**result)
        self.attributes.extend(root.get_autoload_resource_attributes())

    def _load_snmp_tables(self):
        """ Load all  required snmp tables

        :return:
        """

        self.if_table = self.snmp.get_table('IF-MIB', 'ifDescr')
        self.entity_table = self._get_entity_table()
        if len(self.entity_table.keys()) < 1:
            raise Exception('Cannot load entPhysicalTable. Autoload cannot continue')

        self.lldp_local_table = self.snmp.get_table('LLDP-MIB', 'lldpLocPortDesc')
        self.lldp_remote_table = self.snmp.get_table('LLDP-MIB', 'lldpRemTable')
        self.duplex_table = self.snmp.get_table('EtherLike-MIB', 'dot3StatsIndex')
        self.ip_v4_table = self.snmp.get_table('IP-MIB', 'ipAddrTable')

    def _get_entity_table(self):
        """Read Entity-MIB and filter out device's structure and all it's elements, like ports, modules, chassis, etc.

        :rtype: QualiMibTable
        :return: structured and filtered EntityPhysical table.
        """

        result_dict = QualiMibTable('entPhysicalTable')

        entity_table_critical_port_attr = {'entPhysicalContainedIn': 'str', 'entPhysicalClass': 'str',
                                           'entPhysicalVendorType': 'str'}
        entity_table_optional_port_attr = {'entPhysicalDescr': 'str', 'entPhysicalName': 'str'}

        physical_indexes = self.snmp.get_table('ENTITY-MIB', 'entPhysicalParentRelPos')
        for index in physical_indexes.keys():
            is_excluded = False
            if physical_indexes[index]['entPhysicalParentRelPos'] == '':
                self.exclusion_list.append(index)
                continue
            temp_entity_table = physical_indexes[index].copy()
            temp_entity_table.update(self.snmp.get_properties('ENTITY-MIB', index, entity_table_critical_port_attr)
                                     [index])
            if temp_entity_table['entPhysicalContainedIn'] == '':
                is_excluded = True
                self.exclusion_list.append(index)

            for item in self.entity_table_black_list:
                if item in temp_entity_table['entPhysicalVendorType'].lower():
                    is_excluded = True
                    break

            if is_excluded is True:
                continue

            temp_entity_table.update(self.snmp.get_properties('ENTITY-MIB', index, entity_table_optional_port_attr)
                                     [index])

            if temp_entity_table['entPhysicalClass'] == '':
                vendor_type = self.snmp.get_property('ENTITY-MIB', 'entPhysicalVendorType', index)
                index_entity_class = None
                if vendor_type == '':
                   continue
                if 'cevcontainer' in vendor_type.lower():
                    index_entity_class = 'container'
                elif 'cevchassis' in vendor_type.lower():
                    index_entity_class = 'chassis'
                elif 'cevmodule' in vendor_type.lower():
                    index_entity_class = 'module'
                elif 'cevport' in vendor_type.lower():
                    index_entity_class = 'port'
                elif 'cevpowersupply' in vendor_type.lower():
                    index_entity_class = 'powerSupply'
                if index_entity_class:
                    temp_entity_table['entPhysicalClass'] = index_entity_class
            else:
                temp_entity_table['entPhysicalClass'] = temp_entity_table['entPhysicalClass'].replace("'", "")

            if re.search(r'stack|chassis|module|port|powerSupply|container|backplane',
                         temp_entity_table['entPhysicalClass']):
                result_dict[index] = temp_entity_table

            if temp_entity_table['entPhysicalClass'] == 'chassis':
                self.chassis_list.append(index)
            elif temp_entity_table['entPhysicalClass'] == 'port':
                if not re.search(self.port_exclude_pattern, temp_entity_table['entPhysicalName'], re.IGNORECASE) \
                        and not re.search(self.port_exclude_pattern, temp_entity_table['entPhysicalDescr'],
                                          re.IGNORECASE):
                    port_id = self._get_mapping(index, temp_entity_table['entPhysicalDescr'])
                    if port_id and port_id in self.if_table and port_id not in self.port_mapping.values():
                        self.port_mapping[index] = port_id
                        self.port_list.append(index)
            elif temp_entity_table['entPhysicalClass'] == 'powerSupply':
                self.power_supply_list.append(index)

        self._filter_entity_table(result_dict)
        return result_dict

    def _get_mapping(self, port_index, port_descr):
        """Get mapping from entPhysicalTable to ifTable.
        Build mapping based on ent_alias_mapping_table if exists else build manually based on
        entPhysicalDescr <-> ifDescr mapping.

        :return: simple mapping from entPhysicalTable index to ifTable index:
        |        {entPhysicalTable index: ifTable index, ...}
        """

        port_id = None
        try:
            ent_alias_mapping_identifier = self.snmp.get(('ENTITY-MIB', 'entAliasMappingIdentifier', port_index, 0))
            port_id = int(ent_alias_mapping_identifier['entAliasMappingIdentifier'].split('.')[-1])
        except Exception as e:

            if_table_re = "/".join(re.findall('\d+', port_descr))
            for interface in self.if_table.values():
                if re.search(if_table_re, interface['ifDescr']):
                    port_id = int(interface['suffix'])
                    break
        return port_id

    def _filter_entity_table(self, raw_entity_table):
        """Filters out all elements if their parents, doesn't exist, or listed in self.exclusion_list

        :param raw_entity_table: entity table with unfiltered elements
        """

        elements = raw_entity_table.filter_by_column('ContainedIn').sort_by_column('ParentRelPos').keys()
        for element in reversed(elements):
            parent_id = int(self.entity_table[element]['entPhysicalContainedIn'])

            if parent_id not in raw_entity_table or parent_id in self.exclusion_list:
                self.exclusion_list.append(element)

    def _get_resource_id(self, item_id):
        parent_id = int(self.entity_table[item_id]['entPhysicalContainedIn'])
        if parent_id > 0 and parent_id in self.entity_table:
            if re.search(r'container|backplane', self.entity_table[parent_id]['entPhysicalClass']):
                result = self.entity_table[parent_id]['entPhysicalParentRelPos']
            elif parent_id in self._excluded_models:
                result = self._get_resource_id(parent_id)
            else:
                result = self.entity_table[item_id]['entPhysicalParentRelPos']
        else:
            result = self.entity_table[item_id]['entPhysicalParentRelPos']
        return result

    def _filter_lower_bay_containers(self):

        upper_container = None
        lower_container = None
        containers = self.entity_table.filter_by_column('Class', "container").sort_by_column('ParentRelPos').keys()
        for container in containers:
            vendor_type = self.snmp.get_property('ENTITY-MIB', 'entPhysicalVendorType', container)
            if 'uppermodulebay' in vendor_type.lower():
                upper_container = container
            if 'lowermodulebay' in vendor_type.lower():
                lower_container = container
        if lower_container and upper_container:
            child_upper_items_len = len(self.entity_table.filter_by_column('ContainedIn', str(upper_container)
                                                                           ).sort_by_column('ParentRelPos').keys())
            child_lower_items = self.entity_table.filter_by_column('ContainedIn', str(lower_container)
                                                                   ).sort_by_column('ParentRelPos').keys()
            for child in child_lower_items:
                self.entity_table[child]['entPhysicalContainedIn'] = upper_container
                self.entity_table[child]['entPhysicalParentRelPos'] = str(child_upper_items_len + int(
                    self.entity_table[child]['entPhysicalParentRelPos']))

    def get_module_list(self):
        """Set list of all modules from entity mib table for provided list of ports

        :return:
        """

        for port in self.port_list:
            modules = []
            modules.extend(self._get_module_parents(port))
            for module in modules:
                if module in self.module_list:
                    continue
                vendor_type = self.snmp.get_property('ENTITY-MIB', 'entPhysicalVendorType', module)
                if not re.search(self.module_exclude_pattern, vendor_type.lower()):
                    if module not in self.exclusion_list and module not in self.module_list:
                        self.module_list.append(module)
                else:
                    self._excluded_models.append(module)

    def add_relative_paths(self):
        """Build dictionary of relative paths for each module and port

        :return:
        """

        port_list = list(self.port_list)
        module_list = list(self.module_list)
        for module in module_list:
            if module not in self.exclusion_list:
                self.relative_path[module] = self.get_relative_path(module) + '/' + self._get_resource_id(module)
            else:
                self.module_list.remove(module)
        for port in port_list:
            if port not in self.exclusion_list:
                self.relative_path[port] = self._get_port_relative_path(
                    self.get_relative_path(port) + '/' + self._get_resource_id(port))
            else:
                self.port_list.remove(port)

    def get_relative_path(self, item_id):
        """Build relative path for received item

        :param item_id:
        :return:
        """

        result = ''
        if item_id not in self.chassis_list:
            parent_id = int(self.entity_table[item_id]['entPhysicalContainedIn'])
            if parent_id not in self.relative_path.keys():
                if parent_id in self.module_list:
                    result = self._get_resource_id(parent_id)
                if result != '':
                    result = self.get_relative_path(parent_id) + '/' + result
                else:
                    result = self.get_relative_path(parent_id)
            else:
                result = self.relative_path[parent_id]
        else:
            result = self.relative_path[item_id]

        return result

    def _get_chassis_attributes(self, chassis_list):
        """Get Chassis element attributes

        :param chassis_list: list of chassis to load attributes for
        :return:
        """


        for chassis in chassis_list:
            chassis_id = self.relative_path[chassis]
            chassis_details_map = {
                'chassis_model': self.snmp.get_property('ENTITY-MIB', 'entPhysicalModelName', chassis),
                'serial_number': self.snmp.get_property('ENTITY-MIB', 'entPhysicalSerialNum', chassis)
            }
            if chassis_details_map['chassis_model'] == '':
                chassis_details_map['chassis_model'] = self.entity_table[chassis]['entPhysicalDescr']
            relative_path = '{0}'.format(chassis_id)
            chassis_object = Chassis(relative_path=relative_path, **chassis_details_map)
            self._add_resource(chassis_object)

    def _get_ports_attributes(self):
        """Get resource details and attributes for every port in self.port_list

        :return:
        """


        for port in self.port_list:
            if_table_port_attr = {'ifType': 'str', 'ifPhysAddress': 'str', 'ifMtu': 'int', 'ifSpeed': 'int'}
            if_table = self.if_table[self.port_mapping[port]].copy()
            if_table.update(self.snmp.get_properties('IF-MIB', self.port_mapping[port], if_table_port_attr))
            interface_name = self.if_table[self.port_mapping[port]]['ifDescr'].replace("'", '')
            if interface_name == '':
                interface_name = self.entity_table[port]['entPhysicalName']
            if interface_name == '':
                continue
            interface_type = if_table[self.port_mapping[port]]['ifType'].replace('/', '').replace("'", '')
            attribute_map = {'l2_protocol_type': interface_type,
                             'mac': if_table[self.port_mapping[port]]['ifPhysAddress'],
                             'mtu': if_table[self.port_mapping[port]]['ifMtu'],
                             'bandwidth': if_table[self.port_mapping[port]]['ifSpeed'],
                             'description': self.snmp.get_property('IF-MIB', 'ifAlias', self.port_mapping[port]),
                             'adjacent': self._get_adjacent(self.port_mapping[port])}
            attribute_map.update(self._get_interface_details(self.port_mapping[port]))
            attribute_map.update(self._get_ip_interface_details(self.port_mapping[port]))
            port_object = Port(name=interface_name, relative_path=self.relative_path[port], **attribute_map)
            self._add_resource(port_object)

    def _get_module_attributes(self):
        """Set attributes for all discovered modules

        :return:
        """


        for module in self.module_list:
            module_id = self.relative_path[module]
            module_index = self._get_resource_id(module)
            module_details_map = {
                'module_model': self.entity_table[module]['entPhysicalDescr'],
                'version': self.snmp.get_property('ENTITY-MIB', 'entPhysicalSoftwareRev', module),
                'serial_number': self.snmp.get_property('ENTITY-MIB', 'entPhysicalSerialNum', module)
            }

            if '/' in module_id and len(module_id.split('/')) < 3:
                module_name = 'Module {0}'.format(module_index)
                model = 'Generic Module'
            else:
                module_name = 'Sub Module {0}'.format(module_index)
                model = 'Generic Sub Module'
            module_object = Module(name=module_name, model=model, relative_path=module_id, **module_details_map)
            self._add_resource(module_object)

    def _get_module_parents(self, module_id):
        result = []
        parent_id = int(self.entity_table[module_id]['entPhysicalContainedIn'])
        if parent_id > 0 and parent_id in self.entity_table:
            if re.search(r'module', self.entity_table[parent_id]['entPhysicalClass']):
                result.append(parent_id)
                result.extend(self._get_module_parents(parent_id))
            elif re.search(r'chassis', self.entity_table[parent_id]['entPhysicalClass']):
                return result
            else:
                result.extend(self._get_module_parents(parent_id))
        return result

    def _get_port_relative_path(self, relative_id):
        if relative_id in self.relative_path.values():
            if '/' in relative_id:
                ids = relative_id.split('/')
                ids[-1] = str(int(ids[-1]) + 1000)
                result = '/'.join(ids)
            else:
                result = str(int(relative_id.split()[-1]) + 1000)
            if relative_id in self.relative_path.values():
                result = self._get_port_relative_path(result)
        else:
            result = relative_id
        return result

    def _add_resource(self, resource):
        """Add object data to resources and attributes lists

        :param resource: object which contains all required data for certain resource
        """

        self.resources.append(resource.get_autoload_resource_details())
        self.attributes.extend(resource.get_autoload_resource_attributes())

    def _get_adjacent(self, interface_id):
        """Get connected device interface and device name to the specified port id, using  lldp protocols

        :param interface_id: port id
        :return: device's name and port connected to port id
        :rtype string
        """
        result = ''
        if  self.lldp_remote_table:
            for key, value in self.lldp_local_table.iteritems():
                interface_name = self.if_table[interface_id]['ifDescr']
                if interface_name == '':
                    break
                if 'lldpLocPortDesc' in value and interface_name in value['lldpLocPortDesc']:
                    if 'lldpRemSysName' in self.lldp_remote_table and 'lldpRemPortDesc' in self.lldp_remote_table:
                        result = '{0} through {1}'.format(self.lldp_remote_table[key]['lldpRemSysName'],
                                                          self.lldp_remote_table[key]['lldpRemPortDesc'])
        return result

    def _get_interface_details(self, port_index):
        """Get interface attributes

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'Auto Negotiation': '', 'Duplex': ''}
        """

        interface_details = {'duplex': 'Full', 'auto_negotiation': 'False'}
        try:
            auto_negotiation = self.snmp.get(('MAU-MIB', 'ifMauAutoNegAdminStatus', port_index, 1)).values()[0]
            if 'enabled' in auto_negotiation.lower():
                interface_details['auto_negotiation'] = 'True'
        except Exception as e:
            print('Failed to load auto negotiation property for interface {0}'.format(e.message))
        for key, value in self.duplex_table.iteritems():
            if 'dot3StatsIndex' in value.keys() and value['dot3StatsIndex'] == str(port_index):
                interface_duplex = self.snmp.get_property('EtherLike-MIB', 'dot3StatsDuplexStatus', key)
                if 'halfDuplex' in interface_duplex:
                    interface_details['duplex'] = 'Half'
        return interface_details

    def _get_ip_interface_details(self, port_index):
        """Get IP address details for provided port

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'IPv4 Address': '', 'IPv6 Address': ''}
        """

        interface_details = {'ipv4_address': '', 'ipv6_address': ''}
        if self.ip_v4_table and len(self.ip_v4_table) > 1:
            for key, value in self.ip_v4_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == port_index:
                    interface_details['ipv4_address'] = key
                break

        return interface_details

