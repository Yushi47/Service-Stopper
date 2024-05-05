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

- Python 3.x installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

### Steps

1. **Clone the repository**:

    ```bash
    git clone https://github.com/Fatvallon/Service-Stopper.git
    ```

2. **Navigate to the project directory**:

    ```bash
    cd servicestopper
    ```

3. **Install required dependencies**:

    You can install the required dependencies using pip. Run the following command:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the script**:

    Run the following command to start the Service Stopper:

    ```bash
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
