from unit_helpers import *
from unittest import TestCase
import os
import sys
from src.config import fetch_from_api, set_host, handle_specific_env_vars, set_cache_images, check_key

# API_HOST_URL = '0.0.0.0'
# API_HOST_PORT = 8000

class TestApiFunctions(TestCase):

    @patch('requests.get')
    def test_fetch_from_api_success(self, mock_get):
        """Test the fetch_from_api function with a successful API response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_get.return_value = mock_response

        result = fetch_from_api("https://example.com/api")
        self.assertEqual(result, {"data": "test_data"})
        mock_get.assert_called_once_with("https://example.com/api", timeout=10)

    @patch('requests.get')
    def test_fetch_from_api_failure(self, mock_get):
        """Test the fetch_from_api function when the API call fails."""
        mock_get.side_effect = Exception("Connection error")

        result = fetch_from_api("https://example.com/api")
        self.assertIsNone(result)  # The function should return None on failure
        mock_get.assert_called_once_with("https://example.com/api", timeout=10)

class TestHostFunctions(TestCase):

    # @patch("os.getenv", return_value=None)  # Mock that ADMIN_API_KEY is not set
    # @patch("sys.platform", "linux")  # Mock the platform to be linux
    # def test_set_host_no_admin_key(self, mock_platform, mock_getenv):
    #     """Test the set_host function when the ADMIN_API_KEY is not set."""
    #     with patch("builtins.print") as mock_print:
    #         set_host()
    #
    #         mock_print.assert_any_call("No ADMIN_API_KEY set in ENV, defaulting to public access 🔓")
    #         mock_print.assert_any_call('Detected Linux platform (possibly Docker 📦 ). Setting API_HOST_URL to "0.0.0.0".')
    #         self.assertEqual(os.getenv("ADMIN_API_KEY"), "public")  # Check if it defaults to "public"
    #         self.assertEqual(API_HOST_URL, "0.0.0.0")  # Check if API_HOST_URL is set to "0.0.0.0"

    @patch("os.getenv", return_value="private_key")  # Mock that ADMIN_API_KEY is set to a private key
    def test_set_host_with_admin_key(self, mock_getenv):
        """Test the set_host function when the ADMIN_API_KEY is set."""
        with patch("builtins.print") as mock_print:
            set_host()

            mock_print.assert_any_call("ADMIN_API_KEY set in ENV, using private access 🔒")
            self.assertEqual(os.getenv("ADMIN_API_KEY"), "private_key")

class TestEnvVarFunctions(TestCase):

    # @patch("os.getenv", side_effect=lambda key: "8001" if key == "API_HOST_PORT" else None)
    # def test_handle_specific_env_vars(self, mock_getenv):
    #     """Test the handle_specific_env_vars function."""
    #     handle_specific_env_vars("API_HOST_PORT", "8001")
    #     self.assertEqual(API_HOST_PORT, 8001)  # Check if the port is correctly set
    #
    #     handle_specific_env_vars("API_HOST_PORT", "invalid_port")
    #     self.assertEqual(API_HOST_PORT, 8000)  # Check that the port defaults to 8000 on invalid input

    @patch("os.getenv", side_effect=lambda key: "true" if key == "CACHE_IMAGES" else None)
    def test_set_cache_images(self, mock_getenv):
        """Test the set_cache_images function."""
        with patch("builtins.print") as mock_print:
            set_cache_images()
            mock_print.assert_any_call("CACHE_IMAGES set to True")  # Check if it correctly identifies the environment variable
            self.assertEqual(os.getenv("CACHE_IMAGES"), "true")  # Ensure that the environment variable is set to "true"

class TestCheckKey(TestCase):

    @patch("os.getenv", side_effect=lambda key: "public" if key == "ADMIN_API_KEY" else None)
    def test_check_key_public(self, mock_getenv):
        """Test the check_key function when ADMIN_API_KEY is 'public'."""
        result = check_key("public")
        self.assertTrue(result)

    @patch("os.getenv", side_effect=lambda key: "private" if key == "ADMIN_API_KEY" else None)
    def test_check_key_private(self, mock_getenv):
        """Test the check_key function when ADMIN_API_KEY is 'private'."""
        result = check_key("private")
        self.assertTrue(result)

    @patch("os.getenv", side_effect=lambda key: "public" if key == "ADMIN_API_KEY" else None)
    def test_check_key_invalid(self, mock_getenv):
        """Test the check_key function with an invalid key."""
        # Mock that ADMIN_API_KEY is 'public', but we pass an invalid key
        result = check_key("invalid_key")
        self.assertFalse(result)  # This should be False since "invalid_key" does not match the "public" ADMIN_API_KEY
