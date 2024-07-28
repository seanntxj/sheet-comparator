import csv 
import sys
import os.path
import time
from enum import Enum
from openpyxl import Workbook, styles, load_workbook
import threading
from queue import Queue, Empty
from common_logic import xlsx_to_csv

class Sheet:
    def __init__(self) -> None:
        self.fields: dict[str] = {} # field_val:column_index
        self.data: list[str] = []


def combine_sheets(fields: list[str] = [],
                   primary_sheet: Sheet = None,
                   sheets: list[Sheet] = []) -> None:
    
    master_output_sheet = Sheet()
    master_output_sheet.fields = fields
    master_output_sheet.data = [fields]*len(primary_sheet.data)
    sheets.insert(0, primary_sheet)
 
    for sheet in sheets:
        # For every col in the final sheet
        for col in fields:
            # Find the same row in current sheet
            idx_col_current_sheet = sheet.fields[col]
            for idx_row_master_sheet in range(len(master_output_sheet.data)):
                x = sheet.data[idx_col_current_sheet][idx_row_master_sheet] 
    return 



if __name__ == "__main__": 
    x = Sheet()
    x.fields = {'test1': 0, 'test2': 1, 'test3': 2}
    x.data = [['data1', 'd2', 'd3'], ['dx1', 'fx2']]

    y = Sheet()
    y.fields = {'dee1': 0, 'dee2': 1, 'dee3': 2}
    y.data = [['aaaata1', 'aaa2', 'aaa3'], ['aaax1', 'fx2']]

    f = ['test1', 'test2', 'test3', 'test4']
    combine_sheets(f, x, [y])
    pass