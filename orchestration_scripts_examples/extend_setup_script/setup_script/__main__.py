from sandbox_scripts.environment.setup.setup_script import EnvironmentSetup
from sandbox_scripts.extensions.setup_extensions import EnvironmentSetupExtensions



def main():
    EnvironmentSetup().execute()
    EnvironmentSetupExtensions().run_post_setup_logic()

if __name__ == "__main__":
    main()
