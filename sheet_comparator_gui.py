import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # Import ttk for progressbar
import time
import threading
import json
from appdirs import user_data_dir
import os
from sheet_comparator_logic import find_discrepancies, write_issues, compare_csv_folders, compare_csv_folders_single_threaded, write_multiple_issues, write_multiple_issues_single_threaded

TESTING = False
DEFAULT_CONFIG =  { 
                    "output_to_excel": True,
                    "ori": "ori_test", 
                    "upl": "upl_test",
                    "ori_identifier_idx": 1, 
                    "upl_identifier_idx": 1, 
                    "output_folder": os.getcwd(),
                    "ignore_leading_and_trailing_whitespaces": False,
                    }

def save_settings(config_file_path: str, settings: dict):
    """ Saves user settings to a JSON file, creating directories if necessary. """
    # Ensure the directory containing the file exists
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    # Open the file in write mode (will create it if not existing)
    with open(config_file_path, 'w') as f:
        json.dump(settings, f)

def load_settings(defaults: dict, config_file_path: str):
    """ Loads user settings from a JSON file. """
    if not os.path.exists(config_file_path):  
        return defaults
    with open(config_file_path, 'r') as f:
        user_settings =  json.load(f)
        combined_settings = {**defaults, **user_settings} # Merge defaults and user settings, prioritise user settings 
        return combined_settings

def update_progress_bar(progress_value: int) -> None:
    progress_var.set(progress_value)  # Update progress bar value
    root.update_idletasks() # Update the GUI to reflect progress bar change

def update_progress_status(status: str) -> None:
    output_label.config(text=f'{" "*500}')
    output_label.config(text=status)
    root.update_idletasks() # Update the GUI to reflect progress bar change

def compare_sheets_aux(item1_path: str, 
                      item2_path: str, 
                      compare_button: tk.Button, 
                      excel_output: bool,
                      index1_identifier: int,
                      index2_identifier: int,
                      output_dir: str) -> None: 
    
    # Disable the compare button to prevent spamming
    compare_button.config(state=tk.DISABLED)
    progress_var.set(0)
    
    try:
        # Run bulk logic if its a folder path being provided 
        if ( os.path.isdir(item1_path) and os.path.isdir(item2_path) ):
            res = compare_csv_folders_single_threaded(uploaded_folder_path=item2_path,
                                original_folder_path=item1_path,
                                progress_to_show_in_gui=update_progress_bar,
                                status_to_show_in_gui=update_progress_status,
                                uploaded_file_identifying_field_index=index2_identifier,
                                original_file_identifying_field_index=index1_identifier,
                                ignore_leading_and_trailing_whitespaces=ignore_leading_and_trailing_whitespaces_value.get())
            write_multiple_issues_single_threaded(res, update_progress_bar, update_progress_status, output_dir, excel_output)

        # Run single file logic if its a file path being provided
        if ( os.path.isfile(item1_path) and os.path.isfile(item2_path) ):
            res = find_discrepancies(uploaded_file_path=item2_path,
                                    original_file_path=item1_path,
                                    progress_to_show_in_gui=update_progress_bar,
                                    status_to_show_in_gui=update_progress_status,
                                    uploaded_file_identifying_field_index=index2_identifier,
                                    original_file_identifying_field_index=index1_identifier,
                                    ignore_leading_and_trailing_whitespaces=ignore_leading_and_trailing_whitespaces_value.get())
            write_issues(res, output_dir, excel_output, update_progress_bar, update_progress_status)
            
        progress_var.set(100)
    except Exception as e:
        error_type = type(e).__name__
        update_progress_status(f'ERROR: {error_type}: {e}')
        progress_var.set(0)

    compare_button.config(state=tk.NORMAL)
    return

def get_file(file_path_var: tk.StringVar):
    """
    Opens a file explorer window and sets the selected file path to the entry widget.
    """
    file_path = filedialog.askopenfilename(
        title="Select CSV or Excel file",
        filetypes=(
            ("Excel Files", "*.xlsx"),
            ("CSV Files", "*.csv"),
        )
    )    
    if file_path:
        file_path_var.set(file_path)

def get_directory(file_path_var: tk.StringVar):
    """
    Opens a file explorer window and sets the selected file path to the entry widget.
    """
    file_path = filedialog.askdirectory()
    if file_path:
        file_path_var.set(file_path)

def compare_button_click():
    file1_path = file1_var.get()
    file2_path = file2_var.get()
    index1_identifier = index1_var.get() - 1
    index2_identifier = index2_var.get() - 1
    excel_output = use_excel.get()
    output_dir = output_dir_var.get()

    if file1_path == ""  or file2_path == "":
        output_label.config(text='Please select both CSV files first.')
        return 

    if not ( ( os.path.isfile(file1_path) and os.path.isfile(file2_path) ) or ( os.path.isdir(file1_path) and os.path.isdir(file2_path) ) ): 
        output_label.config(text='Cannot find files. Please check the file path for both CSVs.')
        return
    
    if not os.path.isdir(output_dir): 
        output_label.config(text='Cannot find folder for output.')
        return

    comparison_thread = threading.Thread(target=compare_sheets_aux, args=(file1_path, 
                                                                file2_path, 
                                                                compare_button, 
                                                                excel_output, 
                                                                index1_identifier,
                                                                index2_identifier,
                                                                output_dir))
    
    comparison_thread.start()
        
def validate_is_number(P):
    """Validates input to ensure only numbers are entered."""
    return P.isdigit() or P == ""

