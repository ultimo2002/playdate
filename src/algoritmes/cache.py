import os
import requests

from src.config import IMAGE_CACHE_PATH

# test for downloading image
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


def cache_image(app, image_attr, prefix):
    if not app or not hasattr(app, image_attr) or not getattr(app, image_attr):
        return None

    image_url = getattr(app, image_attr)
    ext = image_url.split(".")[-1].split("?")[0]
    image_path = f"{IMAGE_CACHE_PATH}/{prefix}_{app.id}.{ext}"

    if not os.path.exists(image_path):
        if download_image(image_url, image_path):
            print(f"Cached image: {image_path}")
        else:
            return None
    else:
        print(f"Image already cached: {image_path}")

    # Adjust the path and return image info
    relative_path = image_path.split("/", 1)[1]
    return {"id": app.id, "name": app.name, image_attr: relative_path}

def cache_background_image(app):
    return cache_image(app, "background_image", "bg")

def cache_header_image(app):
    return cache_image(app, "header_image", "hi")