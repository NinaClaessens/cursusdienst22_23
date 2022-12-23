import openpyxl
import cursus
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

FILE_ID = "1YnnvC6OunBD5d8-ujuWxbr3jV1MH--ll"
FOLDER_ID = "1a-7PkirJLUz-SxuRcQUdCuw1UZbnX35F"

gauth = GoogleAuth()
# gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

file = drive.CreateFile({'id': FILE_ID})
file.GetContentFile('cursussen_sem2.xlsx', mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

wb = openpyxl.load_workbook('cursussen_sem2.xlsx')
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

index_name = 0
index_barcode = 1
index_status = 2
index_manueel = 3
index_site = 4

index_color = 11
index_rv = 12

already_done = set()

for i, row in enumerate(ws.iter_rows(min_row=2)):

    try:
        barcode = int(row[index_barcode].value)
    except Exception as e:
        barcode = -1

    try:
        if barcode != -1 and barcode not in already_done:
            already_done.add(barcode)

            if row[index_name].value is not None and row[index_barcode].value is not None and (type(row[index_barcode].value) is float or type(row[index_barcode].value) is int or type(row[index_barcode].value) is str) and row[index_status].value is not None and row[index_site].value != "ok" and row[index_manueel].value is None:
                    if row[index_status].value.lower().strip() == 'zelfde' or (row[index_status].value.lower().strip() == 'veranderd' and os.path.isdir('Veranderd/' + str(barcode))):
                        color = int(row[index_color].value)
                        rv = str(row[index_rv].value).strip().lower() == 'rv'

                        print(row[index_status].value.lower().strip(), barcode, color, rv)
                        c = cursus.Cursus(row[index_status].value.lower().strip() == 'zelfde', barcode, color, rv)
                        c.update()
                        row[index_site].value = "ok"
                    else:
                        print(f'Weird value at barcode {int(row[index_barcode].value)}: {row[index_status].value.lower().strip()}. Should be "veranderd" or "zelfde", nothing else. If veranderd, it should be in the folder of new course material')
    except Exception as e:
        print("Failed to do barcode", barcode, "with exception", e)

print("Finished")
wb.save('cursussen_adapted.xlsx')
file.SetContentFile('cursussen_adapted.xlsx')
file.Upload()  # Upload the file.