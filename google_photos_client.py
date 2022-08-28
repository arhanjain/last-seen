import requests

from pathlib import Path
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GooglePhotosClient:

    def __init__(self):
        self.creds = None
        self.scopes = ['https://www.googleapis.com/auth/photoslibrary.readonly']

        # Load auth token to make requests to Google Photos API
        self.load_auth()

    def load_auth(self):
        token_file = Path(__file__).parent/"creds"/"google_token.json"
        if token_file.exists():  # If auth token already exists
            # Load existing auth token
            self.creds = Credentials.from_authorized_user_file(token_file)

        if not self.creds or not self.creds.valid:  # If auth token is missing or invalid, reauthorize
            credentials_file = Path(__file__).parent/"creds"/"google_credentials.json"

            # run authorization flow
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, self.scopes)
            self.creds = flow.run_local_server(port=0)

            # save auth token for next run
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())
    
    def get_latest_image_url(self) -> str:
        shortened_url = None
        try:
            service = build('photoslibrary', 'v1', credentials=self.creds, static_discovery=False)

            result = service.mediaItems().list(pageSize=1).execute()

            url = result["mediaItems"][0]["baseUrl"]

        except HttpError as err:
            raise Exception(err)

        return url

