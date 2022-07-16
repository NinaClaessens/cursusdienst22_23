from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

FILE_ID = "1gpryvBvfH31uZ7RAHPCw5WQdNKNU8sbmZ6GE96wpm-g"

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

file = drive.CreateFile({'id': FILE_ID})
file.GetContentFile('cursussen.xlsx', mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
