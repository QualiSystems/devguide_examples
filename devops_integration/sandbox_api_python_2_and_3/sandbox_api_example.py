import datetime
import pprint
import time

from devops_integration.sandbox_api_python_2_and_3.sandbox_api.sandbox_apis import SandboxRESTAPI


def run_some_tests_or_other_code(sandbox):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(sandbox)

    time.sleep(10)

def main():
    """
    Example workflow of starting a sandbox, waiting for it to setup, then stopping it
    :return:
    """
    api_example = SandboxRESTAPI('localhost', '8032')
    api_example.login("admin", "admin", "Global")
    sandbox_id = api_example.start_sandbox('Simple blueprint', datetime.timedelta(hours=2), 'test_sandbox')
    sandox_details = api_example.wait_for_sandbox_setup(sandbox_id)
    run_some_tests_or_other_code(sandox_details)
    api_example.stop_sandbox(sandbox_id)
    api_example.wait_for_sandbox_teardown(sandbox_id)


if __name__ == "__main__":
    main()
