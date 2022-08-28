from pathlib import Path
import requests
import json

class Imgur():
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

if __name__ == "__main__":
    imgur = Imgur()
    link = imgur.upload_image("https://static.wikia.nocookie.net/meme/images/0/07/Amogus_Template.png/revision/latest?cb=20210308145830")

    print(link)
