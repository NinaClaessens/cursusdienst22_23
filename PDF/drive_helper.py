import openpyxl
import cursus
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

FILE_ID = "1gpryvBvfH31uZ7RAHPCw5WQdNKNU8sbmZ6GE96wpm-g"

#gauth = GoogleAuth()
#gauth.LocalWebserverAuth()

#drive = GoogleDrive(gauth)

#file = drive.CreateFile({'id': FILE_ID})
#file.GetContentFile('cursussen.xlsx', mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

wb = openpyxl.load_workbook('cursussen.xlsx')
ws = wb.active

first = True
for i, row in enumerate(ws.iter_rows(min_row=2)):
    if row[0].value is not None and row[1].value is not None and (type(row[1].value) is float or type(row[1].value) is int) and row[2].value is not None and row[3].value != "ok":
        if row[2].value.lower().strip() == 'zelfde':
            if first:
                first = False
                c = cursus.Cursus(True, 25011, 0, False)
                c.update()
# file.SetContentFile('cursussen_adapted.xlsx')
# file.Upload()  # Upload the file.

