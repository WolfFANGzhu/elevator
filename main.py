import subprocess
import time
import argparse

def run_command(command):
    subprocess.Popen(f'start cmd /k {command}', shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run specified test commands.')
    parser.add_argument('--test', type=str,default='main', help='The test to run:  main, door, main_src, scheduling, control_unit, elevator_unit')

    args = parser.parse_args()

    if args.test == 'main':
        # Start the main application
        run_command("python -m src.main")
    elif args.test == 'door':
        # Run the elevator door unit tests
        run_command("python -m src.main")
        time.sleep(5)
        run_command("python -m tests.functional.door_test")
    elif args.test == 'main_src':
        # Run the main source file
        run_command("python -m src.main")
        time.sleep(5)
        run_command("python -m tests.functional.passengerTest")
    elif args.test == 'scheduling':
        # Run the scheduling tests
        run_command("python -m src.main")
        time.sleep(5)
        run_command("python -m tests.functional.scheduling_test")
    elif args.test == 'control_unit':
        run_command("python -m tests.unit.controllerUnitTest")
    elif args.test == 'elevator_unit':
        run_command("python -m tests.unit.elevatorUnitTest")

    else:
        print("Invalid test option. Available options: main, door, main_src, scheduling, control_unit, elevator_unit")

