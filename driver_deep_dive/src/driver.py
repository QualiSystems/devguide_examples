from time import sleep

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext, ResourceCommandContext, CancellationContext

class DriverDeepDiveDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def return_simple_string(self, context):
        """
        A simple example function returning a string
        :param ResourceCommandContext context: the context the command runs on
        """
        return "Some string return value"

    def return_complex_object(self, context):
        """
        A simple example function returning a string
        :param ResourceCommandContext context: the context the command runs on
        """
        return context

    def failed_command(self, context):
        """
        A simple example function returning a string
        :param ResourceCommandContext context: the context the command runs on
        """
        raise Exception("Failed to run command")


    def cancellable_command(self, context, cancellation_context):
        """
        A simple example function returning a string
        :param ResourceCommandContext context: the context the command runs on
        :param CancellationContext cancellation_context: an object used to signal a request to cancel the operation
        """
        counter = 0
        while counter < 1000 and not cancellation_context.is_cancelled:
            counter += 1
            sleep(1)


    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass