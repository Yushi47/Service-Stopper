import tkinter as tk
import subprocess
import threading
import tkinter.messagebox as messagebox
import logging

# Constants
BG_COLOR = "#333333"
FG_COLOR = "white"
SELECT_COLOR = "#444444"
SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
FONT_STYLE = ("Helvetica", 8)
BUTTON_FONT = ("Inconsolata", 10)
LOG_FONT = ("Courier New", 10)

# Logger configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables
service_checkboxes = []
service_labels = []

# Define a list of recommended services
recommended_services = ["DPS", "WdiServiceHost", "WdiSystemHost", "BITS", "wuauserv", "WaaSMedicSvc", "XblAuthManager", "XboxNetApiSvc", "ClickToRunSvc", "Spooler"]

# Function to select recommended services
def select_recommended_services():
    for service_name, checkbox_var in selected_services:
        if service_name in recommended_services:
            checkbox_var.set(True)

# Function to execute subprocess command and handle errors
def execute_command(command, result_text, success_msg, error_msg):
    try:
        logger.debug(f"Executing command: {' '.join(command)}")
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.debug(f"Command output: {output.stdout}")
        result_text.insert(tk.END, success_msg.format(output.stdout), SUCCESS_COLOR)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")
        result_text.insert(tk.END, error_msg.format(e), ERROR_COLOR)

# Function to start a service
def start_service(service_name, result_text):
    logger.info(f"Attempting to start service: {service_name}")
    try:
        start_output = subprocess.run(["sc", "start", service_name], capture_output=True, text=True)
        if start_output.returncode == 0:
            result_text.insert(tk.END, f"The {service_name} service has started successfully.\n", SUCCESS_COLOR)
        elif start_output.returncode == 1056:
            result_text.insert(tk.END, f"The {service_name} service is already running.\n", WARNING_COLOR)
        else:
            result_text.insert(tk.END, f"Failed to start the {service_name} service: {start_output.stderr}\n", ERROR_COLOR)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting service: {e}")
        result_text.insert(tk.END, f"Failed to start the {service_name} service: {e}\n", ERROR_COLOR)

# Function to stop a service
def stop_service(service_name, result_text):
    logger.info(f"Attempting to stop service: {service_name}")
    try:
        stop_output = subprocess.run(["sc", "stop", service_name], capture_output=True, text=True)
        if stop_output.returncode == 0:
            result_text.insert(tk.END, f"The {service_name} service has stopped successfully.\n", SUCCESS_COLOR)
        elif stop_output.returncode == 1062:
            result_text.insert(tk.END, f"The {service_name} service is already off.\n", WARNING_COLOR)
        else:
            result_text.insert(tk.END, f"Failed to stop the {service_name} service: {stop_output.stderr}\n", ERROR_COLOR)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error stopping service: {e}")
        result_text.insert(tk.END, f"Failed to stop the {service_name} service: {e}\n", ERROR_COLOR)

# Function to set a service to manual start
def set_manual(service_name, result_text):
    logger.info(f"Setting service {service_name} to Manual start")
    try:
        execute_command(["sc", "config", service_name, "start=", "demand"], result_text,
                        f"The {service_name} service has been set to Manual start.\n",
                        f"Failed to set the {service_name} service to Manual start: {{}}\n")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting service to Manual start: {e}")
        result_text.insert(tk.END, f"Failed to set the {service_name} service to Manual start: {e}\n", ERROR_COLOR)

# Function to set a service to automatic start
def set_automatic(service_name, result_text):
    logger.info(f"Setting service {service_name} to Automatic start")
    try:
        execute_command(["sc", "config", service_name, "start=", "auto"], result_text,
                        f"The {service_name} service has been set to Automatic start.\n",
                        f"Failed to set the {service_name} service to Automatic start: {{}}\n")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting service to Automatic start: {e}")
        result_text.insert(tk.END, f"Failed to set the {service_name} service to Automatic start: {e}\n", ERROR_COLOR)

# Function to select all services
def select_all():
    for checkbox in service_checkboxes:
        checkbox.select()

# Function to clear selection
def clear_selection():
    for checkbox in service_checkboxes:
        checkbox.deselect()

