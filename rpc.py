import json
from pathlib import Path
from pypresence import Presence

class RPC():
    def __init__(self):
        self.client = Presence(self.get_client_id())

    def connect(self):
        self.client.connect()

    def update(self, state, large_image):
        self.client.update(state=state, large_image=large_image)

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

