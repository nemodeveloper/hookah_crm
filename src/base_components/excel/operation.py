from openpyxl.styles import Alignment, Border, Side


class BaseExcelOperation(object):

    def centre_cell_value(self, cell):
        cell.alignment = cell.alignment.copy(horizontal='center', vertical='center')

    def set_border(self, sheet, min_row, max_row):
        border = Border(left=Side(border_style='thin', color='000000'),
                        right=Side(border_style='thin', color='000000'),
                        top=Side(border_style='thin', color='000000'),
                        bottom=Side(border_style='thin', color='000000'))

        for row in sheet.iter_rows(min_row=min_row, max_row=max_row):
            for cell in row:
                cell.border = border

    def centre_value(self, sheet, min_row, max_row):
        for row in sheet.iter_rows(min_row=min_row, max_row=max_row):
            for cell in row:
                self.centre_cell_value(cell)

    def post_process_sheet(self, sheet):
        dims = {}
        for row in sheet.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))
        for col, value in dims.items():
            sheet.column_dimensions[col].width = value + 5
