import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

NO_DRIVER_ERR = "129"
DRIVER_FUNCTION_ERROR = "151"


def try_execute_command_on_resources(session, reservation_id, command_name, command_inputs=[]):
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
    for resource in session.GetReservationDetails(reservation_id).ReservationDescription.Resources:
        try:
            result = session.ExecuteCommand(reservation_id, resource.Name, "Resource", command_name, command_inputs)
            results[resource.Name]=result.Output

        except CloudShellAPIError as exc:
            # Ignore the error if the command doesn't exist on the resource or its not assigned a driver
            if exc.code not in (NO_DRIVER_ERR,DRIVER_FUNCTION_ERROR):
                raise


def main():

    session = helpers.get_api_session()
    command_to_run = helpers.get_user_param("Command Name")
    try_execute_command_on_resources(session, reservation_id=helpers.get_reservation_context_details().id, command_name=command_to_run)


if __name__ == "__main__":
    main()