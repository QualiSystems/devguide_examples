import datetime
import time
import pprint

from devops_integration.sandbox_api_python_2_and_3.sandbox_api.sandbox_context import QualiConnectivityParams, \
    SandboxContext


def run_some_tests_or_other_code(sandbox):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(sandbox)

    time.sleep(10)


def main():
    """
    Example of using sandbox as a context
    """
    connectivity_params = QualiConnectivityParams('localhost', '8032', 'admin', 'admin', 'Global')

    with SandboxContext(connectivity_params, 'Simple blueprint', datetime.timedelta(hours=2)) as sandbox:
        run_some_tests_or_other_code(sandbox)


if __name__ == "__main__":
    main()
