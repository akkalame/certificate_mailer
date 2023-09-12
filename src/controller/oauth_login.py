from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# If modifying these scopes, delete the file token.picklefrom 
import os
from utils import _

class Service():
    def __init__(self):
        self.gCreds = None

    def get_creds(self, tokenFileName):
        #.readonly
        SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/spreadsheets']
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(f'./tokens/{tokenFileName}.json') and tokenFileName != '':
            creds = Credentials.from_authorized_user_file(f'./tokens/{tokenFileName}.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('./kernel/app_credential.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            print("guardando el token en json")
            with open(f'./tokens/{tokenFileName}.json', 'w') as token:
                token.write(creds.to_json())
        self.gCreds = creds

    def gmail(self):
        try:
            return build(serviceName='gmail', version='v1', credentials=self.gCreds, static_discovery=False)
        except Exception as e:
            print(_("Error in {0}").format("oauth_login.gmail_service"))
            raise e
        

    def sheets(self):
        try:
            return build(serviceName='sheets', version='v4', credentials=self.gCreds, static_discovery=False)
        except Exception as e:
            print(_("Error in {0}").format("oauth_login.sheets_service"))
            raise e
        
