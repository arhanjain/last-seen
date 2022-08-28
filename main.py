import json
from pathlib import Path
import time
import logging
import atexit
import signal

from functools import partial
from google_photos_client import GooglePhotosClient
from image_hosting import Imgur
from rpc import RPC
from pypresence import Presence

def cleanup(imgur_client: Imgur, rpc: RPC, *args):
    print("Cleaning up leftovers...")
    imgur_client.delete_image()
    rpc.shutdown()
    exit(0)

def main():
    # Initialize clients
    photos_client = GooglePhotosClient()
    imgur = Imgur()
    rpc = RPC()

    # Exit handlers
    #atexit.register(cleanup, imgur, rpc)
    signal.signal(signal.SIGINT, partial(cleanup, imgur, rpc))
    signal.signal(signal.SIGTERM, partial(cleanup, imgur, rpc))
 
    img = photos_client.get_latest_image_url()
    img_hosted = imgur.upload_image(img)

    rpc.connect()
    rpc.update(state="in Nitin's pants", large_image=img_hosted)

    while True:
        time.sleep(5)


if __name__ == '__main__':
    main()


