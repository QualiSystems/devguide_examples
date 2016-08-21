import pprint

import jsonpickle
from cloudshell.api.cloudshell_api import CloudShellAPISession, UpdateTopologyGlobalInputsRequest
import time

from devops_integration.python_api.extensions.sandbox_helpers import SandboxHelpers


def run_some_tests_or_other_code(sandox_details):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(jsonpickle.dumps(sandox_details))

    time.sleep(10)


def main():
    """
    Example workflow of starting a sandbox, waiting for it to setup, then stopping it
    :return:
    """

    session = CloudShellAPISession('10.211.55.4', "admin", "admin", "Global")
    # Create the sandbox
    sandbox = session.CreateImmediateTopologyReservation('test sandbox', owner='admin',
                                                         durationInMinutes=120,
                                                         topologyFullPath='AWS Simple Demo1',
                                                         globalInputs=[UpdateTopologyGlobalInputsRequest('Target Cloud', 'AWS')]).Reservation

    sandbox_details = SandboxHelpers().wait_for_sandbox_setup(sandbox.Id, session,10)
    run_some_tests_or_other_code(sandbox_details)
    session.EndReservation(sandbox.Id)




if __name__ == "__main__":
    main()
