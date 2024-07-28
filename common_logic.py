from openpyxl import load_workbook

def xlsx_to_csv(excel_file_path: str) -> tuple:
    wb = load_workbook(excel_file_path)
    sh = wb.active.values
    fields = [] # headers of the sheet
    rest = [] # the data/content of the sheet
    for i, row in enumerate(sh): 
        if i == 0: # if its the first row, it is the fields
            fields = [str(cell) for cell in row if cell != None]
        else: # rest is normal data rows
            rest.append([(u"" if cell == None else str(cell)) for cell in row]) # Ensure empty cells are blanks rather than "None" objects, also convert to string to prevent typing discrepancies
    wb.close()
    return fields, rest 
