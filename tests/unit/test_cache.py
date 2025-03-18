from tests.unit.unit_helpers import *
from src.algoritmes.cache import download_image, cache_image, cache_background_image, cache_header_image

from src.config import IMAGE_CACHE_PATH



class MockApp:
    def __init__(self, app_id, name, background_image=None, header_image=None):
        self.id = app_id
        self.name = name
        self.background_image = background_image
        self.header_image = header_image


class TestImageCaching(unittest.TestCase):


    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_download_image(self, mock_makedirs, mock_open, mock_get):
        mock_get.return_value = MagicMock(status_code=200, headers={"content-type": "image/png"}, content=b"fake_data")
        self.assertTrue(download_image("http://example.com/image.png", "/fake/path/image.png"))
        mock_open.assert_called_once_with("/fake/path/image.png", "wb")


    @patch("requests.get", return_value=MagicMock(status_code=404, headers={}))
    def test_download_image_failure(self, mock_get):
        self.assertFalse(download_image("http://example.com/image.png", "/fake/path/image.png"))


    @patch("os.path.exists", return_value=False)
    @patch("src.algoritmes.cache.download_image", return_value=True)
    def test_cache_image(self, mock_download, mock_exists):
        app = MockApp(1, "TestApp", background_image="http://example.com/bg.jpg")
        result = cache_image(app, "background_image", "bg")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], app.id)
        mock_download.assert_called_once()


    @patch("os.path.exists", return_value=True)
    def test_cache_image_already_cached(self, mock_exists):
        app = MockApp(1, "TestApp", background_image="http://example.com/bg.jpg")
        result = cache_image(app, "background_image", "bg")
        self.assertIsNotNone(result)


    def test_cache_image_invalid_app(self):
        self.assertIsNone(cache_image(None, "background_image", "bg"))


    @patch("src.algoritmes.cache.cache_image")
    def test_cache_background_image(self, mock_cache):
        app = MockApp(1, "TestApp", background_image="http://example.com/bg.jpg")
        cache_background_image(app)
        mock_cache.assert_called_once_with(app, "background_image", "bg")


    @patch("src.algoritmes.cache.cache_image")
    def test_cache_header_image(self, mock_cache):
        app = MockApp(1, "TestApp", header_image="http://example.com/header.jpg")
        cache_header_image(app)
        mock_cache.assert_called_once_with(app, "header_image", "hi")