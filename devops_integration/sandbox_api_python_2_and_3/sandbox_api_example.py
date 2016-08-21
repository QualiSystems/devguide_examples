import datetime

from devops_integration.sandbox_api_python_2_and_3.sandbox_api.sandbox_apis import SandboxRESTAPI


def main():
    """
    Example workflow of starting a sandbox, waiting for it to setup, then stopping it
    :return:
    """
    api_example = SandboxRESTAPI('localhost', '8032')
    api_example.login("admin", "admin", "Global")
    sandbox_id = api_example.start_sandbox('Simple blueprint', datetime.timedelta(hours=2), 'test_sandbox')
    api_example.wait_for_sandbox_setup(sandbox_id)
    api_example.stop_sandbox(sandbox_id)
    api_example.wait_for_sandbox_teardown(sandbox_id)


if __name__ == "__main__":
    main()
