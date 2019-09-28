from __future__ import print_function

import pickle
import os.path
import io

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.file'
]

def authorize_login_oauth():
    store = file.Storage('storage.json')
    creds = store.get()
    # Add your conditional here. I removed it in order to test different scopes
    # You can change 'credentials.json' to 'client_id.json'
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
    drive_service = discovery.build('drive', 'v3', http=creds.authorize(Http()))
    return drive_service

def get_file_id(drive_service):
    # You can take this out of the loop. I just used it to pull the first file
    # I could find on my drive.
    results = drive_service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('Nothing here!')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    return items[0]['id']

def download_file(drive_service, file_id):
    # Using files().get per SO
    # --> https://stackoverflow.com/questions/46302540/google-drive-export-non-google-doc-file
    request = drive_service.files().get(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

if __name__ == '__main__':
    drive_service = authorize_login_oauth()
    target_file = get_file_id(drive_service)
    download_file(drive_service, target_file)
