import subprocess
import time

def run_command(command):
    subprocess.Popen(f'start cmd /k {command}', shell=True)

if __name__ == "__main__":
    # Start the main application
    run_command("python -m main")

    # Give the main application some time to start up
    time.sleep(2)

    # Run the elevator unit tests
    run_command("python -m project.tests.functional.functionalTest")

    # Optionally, run the functional tests
    # run_command("python -m unittest project.tests.unit.elevatorUnitTest")
    # run_command("python -m project.tests.functional.functionalTest")