# Function to handle service operations for selected services
def handle_selected_services(result_text, selected_services, operation_func, success_msg):
    result_text.delete(1.0, tk.END)  # Clear previous results
    selected_count = sum(checkbox_var.get() for _, checkbox_var in selected_services)
    if selected_count == 0:
        result_text.insert(tk.END, "No services selected.\n")
        return
    logger.info(f"{success_msg}...")
    for service_name, checkbox_var in selected_services:
        if checkbox_var.get():
            threading.Thread(target=operation_func, args=(service_name, result_text), daemon=True).start()

# Function to clear the result text area
def clear_logs(result_text):
    result_text.delete(1.0, tk.END)

# Function to copy logs to clipboard
def copy_logs(result_text):
    logs = result_text.get("1.0", tk.END)
    window.clipboard_clear()
    window.clipboard_append(logs)
    messagebox.showinfo("Copy Logs", "Logs copied to clipboard.")

# Function to update the services list
def update_services_list():
    global service_checkboxes, service_labels
    search_term = search_entry.get().lower()  # Define search_term here
    try:
        output = subprocess.run(["sc", "query", "state=", "all"], capture_output=True, text=True, check=True)
        services_info = {}
        lines = output.stdout.splitlines()
        for line in lines:
            if "SERVICE_NAME:" in line:
                service_name = line.split(":")[1].strip()
                services_info[service_name] = ""
            elif "DISPLAY_NAME:" in line:
                service_desc = line.split(":")[1].strip()
                services_info[service_name] = service_desc

        filtered_services = {name: desc for name, desc in services_info.items() if search_term in name.lower() or search_term in desc.lower()}

        for checkbox, label in zip(service_checkboxes, service_labels):
            checkbox.destroy()
            label.destroy()
        service_checkboxes.clear()
        service_labels.clear()
        for service_name, service_desc in filtered_services.items():
            checkbox_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(services_frame, text=service_name, variable=checkbox_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=SELECT_COLOR)
            checkbox.pack(anchor=tk.W, padx=10, pady=2)
            service_checkboxes.append(checkbox)
            desc_label = tk.Label(services_frame, text=service_desc, font=FONT_STYLE, bg=BG_COLOR, fg="gray")
            desc_label.pack(anchor=tk.W, padx=30, pady=(0, 5))
            service_labels.append(desc_label)
            selected_services.append((service_name, checkbox_var))
    except subprocess.CalledProcessError as e:
        logger.error(f"Error updating services list: {e}")
        messagebox.showerror("Error", f"Failed to update services list: {e}")

# Function to handle search
def handle_search():
    search_term = search_entry.get().lower()
    if not search_term:
        update_services_list()
    else:
        try:
            output = subprocess.run(["sc", "query", "state=", "all"], capture_output=True, text=True, check=True)
            services_info = {}
            lines = output.stdout.splitlines()
            for line in lines:
                if "SERVICE_NAME:" in line:
                    service_name = line.split(":")[1].strip()
                    services_info[service_name] = ""
                elif "DISPLAY_NAME:" in line:
                    service_desc = line.split(":")[1].strip()
                    services_info[service_name] = service_desc

            filtered_services = {name: desc for name, desc in services_info.items() if search_term in name.lower() or search_term in desc.lower()}

            for checkbox, label in zip(service_checkboxes, service_labels):
                checkbox.destroy()
                label.destroy()
            service_checkboxes.clear()
            service_labels.clear()
            for service_name, service_desc in filtered_services.items():
                checkbox_var = tk.BooleanVar()
                checkbox = tk.Checkbutton(services_frame, text=service_name, variable=checkbox_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=SELECT_COLOR)
                checkbox.pack(anchor=tk.W, padx=10, pady=2)
                service_checkboxes.append(checkbox)
                desc_label = tk.Label(services_frame, text=service_desc, font=FONT_STYLE, bg=BG_COLOR, fg="gray")
                desc_label.pack(anchor=tk.W, padx=30, pady=(0, 5))
                service_labels.append(desc_label)
                selected_services.append((service_name, checkbox_var))
        except subprocess.CalledProcessError as e:
            logger.error(f"Error updating services list: {e}")
            messagebox.showerror("Error", f"Failed to update services list: {e}")

# Create a tkinter window
window = tk.Tk()
window.title("Service Stopper")
window.configure(bg=BG_COLOR)

