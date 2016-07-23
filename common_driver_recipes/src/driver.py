from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext, ResourceCommandContext


class CommonDriverRecipesDriver (ResourceDriverInterface):

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

    def decrypt_password(self, context):
        """
        A simple example function
        :param ResourceCommandContext context: the context the command runs on
        """
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)

        password = session.DecryptPassword(context.resource.attributes['Password']).Value


    def update_resource_status(self, context):
        """
        A simple example function
        :param ResourceCommandContext context: the context the command runs on
        """
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)

        session.SetResourceLiveStatus(context.resource.name, "Offline" )
        for i in range(0,10):
            session.SetResourceLiveStatus(context.resource.name, "Progress {status}".format(status=str(i*10)))


        session.SetResourceLiveStatus(context.resource.name, "Online" )


    def update_resource_status_to_console(self, context):
        """
        A simple example function
        :param ResourceCommandContext context: the context the command runs on
        """
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)

        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Starting operation")
        for i in range(0, 10):
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Progress as {status}%".format(status=str(i * 10)))

        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Done - service online")
