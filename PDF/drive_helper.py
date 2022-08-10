import openpyxl
import cursus
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

FILE_ID = "1gpryvBvfH31uZ7RAHPCw5WQdNKNU8sbmZ6GE96wpm-g"
FOLDER_ID = "1OjkrY8dj3LbRaxJ3BKKj07xpr8dokfxn"

gauth = GoogleAuth()
# gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

file = drive.CreateFile({'id': FILE_ID})
file.GetContentFile('cursussen.xlsx', mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

wb = openpyxl.load_workbook('cursussen.xlsx')
ws = wb.active

subfolders = drive.ListFile({'q': "'{}' in parents and trashed=false".format(FOLDER_ID)}).GetList()
for folder in subfolders:
    if folder['mimeType'] == 'application/vnd.google-apps.folder':
        subfolder_id, cursus_barcode = folder['id'], folder['title']
        if len(cursus_barcode) == 5:
            if not os.path.isdir('Veranderd/' + cursus_barcode):
                os.mkdir('Veranderd/' + cursus_barcode)
                cursusdelen = drive.ListFile({'q': "'{}' in parents and trashed=false".format(subfolder_id)}).GetList()
                for i, deeltje in enumerate(sorted(cursusdelen, key=lambda x: x['title']), start=1):
                    print('Downloading {}/{} from GDrive ({}/{})'.format(cursus_barcode, deeltje['title'], i, len(cursusdelen)))
                    deeltje.GetContentFile('Veranderd/' + cursus_barcode + '/' + deeltje['title'])
        else:
            print(f'Folder in Cursussen folder op Google Drive met onherkende naam: {cursus_barcode}.')
    else:
        print(f'Weird file found in Cursussen folder on Google Drive: {folder["title"]}')

index_barcode = 1
index_slides_per_p = 8
index_color = 10
index_rv = 11
index_site = 3

first = True
for i, row in enumerate(ws.iter_rows(min_row=2)):
    if row[0].value is not None and row[1].value is not None and (type(row[1].value) is float or type(row[1].value) is int) and row[2].value is not None and row[index_site].value != "ok":
        barcode = int(row[index_barcode].value)
        if row[2].value.lower().strip() == 'zelfde' or (row[2].value.lower().strip() == 'veranderd' and os.path.isdir('Veranderd/' + str(barcode))):
            color = int(row[index_color].value)
            rv = int(row[index_rv].value) == 1
            pp = False if row[index_slides_per_p].value is not None and int(row[index_slides_per_p].value) > 2 else True
            if pp:
                print(row[2].value.lower().strip(), barcode, color, rv)
                c = cursus.Cursus(row[2].value.lower().strip() == 'zelfde', barcode, color, rv)
                c.update()
                row[index_site].value = "ok"
            else:
                print(f'Custom: {barcode}.')
        else:
            print(f'Weird value at barcode {int(row[1].value)}: {row[2].value}. Should be "veranderd" or "zelfde", nothing else.')
wb.save('cursussen_adapted.xlsx')
file.SetContentFile('cursussen_adapted.xlsx')
file.Upload()  # Upload the file.