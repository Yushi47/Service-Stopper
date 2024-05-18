# Service Stopper

This script provides a graphical user interface (GUI) to stop and configure services on a Windows system using tkinter.

## Features
- Stop services
- Set services to manual start
- Select all services
- Clear selection
- Select recommended services
- Search for services
- Copy logs to clipboard
- Clear logs

## Dependencies
- Python 3
- tkinter (Python standard library)
- subprocess (Python standard library)
- threading (Python standard library)
- logging (Python standard library)

## How to Use

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
    run_as_admin_ui_2.0.bat
    ```
4. Use the GUI to select the desired services and perform actions such as stopping, setting to manual start, etc.
5. Use the search feature to filter services.
6. Use the "Recommended" button to select recommended services.

## Recommended Services
The following services are marked as recommended:
- DPS
- WdiServiceHost
- WdiSystemHost
- BITS
- wuauserv
- WaaSMedicSvc
- XblAuthManager
- XboxNetApiSvc
- ClickToRunSvc
- Spooler

<p align="Center">
<a href="#">
<img src="https://cdn.discordapp.com/attachments/516495873807482890/1241188486875320470/image.png?ex=66494a5b&is=6647f8db&hm=b174440cd33d0e60875a32865f78e50f1784f0e74ef722b2099e5790bc221665&" width="1000" height="300" alt="logo"/>
</a>
</p>

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
