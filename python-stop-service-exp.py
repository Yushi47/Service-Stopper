import tkinter as tk
import subprocess
import threading
import tkinter.messagebox as messagebox
import logging

# List of service names and their descriptions
services_info = {
    "DPS": "Diagnostic Policy Service",
    "WdiServiceHost": "Diagnostic Service Host Service",
    "WdiSystemHost": "Diagnostic System Host Service",
    "BITS": "Background Intelligent Transfer Service",
    "wuauserv": "Windows Update",
    "WaaSMedicSvc": "Windows Update Medic Service",
    "XblAuthManager": "Xbox Live Auth Manager",
    "XboxNetApiSvc": "Xbox Live Networking Service",
    "ClickToRunSvc": "Microsoft Office Click-to-Run Service",
    "Spooler": "Print Spooler Service"
}

# Define global variables for checkboxes and labels
service_checkboxes = []
service_labels = []

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and set it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Set to keep track of processed services
processed_services = set()

# Function to execute subprocess command and handle errors
def execute_command(command, result_text, success_msg, error_msg):
    try:
        logger.debug(f"Executing command: {' '.join(command)}")
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.debug(f"Command output: {output.stdout}")
        result_text.insert(tk.END, success_msg.format(output.stdout), "green")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")
        result_text.insert(tk.END, error_msg.format(e), "red")

# Function to stop a service
def stop_service(service_name, result_text):
    try:
        if service_name in processed_services:
            return  # Skip if already processed
        processed_services.add(service_name)
        
        logger.info(f"Attempting to stop service: {service_name}")
        stop_output = subprocess.run(["sc", "stop", service_name], capture_output=True, text=True)
        if stop_output.returncode == 0:
            result_text.insert(tk.END, f"The {service_name} service has stopped successfully.\n", "green")
        elif stop_output.returncode == 1062:
            result_text.insert(tk.END, f"The {service_name} service is already off.\n", "yellow")
        else:
            result_text.insert(tk.END, f"Failed to stop the {service_name} service: {stop_output.stderr}\n", "red")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error stopping service: {e}")
        result_text.insert(tk.END, f"Failed to stop the {service_name} service: {e}\n", "red")

# Function to set a service to manual start
def set_manual(service_name, result_text):
    try:
        if service_name in processed_services:
            return  # Skip if already processed
        processed_services.add(service_name)
        
        logger.info(f"Setting service {service_name} to Manual start")
        execute_command(["sc", "config", service_name, "start=", "demand"], result_text,
                        f"The {service_name} service has been set to Manual start.\n",
                        f"Failed to set the {service_name} service to Manual start: {{}}\n")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting service to Manual start: {e}")
        result_text.insert(tk.END, f"Failed to set the {service_name} service to Manual start: {e}\n", "red")

# Function to handle service operations for selected services
def handle_selected_services(result_text, selected_services, operation_func, success_msg):
    # Clear previous results
    result_text.delete(1.0, tk.END)
    
    # Clear processed services set
    processed_services.clear()

    # Check if any service is selected
    selected_count = sum(checkbox_var.get() for _, checkbox_var in selected_services)
    if selected_count == 0:
        result_text.insert(tk.END, "No services selected.\n")
        return

    # Log to console
    logger.info(f"{success_msg}...")

    # Start operation for selected services
    for service_name, checkbox_var in selected_services:
        if checkbox_var.get():
            threading.Thread(target=operation_func, args=(service_name, result_text), daemon=True).start()

# Function to clear the result text area
def clear_logs(result_text):
    result_text.delete(1.0, tk.END)

# Function to select all services
def select_all(selected_services):
    for _, checkbox_var in selected_services:
        checkbox_var.set(True)

# Function to clear selection of all services
def clear_selection(selected_services):
    for _, checkbox_var in selected_services:
        checkbox_var.set(False)

# Function to copy logs to clipboard
def copy_logs(result_text):
    logs = result_text.get("1.0", tk.END)
    window.clipboard_clear()
    window.clipboard_append(logs)
    messagebox.showinfo("Copy Logs", "Logs copied to clipboard.")

# Function to add a new service
def add_service():
    service_name = service_name_entry.get()
    service_desc = service_desc_entry.get()
    
    if service_name and service_desc:
        if service_name not in services_info:
            services_info[service_name] = service_desc
            update_services_list()
            clear_selection(selected_services)  # Clear selection after addition
        else:
            result_text.insert(tk.END, "Service already exists.\n", "red")
    else:
        result_text.insert(tk.END, "Please enter both service name and description.\n", "red")

# Function to remove a service
def remove_service():
    service_name = service_name_entry.get()
    if service_name in services_info:
        del services_info[service_name]
        update_services_list()
        clear_selection(selected_services)  # Clear selection after removal

