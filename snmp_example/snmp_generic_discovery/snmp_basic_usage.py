from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.snmp.quali_snmp import QualiSnmp, QualiMibTable

class SNMPExample:

    def retrieving_snmp_properties(self, ip, community_string):

        logger = get_qs_logger()

        snmp_service = QualiSnmp(ip=ip, snmp_version='2',
                              snmp_community=community_string,
                              logger=logger)

        return snmp_service.get_property('SNMPv2-MIB', 'sysName', 0)

    def retrieving_snmp_table(self, ip):
        logger = get_qs_logger()

        snmp_service = QualiSnmp(ip=ip, snmp_version='2',
                                 snmp_community="Community String",
                                 logger=logger)

        if_table = snmp_service.get_table('IF-MIB', 'ifDescr')



