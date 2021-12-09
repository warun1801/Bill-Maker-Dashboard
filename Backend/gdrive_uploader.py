from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.json")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.json")
drive = GoogleDrive(gauth)
path = f"./"

for x in os.listdir(path):
    if x.endswith(".pdf"):
        f = drive.CreateFile({'title': x})
        f.SetContentFile(f'{path}/{x}')
        f.Upload()
        print(f'{x} uploaded')
        f = None
    else:
        continue
