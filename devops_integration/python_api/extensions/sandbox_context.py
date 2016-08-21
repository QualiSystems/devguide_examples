from __future__ import print_function

import datetime

from cloudshell.api.cloudshell_api import CloudShellAPISession, UpdateTopologyGlobalInputsRequest

from devops_integration.python_api.extensions.sandbox_helpers import SandboxHelpers


class QualiConnectivityParams:
    def __init__(self,api_service_host, username, password, domain,api_port=8029):
        self.domain = domain
        self.password = password
        self.username = username
        self.api_port = api_port
        self.api_service_host = api_service_host

class BlueprintInputs:
    def __init__(self, global_inputs=[], requirements_inputs=[], additional_info_inputs=[]):
        """
        :param list[UpdateTopologyGlobalInputsRequest] global_inputs: Global inputs associated with the specified topology. For example: {['Input Name', 'Value';]}.
        :param list[UpdateTopologyRequirementsInputsRequest] requirements_inputs: Requirements inputs associated with the specified topology. For example: {['Resource Name', 'Input Name', 'Value', 'AttributeType';]}, AttributeType can be one of the following: Attributes/Models/Quantity.
        :param list[UpdateTopologyAdditionalInfoInputsRequest] additiona_info_inputs: Additional info inputs associated with the specified topology. For example: {['Resource Name', 'Input Name', 'Value';]}.
        """
        self.additional_info_inputs = additional_info_inputs
        self.requirements_inputs = requirements_inputs
        self.global_inputs = global_inputs


class SandboxContext:

    def __init__(self, connectivity_params, blueprint_name, duration, sandbox_name=None, blueprint_inputs=None):
        """
        :param QualiConnectivityParams connectivity_params: Information about the API server and the user/pwd/domain
        :param str blueprint_name: Name of the blueprint to use for the sandbox
        :param int duration: Sandbox time scope duration in minutes
        :param str sandbox_name: The sandbox name, if not provided, the following convention will be used:
        :param BlueprintInputs blueprint_inputs: Inputs to the blueprint that need to be provided to create the sandbox

        """
        self.blueprint_inputs = blueprint_inputs
        self.sandbox_name = sandbox_name
        self.duration = duration
        self.blueprint_name = blueprint_name
        self.connectivity_params = connectivity_params
        self.sandbox_name = sandbox_name or self._default_name(blueprint_name)

    @staticmethod
    def _default_name(blueprint_name):
        return blueprint_name + '-' + datetime.datetime.utcnow().strftime("%m-%d-%Y %H-%M")

    def __enter__(self):
        session = CloudShellAPISession(self.connectivity_params.api_service_host, self.connectivity_params.username,
                                       self.connectivity_params.username, self.connectivity_params.domain)
        # Create the sandbox
        sandbox = session.CreateImmediateTopologyReservation(self.sandbox_name, owner=self.connectivity_params.username,
                                                             durationInMinutes=self.duration,
                                                             topologyFullPath=self.blueprint_name,
                                                             globalInputs=self.blueprint_inputs.global_inputs,
                                                             requirementsInputs=self.blueprint_inputs.requirements_inputs,
                                                             additionalInfoInputs=self.blueprint_inputs.additional_info_inputs).Reservation
        self.sandbox_id = sandbox.Id
        return SandboxHelpers().wait_for_sandbox_setup(sandbox.Id, session, 10)

    def __exit__(self, exc_type, exc_val, exc_tb):
        session = CloudShellAPISession(self.connectivity_params.api_service_host, self.connectivity_params.username,
                                       self.connectivity_params.username, self.connectivity_params.domain)
        session.EndReservation(self.sandbox_id)
