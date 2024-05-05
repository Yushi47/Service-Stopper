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

1. **Clone the repository**:

    ```batch
    git clone https://github.com/yourusername/servicestopper.git
    ```

2. **Navigate to the project directory**:

    ```batch
    cd servicestopper
    ```

3. **Install required dependencies**:

    You can install the required dependencies using pip. Run the following command:

    ```batch
    pip install -r requirements.txt
    ```

4. **Install pywin32 module**:

    This script utilizes the `pywin32` module to interact with Windows services. If you don't have it installed, you can install it using pip:

    ```batch
    pip install pywin32
    ```

5. **Run the script**:

    Execute the following command in your command prompt to start the Service Stopper:

    ```batch
    python service_stopper.py
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
