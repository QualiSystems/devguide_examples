from __future__ import print_function

import datetime

from devops_integration.sandbox_api_python_2_and_3.sandbox_api.sandbox_apis import SandboxRESTAPI


class QualiConnectivityParams:
    def __init__(self,api_service_host, api_port, username, password, domain):
        self.domain = domain
        self.password = password
        self.username = username
        self.api_port = api_port
        self.api_service_host = api_service_host


class SandboxContext:

    def __init__(self, connectivity_params, blueprint_name, duration, sandbox_name=None):
        """
        :param QualiConnectivityParams connectivity_params: Information about the API server and the user/pwd/domain
        :param str blueprint_name: Name of the blueprint to use for the sandbox
        :param datetime.timedelta duration: Sandbox time scope duration
        :param str sandbox_name: The sandbox name, if not provided, the following convention will be used:
        """
        self.sandbox_name = sandbox_name
        self.duration = duration
        self.blueprint_name = blueprint_name
        self.connectivity_params = connectivity_params
        self.sandbox_name = sandbox_name or self._default_name(blueprint_name)

    @staticmethod
    def _default_name(blueprint_name):
        return blueprint_name + '-' + datetime.datetime.utcnow().strftime("%m-%d-%Y %H-%M")

    def __enter__(self):
        connectivity_params = self.connectivity_params
        sandbox_api = SandboxRESTAPI(connectivity_params.api_service_host, connectivity_params.api_port)
        sandbox_api.login(connectivity_params.username, connectivity_params.password, connectivity_params.domain)
        sandbox_id = sandbox_api.start_sandbox('AWS Simple Demo', datetime.timedelta(hours=2), self.sandbox_name)
        self.sandbox_id = sandbox_id
        return sandbox_api.wait_for_sandbox_setup(sandbox_id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        connectivity_params = self.connectivity_params
        sandbox_api = SandboxRESTAPI(connectivity_params.api_service_host, connectivity_params.api_port)
        sandbox_api.login(connectivity_params.username, connectivity_params.password, connectivity_params.domain)
        sandbox_api.stop_sandbox(self.sandbox_id)
