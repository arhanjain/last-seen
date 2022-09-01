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
    imgur_client = ImgurClient()
    rpc_client = RichPresenceClient()
    azure_cv_client = AzureCVClient()

    # Exit handlers
    #atexit.register(cleanup, imgur, rpc)
    signal.signal(signal.SIGINT, partial(cleanup, imgur_client, rpc_client))
    signal.signal(signal.SIGTERM, partial(cleanup, imgur_client, rpc_client))
 
    rpc_client.connect()

    current_image_url = None
    current_image_hosted_url = None
    caption = None

    while True:
        # Get latest image
        img_url = photos_client.get_latest_image_url()

        if img_url != current_image_url:  # Only host image and generate captions if new image found
            current_image_hosted_url = imgur_client.upload_image(img_url)

            # Generate image caption
            caption = azure_cv_client.get_best_caption(img_url=img_url)

            # Set new image to current image being used
            current_image_url = img_url

        # Get current epoch
        epoch = int(time.time())

        # Update Discord Rich Presence
        rpc_client.update(caption=caption, large_image=current_image_hosted_url, end=(epoch + 5*60))

        # Run every 5 minutes
        time.sleep(300)


if __name__ == '__main__':
    main()


