import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # Import ttk for progressbar
import time
import threading
from find_discrepencies_with_progress_bar import find_discrepencies, write_issues

TESTING = False

def compare_csv_files(file1_path: str, file2_path: str, progress_var: tk.IntVar, output_label: tk.Label, compare_button: tk.Button):
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
        res = find_discrepencies(file2_path, file1_path, update_progress_bar, update_progress_status)

    if len(res.issue_list) > 0:
        write_issues(res.issue_list)

    update_progress_status(res.status.value)
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

def compare_button_click():
    file1_path = file1_var.get()
    file2_path = file2_var.get()

    if file1_path == ""  or file2_path == "":
        output_label.config(text='Please select both CSV files first.')
        return 
    
    # Run comparison in a separate thread
    comparison_thread = threading.Thread(target=compare_csv_files, args=(file1_path, file2_path, progress_var, output_label, compare_button))
    comparison_thread.start()
    return

if __name__ == "__main__":
    # Window and widgets
    root = tk.Tk()
    root.title("CSV Comparison Tool")
    root.geometry('800x120')

    # Frame for first CSV file selection
    file1_frame = tk.Frame(root)
    file1_frame.pack(fill=tk.X, padx=25)

    file1_label = tk.Label(file1_frame, text="Select original CSV file:")
    file1_label.pack(side=tk.LEFT)  # Pack label to the left

    file1_var = tk.StringVar()
    file1_var.set('ori.csv')
    file1_textbox = tk.Entry(file1_frame, textvariable=file1_var)
    file1_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)  # Pack textbox to left, fill remaining space

    file1_browse_button = tk.Button(file1_frame, text="Browse", command=lambda: get_csv_file(file1_var))
    file1_browse_button.pack(side=tk.RIGHT)  # Pack button to right

    file2_frame = tk.Frame(root)
    file2_frame.pack(fill=tk.X, padx=25)

    file2_label = tk.Label(file2_frame, text="Select uploaded CSV file:")
    file2_label.pack(side=tk.LEFT)

    file2_var = tk.StringVar()
    file2_var.set('uploaded.csv')
    file2_textbox = tk.Entry(file2_frame, textvariable=file2_var)
    file2_textbox.pack(side=tk.LEFT, fill=tk.X, padx=10, expand=True)

    file2_browse_button = tk.Button(file2_frame, text="Browse", command=lambda: get_csv_file(file2_var))
    file2_browse_button.pack(side=tk.RIGHT)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, maximum=100, variable=progress_var)
    progress_bar.pack(fill=tk.X, padx=25)  # Pack the progress bar with padding

    compare_button = tk.Button(root, text="Compare", command=compare_button_click)
    compare_button.pack()

    output_label = tk.Label(root, text="")
    output_label.pack()

    root.mainloop()