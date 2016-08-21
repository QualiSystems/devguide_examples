import time


class SandboxHelpers:
    def wait_for_sandbox_setup(self,sandbox_id, session, polling_interval):
        sandbox = session.GetReservationDetails(reservationId=sandbox_id).ReservationDescription
        while sandbox.ProvisioningStatus != 'Ready':
            if sandbox.ProvisioningStatus not in ['Not Run', 'Setup']:
                raise Exception('Unknown or error setup state {state}'.format(state=sandbox.ProvisioningStatus))
            time.sleep(polling_interval)
            sandbox = session.GetReservationDetails(reservationId=sandbox.Id).ReservationDescription
        return sandbox
