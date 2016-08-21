import pprint

import jsonpickle
import time
from cloudshell.api.cloudshell_api import UpdateTopologyGlobalInputsRequest

from devops_integration.python_api.extensions.sandbox_context import SandboxContext, QualiConnectivityParams, \
    BlueprintInputs



def run_some_tests_or_other_code(sandox_details):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(jsonpickle.dumps(sandox_details))

    time.sleep(10)


def main():
    """
    Example workflow of starting a sandbox, waiting for it to setup, then stopping it
    :return:
    """
    connectivity_params = QualiConnectivityParams(api_service_host='localhost', domain='Global',
                                                  password='admin', username='admin')
    inputs = BlueprintInputs(global_inputs=[UpdateTopologyGlobalInputsRequest('Target Cloud', 'AWS')])

    with SandboxContext(connectivity_params=connectivity_params,
                        blueprint_name='Simple Blueprint1', duration=120,
                        blueprint_inputs=inputs) as sandbox:
        run_some_tests_or_other_code(sandbox)




if __name__ == "__main__":
    main()