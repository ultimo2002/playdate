import os
import requests

from code.config import IMAGE_CACHE_PATH


def download_image(image_url, image_path):
    """Helper function to download an image and save it to the given path."""
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    response = requests.get(image_url)
    if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
        with open(image_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Error: The URL '{image_url}' is not an image.")
        return False


def cache_background_image(app):
    if not app or not hasattr(app, "background_image") or not app.background_image:
        return None

    image_url = app.background_image
    ext = image_url.split(".")[-1].split("?")[0]
    image_path = f"{IMAGE_CACHE_PATH}/bg_{app.id}.{ext}"

    if not os.path.exists(image_path):
        if download_image(image_url, image_path):
            print(f"Cached image: {image_path}")
        else:
            return None
    else:
        print(f"Image already cached: {image_path}")

    # Adjust the path as needed and return the background image info
    background_image_path = image_path.split("/", 1)[1]
    return {"id": app.id, "name": app.name, "background_image": background_image_path}
