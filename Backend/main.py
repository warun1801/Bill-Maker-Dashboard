from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pdfautomation import BillMaker
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def remove_file(path: str) -> None:
    os.remove(path)

@app.post("/bill")
async def make_bill(name: str = Form(...), address: str = Form(...), items: str = Form(...), quantities: str = Form(...), rates: str = Form(...), date: str = Form(...), invoice: str = Form(...)):
    b = BillMaker()
    items = list(items.split())
    quantities = list(map(int, quantities.split()))
    rates = list(map(float, rates.split()))
    b.bill_maker_form(name, address, items, quantities, rates, date, invoice)
    file_name = b.set_file_name()
    path = os.getcwd()
    
    # Google Drive Upload
    f = drive.CreateFile({'title': file_name})
    f.SetContentFile(f'{path}/{file_name}')
    f.Upload()
    f = None
    print(f'{file_name} uploaded to drive')

    # background_tasks.add_task(remove_file, path + "/" + file_name)
    return FileResponse(path=path + "/" + file_name, media_type='application/octet-stream', filename=file_name, background=BackgroundTask(remove_file, path + "/" + file_name))
    