# Create a frame for search
search_frame = tk.Frame(window, bg=BG_COLOR)
search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Search entry widget
search_entry = tk.Entry(search_frame, bg="white", fg="black", font=FONT_STYLE)
search_entry.pack(side=tk.LEFT, padx=(0, 5))

# Bind Enter key press to handle_search function
search_entry.bind("<Return>", lambda event: handle_search())

# Search button
search_button = tk.Button(search_frame, text="Search", command=handle_search, bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
search_button.pack(side=tk.LEFT)

# Create a canvas widget to contain the services frame
services_canvas = tk.Canvas(window, bg=BG_COLOR)
services_canvas.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y, expand=True)

# Create a frame for services inside the canvas
services_frame = tk.Frame(services_canvas, bg=BG_COLOR)
services_frame.pack(fill=tk.Y, expand=True)

# Create a scrollbar for the canvas
services_scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=services_canvas.yview)
services_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

# Configure the canvas to use the scrollbar
services_canvas.config(yscrollcommand=services_scrollbar.set)
services_canvas.create_window((0, 0), window=services_frame, anchor=tk.NW)
services_frame.bind("<Configure>", lambda event, canvas=services_canvas: canvas.configure(scrollregion=canvas.bbox("all")))

# Checkboxes for selecting services
selected_services = []

# Update services list initially
update_services_list()

# Create a frame for buttons
button_frame = tk.Frame(window, bg=BG_COLOR)
button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

# Create buttons for starting and stopping services
start_button = tk.Button(button_frame, text="Start", command=lambda: handle_selected_services(result_text, selected_services, start_service, "Starting services"), bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
start_button.pack(pady=5, fill=tk.X)

stop_button = tk.Button(button_frame, text="Stop", command=lambda: handle_selected_services(result_text, selected_services, stop_service, "Stopping services"), bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
stop_button.pack(pady=5, fill=tk.X)

# Separator between start/stop and manual/automatic buttons
separator = tk.Frame(button_frame, height=2, bg="gray")
separator.pack(fill=tk.X, padx=10, pady=10)

# Create buttons for setting service start type
set_manual_button = tk.Button(button_frame, text="Set to Manual", command=lambda: handle_selected_services(result_text, selected_services, set_manual, "Setting services to Manual start"), bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
set_manual_button.pack(pady=5, fill=tk.X)

set_automatic_button = tk.Button(button_frame, text="Set to Automatic", command=lambda: handle_selected_services(result_text, selected_services, set_automatic, "Setting services to Automatic start"), bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
set_automatic_button.pack(pady=5, fill=tk.X)

separator = tk.Frame(button_frame, height=2, bg="gray")
separator.pack(fill=tk.X, padx=10, pady=10)

# Create buttons for select all and clear selection
select_all_button = tk.Button(button_frame, text="Select All", command=select_all, bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
select_all_button.pack(pady=5, fill=tk.X)

clear_selection_button = tk.Button(button_frame, text="Clear Selection", command=clear_selection, bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
clear_selection_button.pack(pady=5, fill=tk.X)

separator = tk.Frame(button_frame, height=2, bg="gray")
separator.pack(fill=tk.X, padx=10, pady=10)

copy_logs_button = tk.Button(button_frame, text="Copy Logs", command=lambda: copy_logs(result_text), bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
copy_logs_button.pack(pady=5, fill=tk.X)

clear_logs_button = tk.Button(button_frame, text="Clear Logs", command=lambda: clear_logs(result_text), bg="#1F1F23", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
clear_logs_button.pack(pady=5, fill=tk.X)

separator = tk.Frame(button_frame, height=2, bg="gray")
separator.pack(fill=tk.X, padx=10, pady=10)

# Create the "Recommended" button
recommended_button = tk.Button(button_frame, text="Recommended", command=select_recommended_services, bg="#006400", fg="white", font=BUTTON_FONT, borderwidth=2, relief="groove", highlightthickness=0)
recommended_button.pack(pady=5, fill=tk.X)

# Create a frame for result text and scrollbar
result_frame = tk.Frame(window, bg=BG_COLOR)
result_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create a scrollable text area for displaying logs
result_text = tk.Text(result_frame, height=15, width=70, wrap=tk.WORD, font=LOG_FONT, bg="#222222", fg="white")
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a scrollbar
scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=result_text.yview)

# Run the tkinter event loop
window.mainloop()
