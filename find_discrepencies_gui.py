import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # Import ttk for progressbar
import time
import threading
import os
from find_discrepencies import find_discrepencies, write_issues, write_issues_to_excel, compare_csv_folders, write_multiple_issues

TESTING = False
DEFAULT_ORI = 'ori.csv'
DEFAULT_UPL = 'upl2.csv'

def compare_csv_files(file1_path: str, 
                      file2_path: str, 
                      progress_var: tk.IntVar, 
                      output_label: tk.Label, 
                      compare_button: tk.Button, 
                      excel_output: bool,
                      index1_identifier: int,
                      index2_identifier: int,
                      output_dir: str):
    def update_progress_bar(progress_value: int) -> None:
        progress_var.set(progress_value)  # Update progress bar value
        root.update_idletasks() # Update the GUI to reflect progress bar change
    
    def update_progress_status(status: str) -> None:
        output_label.config(text=f'{" "*500}')
        output_label.config(text=status)
        root.update_idletasks() # Update the GUI to reflect progress bar change

    compare_button.config(state=tk.DISABLED)

    if TESTING: # Simulate some progress for demonstration
        for i in range(100):
            update_progress_bar(i + 1) 
            time.sleep(0.02)  # Simulate some processing time (replace with actual comparison logic)
    else: # Run actual comparison
        res = find_discrepencies(file2_path, file1_path, update_progress_bar, update_progress_status, index1_identifier, index2_identifier)

    if len(res.issue_list) > 0:
        if excel_output:
            update_progress_status('Writing to Excel, if this takes too long, use text.')
            write_issues_to_excel(res.issue_list, res.original_fields ,progress_bar=update_progress_bar, output_dir=output_dir, name=res.name)
        else:
            update_progress_status('Writing to text file.')
            write_issues(res.issue_list, output_dir=output_dir, name=res.name)

    # Update status
    if res.has_issues():
        update_progress_status(f"Discrepencies found: {res.name}")
    else: 
        update_progress_status(f"Clear: {res.name}")
        
    compare_button.config(state=tk.NORMAL)
    progress_var.set(100)
    return

def compare_csv_folder(folder1_path: str, 
                      folder2_path: str, 
                      progress_var: tk.IntVar, 
                      output_label: tk.Label, 
                      compare_button: tk.Button, 
                      excel_output: bool,
                      index1_identifier: int,
                      index2_identifier: int,
                      output_dir: str):
    def update_progress_bar(progress_value: int) -> None:
        progress_var.set(progress_value)  # Update progress bar value
        root.update_idletasks() # Update the GUI to reflect progress bar change
    
    def update_progress_status(status: str) -> None:
        output_label.config(text=f'{" "*500}')
        output_label.config(text=status)
        root.update_idletasks() # Update the GUI to reflect progress bar change

    compare_button.config(state=tk.DISABLED)

    if TESTING: # Simulate some progress for demonstration
        for i in range(100):
            update_progress_bar(i + 1) 
            time.sleep(0.02)  # Simulate some processing time (replace with actual comparison logic)
    else: # Run actual comparison
        try:
            res_list = compare_csv_folders(folder2_path, folder1_path, update_progress_bar, update_progress_status, index1_identifier, index2_identifier)
            write_multiple_issues(res_list, update_progress_bar, output_dir, excel_output)
        except KeyError as e: 
            update_progress_status(f'Cannot find the matching file for {e.args[0]}')

    compare_button.config(state=tk.NORMAL)
    progress_var.set(100)
    return

