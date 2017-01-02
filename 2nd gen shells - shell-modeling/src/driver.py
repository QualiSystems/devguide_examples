from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext


from data_model import *  # run 'shellfoundry generate' to generate data model classes

class ShellModelingDriver (ResourceDriverInterface):


    def shell_model_example (self, context):

        resource = ShellModeling.create_from_context(context)

        # resource holds an instance of the shell data model

        custom_property_1 = resource.custom_property_1













