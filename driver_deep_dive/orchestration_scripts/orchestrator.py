from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
from cloudshell.helpers.scripts import cloudshell_dev_helpers as dev_helpers

dev_helpers.attach_to_cloudshell_as("admin","admin","Global","55aec269-792f-4ca9-8156-9967788d3a4f","10.211.55.4")

reservation_id = helpers.get_reservation_context_details().id

try:
    helpers.get_api_session().ExecuteCommand(reservation_id, "DriverDeepDive", "Resource", "failed_command")

except CloudShellAPIError as err:
    print err.message
    raise
