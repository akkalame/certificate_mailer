from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# If modifying these scopes, delete the file token.picklefrom 
import os
from apps.certificate_mailer.utils import mkdir

basedir = os.path.abspath(os.path.dirname(__file__))

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
        token_path = os.path.join(basedir, f'tokens/{tokenFileName}.json')
        if os.path.exists(token_path) and tokenFileName != '':
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            #if creds and creds.expired and creds.refresh_token:
            #    creds.refresh(Request())
            #else:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(basedir,'kernel/app_credential.json'), SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            mkdir(os.path.join(basedir,"tokens/"))
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        self.gCreds = creds

    def gmail(self):
        try:
            return build(serviceName='gmail', version='v1', credentials=self.gCreds, static_discovery=False)
        except Exception as e:
            print("Error in {0}".format("oauth_login.gmail_service"))
            raise e
        

    def sheets(self):
        try:
            return build(serviceName='sheets', version='v4', credentials=self.gCreds, static_discovery=False)
        except Exception as e:
            print("Error in {0}".format("oauth_login.sheets_service"))
            raise e
        
