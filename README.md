## Usage

### Running the Main Program

To run the main program, navigate to the project's root directory and execute the following command:

```bash
python -m main
```

### Running Tests

To run the tests, follow the steps below:

1. Open the file `project/tests/run_test.py` in your text editor.

2. Paste the appropriate command for the test you want to run. For example:

   For the `elevator` module's unit test:

   ```bash
   python -m unittest project.tests.unit.elevatorUnitTest
   ```

   For the system's functional test:

   ```bash
   python -m project.tests.functional.functionalTest
   ```

3. Save and close `run_test.py`.

4. Open a terminal, navigate to the project's root directory, and run the following command:

   ```bash
   python -m project.tests.run_test
   ```