# Function to update the services list
def update_services_list():
    # Destroy existing checkboxes and labels
    for checkbox, label in zip(service_checkboxes, service_labels):
        checkbox.destroy()
        label.destroy()

    # Clear the lists
    service_checkboxes.clear()
    service_labels.clear()

    # Re-populate the services list
    for service_name, service_desc in services_info.items():
        checkbox_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(services_frame, text=service_name, variable=checkbox_var, bg="#333333", fg="white", selectcolor="#444444")
        checkbox.pack(anchor=tk.W, padx=10, pady=2)
        service_checkboxes.append(checkbox)

        # Create a label for service description
        desc_label = tk.Label(services_frame, text=service_desc, font=("Helvetica", 8), bg="#333333", fg="gray")
        desc_label.pack(anchor=tk.W, padx=30, pady=(0, 5))
        service_labels.append(desc_label)

        selected_services.append((service_name, checkbox_var))

def stop_selected_services(result_text, selected_services):
    handle_selected_services(result_text, selected_services, stop_service, "Stopping services")

def set_manual_selected_services(result_text, selected_services):
    handle_selected_services(result_text, selected_services, set_manual, "Setting services to Manual start")

# Create a tkinter window
window = tk.Tk()
window.title("Service Stopper")
window.configure(bg="#333333")  # Set dark background color

# Create a frame for services
services_frame = tk.Frame(window, bg="#333333")
services_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Checkboxes for selecting services
selected_services = []

update_services_list()

# Create a frame for buttons
button_frame = tk.Frame(window, bg="#333333")
button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

# Create buttons with a different font
button_font = ("Inconsolata", 10)  # Specify the desired font family and size

stop_button = tk.Button(button_frame, text="Stop", command=lambda: stop_selected_services(result_text, selected_services), bg="#1F1F23", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
stop_button.pack(pady=5, fill=tk.X)

set_manual_button = tk.Button(button_frame, text="Set to Manual", command=lambda: set_manual_selected_services(result_text, selected_services), bg="#1F1F23", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
set_manual_button.pack(pady=5, fill=tk.X)

select_all_button = tk.Button(button_frame, text="Select All", command=lambda: select_all(selected_services), bg="#1F1F23", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
select_all_button.pack(pady=5, fill=tk.X)

clear_selection_button = tk.Button(button_frame, text="Clear Selection", command=lambda: clear_selection(selected_services), bg="#1F1F23", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
clear_selection_button.pack(pady=5, fill=tk.X)

# Separator between the above buttons and the logs buttons
separator = tk.Frame(button_frame, height=2, bg="gray")
separator.pack(fill=tk.X, padx=10, pady=10)

copy_logs_button = tk.Button(button_frame, text="Copy Logs", command=lambda: copy_logs(result_text), bg="#1F1F23", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
copy_logs_button.pack(pady=5, fill=tk.X)

clear_logs_button = tk.Button(button_frame, text="Clear Logs", command=lambda: clear_logs(result_text), bg="#850000", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
clear_logs_button.pack(pady=5, fill=tk.X)

# Create a separator between the under buttons and the logs buttons
separator2 = tk.Frame(button_frame, height=2, bg="gray")
separator2.pack(fill=tk.X, padx=10, pady=10)

# Create entry and buttons for adding/removing services
service_name_label = tk.Label(button_frame, text="Service Name:", bg="#333333", fg="white")
service_name_label.pack(pady=(20, 5), fill=tk.X)
service_name_entry = tk.Entry(button_frame, bg="white", width=30)
service_name_entry.pack(pady=5, fill=tk.X)

service_desc_label = tk.Label(button_frame, text="Service Description:", bg="#333333", fg="white")
service_desc_label.pack(pady=5, fill=tk.X)
service_desc_entry = tk.Entry(button_frame, bg="white", width=30)
service_desc_entry.pack(pady=5, fill=tk.X)

add_button = tk.Button(button_frame, text="Add Service", command=add_service, bg="#0F4D26", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
add_button.pack(pady=5, fill=tk.X)

remove_button = tk.Button(button_frame, text="Remove Service", command=remove_service, bg="#850000", fg="white", font=button_font, borderwidth=2, relief="groove", highlightthickness=0)
remove_button.pack(pady=5, fill=tk.X)

# Create a frame for result text and scrollbar
result_frame = tk.Frame(window, bg="#333333")
result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create a scrollable text area for displaying logs
result_text = tk.Text(result_frame, height=15, width=70, wrap=tk.WORD, font=("Courier New", 10), bg="#222222", fg="white")
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a scrollbar
scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=result_text.yview)

# Run the tkinter event loop
window.mainloop()
