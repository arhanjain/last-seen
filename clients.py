import requests
import json

from pypresence import Presence
from pathlib import Path
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

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
            if not self.creds.valid:
                self.creds.refresh(Request())

        if not self.creds or not self.creds.valid:  # If auth token is missing or invalid, reauthorize
            credentials_file = Path(__file__).parent/"creds"/"google_credentials.json"

            # run authorization flow
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, self.scopes)
            self.creds = flow.run_local_server(port=0)

            # save auth token for next run
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())
    
    def get_latest_image_url(self) -> str:
        try:
            service = build('photoslibrary', 'v1', credentials=self.creds, static_discovery=False)

            result = service.mediaItems().list(pageSize=1).execute()

            url = result["mediaItems"][0]["baseUrl"]

        except HttpError as err:
            raise Exception(err)

        return url



class ImgurClient():
    def __init__(self):
        self.upload_endpoint = "https://api.imgur.com/3/upload"
        self.delete_endpoint = "https://api.imgur.com/3/image/"
        self.client_id = self.get_client_id()
        self.image_del_hash = None

    @staticmethod
    def get_client_id() -> str:
        client_id = None

        imgur_cred_path = Path(__file__).parent/"creds"/"imgur_credentials.json"
        with open(imgur_cred_path, "r") as imgur_cred_file:
            client_id = json.load(imgur_cred_file)["client_id"]
            imgur_cred_file.close()
        
        if client_id is None:
            raise Exception("Failed to get client_id for Imgur")
        else:
            return client_id
        

    def upload_image(self, url: str):
        # Delete previous image if exists
        self.delete_image()

        headers = {
            "Authorization": f"Client-ID {self.client_id}"
        }
        payload = {
            "image": url,
            "type": "url"
        }

        response = requests.post(url=self.upload_endpoint, headers=headers, data=payload)

        if response.ok:
            response = response.json()
            self.image_del_hash = response["data"]["deletehash"]
            return response["data"]["link"]
        else:
            print(response.text)
            print(response.headers)
            raise Exception("Upload image to Imgur request failed.")


    def delete_image(self):
        if self.image_del_hash is None:
            return

        headers = {
            "Authorization": f"Client-ID {self.client_id}"
        }

        endpoint = self.delete_endpoint + self.image_del_hash

        requests.delete(url=endpoint, headers=headers)




class RichPresenceClient():
    def __init__(self):
        self.client = Presence(self.get_client_id())

    def connect(self):
        self.client.connect()

    def update(self, state, large_image):
        self.client.update(state=state, large_image=large_image, buttons=[{"label": "Find Single Nitins in your Area", "url": "https://github.com/arhanjain/last-seen"}])

    def shutdown(self):
        self.client.close()

    @staticmethod
    def get_client_id():
        client_id = None

        discord_client_id_path = Path(__file__).parent/"creds"/"discord_credentials.json"
        with open(discord_client_id_path, "r") as discord_cred_file:
            client_id = json.load(discord_cred_file)["client_id"]
            discord_cred_file.close()

        if client_id is None:
            raise Exception("Failed to get client_id for Discord")
        else:
            return client_id


class AzureCVClient():
    def __init__(self):
        self.endpoint, self.key = self._get_credentials()
        self.client = ComputerVisionClient(
            endpoint=self.endpoint,
            credentials=CognitiveServicesCredentials(subscription_key=self.key)
        )

    @staticmethod
    def _get_credentials():
        azure_cred_path = Path(__file__).parent/"creds"/"azure_credentials.json"
        with open(azure_cred_path, "r") as azure_cred_file:
            creds = json.load(azure_cred_file)
            endpoint = creds["endpoint"]
            key = creds["key"]
            azure_cred_file.close()

        if endpoint is None or key is None:
            raise Exception("Failed to get endpoint/key for AzureCVClient")
        else:
            return endpoint, key

    def get_best_caption(self, img_url: str):
        analysis = self.client.describe_image(url=img_url)
        return analysis.captions[0].text


        
