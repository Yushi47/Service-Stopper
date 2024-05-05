# Service Stopper

Service Stopper is a Python script built with Tkinter that allows you to stop Windows services easily through a graphical user interface (GUI). It provides a convenient way to select services from a list and perform actions like stopping them or setting them to manual start.

## Features

- Stop selected services
- Set selected services to manual start
- Add new services with their descriptions
- Remove existing services
- Copy logs to clipboard
- Clear logs

## Installation

### Prerequisites

- Python 3.x installed on your Windows system. You can download it from the [official Python website](https://www.python.org/downloads/).
- Ensure that you are running the script on a Windows machine.

### Steps

1. **Install python on windows**:

    You can install python with the command below. Open a command prompt as an administrator and run the following command to install

    ```batch
    choco install python
    ```

2. **Install pywin32 module**:

    This script utilizes the `pywin32` module to interact with Windows services. If you don't have it installed, you can install it using pip:

    ```batch
    python -m pip install --upgrade pywin32
    ```
and/or the below if didn't work
    ```batch
    python Scripts/pywin32_postinstall.py -install
    ```

3. **Run the script from the batch file**:

    Execute the following batch file:

    ```batch
    run_as_admin_exp.bat
    ```

## Usage

- Upon running the script, a graphical user interface (GUI) will appear.
- You can select services from the list and perform actions using the buttons provided.
- The result of each action will be displayed in the logs area.
- You can add new services by entering their names and descriptions, or remove existing services.
- Logs can be copied to the clipboard or cleared using the respective buttons.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
