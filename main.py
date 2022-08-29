import time
import logging
import signal

from functools import partial
from clients import GooglePhotosClient, ImgurClient, RichPresenceClient, AzureCVClient

def cleanup(imgur_client: ImgurClient, rpc: RichPresenceClient, *args):
    print("Cleaning up leftovers...")
    imgur_client.delete_image()
    rpc.shutdown()
    exit(0)

def main():
    # Initialize clients
    photos_client = GooglePhotosClient()
    imgur = ImgurClient()
    rpc = RichPresenceClient()
    azure_cv_client = AzureCVClient()

    # Exit handlers
    #atexit.register(cleanup, imgur, rpc)
    signal.signal(signal.SIGINT, partial(cleanup, imgur, rpc))
    signal.signal(signal.SIGTERM, partial(cleanup, imgur, rpc))
 
    img_url = photos_client.get_latest_image_url()
    img_hosted_url = imgur.upload_image(img_url)

    caption = azure_cv_client.get_best_caption(img_url=img_url)

    rpc.connect()
    rpc.update(state=caption, large_image=img_hosted_url)

    while True:
        time.sleep(5)


if __name__ == '__main__':
    main()