def get_csv_file(file_path_var: tk.StringVar):
    """
    Opens a file explorer window and sets the selected file path to the entry widget.
    """
    file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV Files", "*.csv")])
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
    
    if ( os.path.isdir(file1_path) and os.path.isdir(file2_path) ):
        comparison_thread = threading.Thread(target=compare_csv_folder, args=(file1_path, 
                                                                    file2_path, 
                                                                    progress_var, 
                                                                    output_label, 
                                                                    compare_button, 
                                                                    excel_output,
                                                                    index1_identifier,
                                                                    index2_identifier,
                                                                    output_dir))
    
    if ( os.path.isfile(file1_path) and os.path.isfile(file2_path) ):
        # Run comparison in a separate thread
        comparison_thread = threading.Thread(target=compare_csv_files, args=(file1_path, 
                                                                            file2_path, 
                                                                            progress_var, 
                                                                            output_label, 
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
    # Window and widgets
    root = tk.Tk()
    root.title("CSV Comparison Tool")
    root.geometry('600x170')
    use_excel = tk.BooleanVar(value=True)  # Boolean variable, initially True (checked)

    file_selector_frame = tk.Frame(root)
    file_selector_frame.pack(fill=tk.X, pady=10)

    # Frame for first CSV file selection
    file1_frame = tk.Frame(file_selector_frame)
    file1_frame.pack(fill=tk.X, padx=25)

    file1_label = tk.Label(file1_frame, text="Select original CSV file:")
    file1_label.pack(side=tk.LEFT)  # Pack label to the left

    file1_var = tk.StringVar()
    file1_var.set(DEFAULT_ORI)
    file1_textbox = tk.Entry(file1_frame, textvariable=file1_var)
    file1_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)  # Pack textbox to left, fill remaining space

    file1_browse_button = tk.Button(file1_frame, text="File", command=lambda: get_csv_file(file1_var))
    file1_browse_button.pack(side=tk.LEFT)  

    file1_browse_folder_button = tk.Button(file1_frame, text="Folder", command=lambda: get_directory(file1_var))
    file1_browse_folder_button.pack(side=tk.LEFT)  

    index1_label = tk.Label(file1_frame, text="Index:")
    index1_label.pack(side=tk.LEFT, padx=10)  

    index1_var = tk.IntVar()
    index1_var.set(1)
    index1_textbox = tk.Entry(file1_frame, width=5, textvariable=index1_var, validate="key", validatecommand=(file1_frame.register(validate_is_number), "%P"))
    index1_textbox.pack(side=tk.LEFT)

    # Frame for second CSV file selection
    file2_frame = tk.Frame(file_selector_frame)
    file2_frame.pack(fill=tk.X, padx=25)

    file2_label = tk.Label(file2_frame, text="Select uploaded CSV file:")
    file2_label.pack(side=tk.LEFT)  # Pack label to the left

    file2_var = tk.StringVar()
    file2_var.set(DEFAULT_UPL)
    file2_textbox = tk.Entry(file2_frame, textvariable=file2_var)
    file2_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)  # Pack textbox to left, fill remaining space

    file2_browse_button = tk.Button(file2_frame, text="File", command=lambda: get_csv_file(file2_var))
    file2_browse_button.pack(side=tk.LEFT)  # Pack button to right

    file2_browse_folder_button = tk.Button(file2_frame, text="Folder", command=lambda: get_directory(file2_var))
    file2_browse_folder_button.pack(side=tk.LEFT)  

    index2_label = tk.Label(file2_frame, text="Index:")
    index2_label.pack(side=tk.LEFT, padx=10)  

    index2_var = tk.IntVar()
    index2_var.set(1)
    index2_textbox = tk.Entry(file2_frame, width=5,textvariable=index2_var, validate="key", validatecommand=(file2_frame.register(validate_is_number), "%P"))
    index2_textbox.pack(side=tk.LEFT)

    # Frame for outfile file location
    output_dir_frame = tk.Frame(file_selector_frame)
    output_dir_frame.pack(fill=tk.X, padx=25)

    output_dir_label = tk.Label(output_dir_frame, text="Select output folder:")
    output_dir_label.pack(side=tk.LEFT)  # Pack label to the left

    output_dir_var = tk.StringVar()
    output_dir_var.set(f'{os.getcwd()}')
    output_dir_textbox = tk.Entry(output_dir_frame, textvariable=output_dir_var)
    output_dir_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)  # Pack textbox to left, fill remaining space

    output_dir_browse_button = tk.Button(output_dir_frame, text="Browse", command=lambda: get_directory(output_dir_var))
    output_dir_browse_button.pack(side=tk.LEFT)  # Pack button to right

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, maximum=100, variable=progress_var)
    progress_bar.pack(fill=tk.X, padx=25)  # Pack the progress bar with padding

    excel_checkbox = tk.Checkbutton(
        root, text="Output to Excel", variable=use_excel
    )
    excel_checkbox.pack(side=tk.LEFT, padx=25)

    compare_button = tk.Button(root, text="Compare", command=compare_button_click)
    compare_button.pack(side=tk.RIGHT, padx=25)

    output_label = tk.Label(root, text="")
    output_label.pack()

    root.mainloop()