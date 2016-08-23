from cloudshell.api.common_cloudshell_api import CloudShellAPIError
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers 
from cloudshell.helpers.scripts.cloudshell_scripts_helpers import ReservationContextDetails

from sandbox_scripts.environment.setup.setup_script import EnvironmentSetup


class EnvironmentSetupExtensions:
    NO_DRIVER_ERR = "129"
    DRIVER_FUNCTION_ERROR = "151"
        
    def run_post_setup_logic(self, reservation_context):
        """
        :param ReservationContextDetails reservation_context:
        :param EnvironmentSetup.EnvironmentSetupResult setup_result:

        :return: 
        """

        reservation_details = helpers.get_api_session().GetReservationDetails(reservation_context.id)

        # Run a custom post-setup command on each Shell resource
        resource_names = [resource.Name for resource in reservation_details.ReservationDescription.Resources]

        self._try_execute_command_on_resources(reservation_context.id, resource_names, "Bootsrap")

    def _try_execute_command_on_resources(session, reservation_id, resource_names, command_name, command_inputs=[]):
        """
        This function will try to execute a command on all app resources that support it
        :param CloudShellAPISession session: CloudShell API Session
        :param str reservation_id: The reservation Id to run the commands on
        :param str command_name: The command to try and execute
        :param list[InputNameValue] command_inputs: Inputs parameters for the command
        :return: The aggregated results of the successful calls
        :rtype: dict[str,str]
        """
        results = {}
        for resource in resource_names:
            try:
                result = session.ExecuteCommand(reservation_id, resource.Name, "Resource", command_name, command_inputs)
                results[resource.Name] = result.Output
    
            except CloudShellAPIError as exc:
                # Ignore the error if the command doesn't exist on the resource or its not assigned a driver
                if exc.code not in (
                EnvironmentSetupExtensions.NO_DRIVER_ERR, EnvironmentSetupExtensions.DRIVER_FUNCTION_ERROR):
                    raise
        return results