if __name__ == "__main__":
    app_name = 'Sheet Comparator'
    # Get the platform-specific configuration directory
    config_dir = user_data_dir(appname=app_name, appauthor='seanntxj', roaming=False)  
    # Construct the configuration file path
    config_file_path = os.path.join(config_dir, 'config.json')
    config = load_settings(DEFAULT_CONFIG, config_file_path)

    # Window and widgets
    root = tk.Tk()
    root.title("Sheet Comparator")
    root.geometry('870x190')
    use_excel = tk.BooleanVar(value=config["output_to_excel"])  # Boolean variable, initially True (checked)
    ignore_leading_and_trailing_whitespaces_value = tk.BooleanVar(value=config["ignore_leading_and_trailing_whitespaces"])

    file_selector_frame = tk.Frame(root)
    file_selector_frame.pack(fill=tk.X, pady=10)

    # Frame for first CSV file selection
    file1_frame = tk.Frame(file_selector_frame)
    file1_frame.pack(fill=tk.X, padx=25)

    file1_label = tk.Label(file1_frame, text="Select original file:")
    file1_label.pack(side=tk.LEFT)  # Pack label to the left

    file1_var = tk.StringVar()
    file1_var.set(config["ori"])
    file1_textbox = tk.Entry(file1_frame, textvariable=file1_var)
    file1_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)  # Pack textbox to left, fill remaining space

    file1_browse_button = tk.Button(file1_frame, text="File", command=lambda: get_file(file1_var))
    file1_browse_button.pack(side=tk.LEFT)  

    file1_browse_folder_button = tk.Button(file1_frame, text="Folder", command=lambda: get_directory(file1_var))
    file1_browse_folder_button.pack(side=tk.LEFT)  

    index1_label = tk.Label(file1_frame, text="Index:")
    index1_label.pack(side=tk.LEFT, padx=10)  

    index1_var = tk.IntVar()
    index1_var.set(int(config["ori_identifier_idx"]))
    index1_textbox = tk.Entry(file1_frame, width=5, textvariable=index1_var, validate="key", validatecommand=(file1_frame.register(validate_is_number), "%P"))
    index1_textbox.pack(side=tk.LEFT)

    # Frame for second CSV file selection
    file2_frame = tk.Frame(file_selector_frame)
    file2_frame.pack(fill=tk.X, padx=25)

    file2_label = tk.Label(file2_frame, text="Select uploaded file:")
    file2_label.pack(side=tk.LEFT)  # Pack label to the left

    file2_var = tk.StringVar()
    file2_var.set(config["upl"])
    file2_textbox = tk.Entry(file2_frame, textvariable=file2_var)
    file2_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)  # Pack textbox to left, fill remaining space

    file2_browse_button = tk.Button(file2_frame, text="File", command=lambda: get_file(file2_var))
    file2_browse_button.pack(side=tk.LEFT)  # Pack button to right

    file2_browse_folder_button = tk.Button(file2_frame, text="Folder", command=lambda: get_directory(file2_var))
    file2_browse_folder_button.pack(side=tk.LEFT)  

    index2_label = tk.Label(file2_frame, text="Index:")
    index2_label.pack(side=tk.LEFT, padx=10)  

    index2_var = tk.IntVar()
    index2_var.set(int(config["upl_identifier_idx"]))
    index2_textbox = tk.Entry(file2_frame, width=5,textvariable=index2_var, validate="key", validatecommand=(file2_frame.register(validate_is_number), "%P"))
    index2_textbox.pack(side=tk.LEFT)

    # Frame for outfile file location
    output_dir_frame = tk.Frame(file_selector_frame)
    output_dir_frame.pack(fill=tk.X, padx=25)

    output_dir_label = tk.Label(output_dir_frame, text="Select output folder:")
    output_dir_label.pack(side=tk.LEFT)  # Pack label to the left

    output_dir_var = tk.StringVar()
    output_dir_var.set(config["output_folder"])
    output_dir_textbox = tk.Entry(output_dir_frame, textvariable=output_dir_var)
    output_dir_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)  # Pack textbox to left, fill remaining space

    output_dir_browse_button = tk.Button(output_dir_frame, text="Folder", command=lambda: get_directory(output_dir_var))
    output_dir_browse_button.pack(side=tk.LEFT) 

    # Progress bar placed below the frame for file selections
    progress_frame = tk.Frame(root,borderwidth=0.5, relief="flat")
    progress_frame.pack(fill=tk.X, padx=25)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(progress_frame, maximum=100, variable=progress_var)
    progress_bar.pack(fill=tk.X)  # Pack the progress bar with padding

    output_label = tk.Label(progress_frame, text="")
    output_label.pack(fill=tk.X)

    # Bottom options frame
    bottom_options_frame = tk.Frame(root)
    bottom_options_frame.pack(fill=tk.X)

    excel_checkbox = tk.Checkbutton(
        bottom_options_frame, text="Output to Excel", variable=use_excel
    )
    excel_checkbox.pack(side=tk.LEFT, padx=25)

    ignore_leading_and_trailing_whitespaces_checkbox = tk.Checkbutton(
        bottom_options_frame, text="Ignore whitespaces", variable=ignore_leading_and_trailing_whitespaces_value
    )
    ignore_leading_and_trailing_whitespaces_checkbox.pack(side=tk.LEFT, padx=25)

    compare_button = tk.Button(bottom_options_frame, text="Compare", command=compare_button_click)
    compare_button.pack(side=tk.RIGHT, padx=25)

    root.mainloop()

    save_settings(config_file_path, { 
       "output_to_excel": use_excel.get(),
       "ori": file1_var.get(), 
       "upl": file2_var.get(),
       "ori_identifier_idx": index1_var.get(),
       "upl_identifier_idx": index2_var.get(),
       "output_folder": output_dir_var.get(),
       "ignore_leading_and_trailing_whitespaces": ignore_leading_and_trailing_whitespaces_value.get()
    })