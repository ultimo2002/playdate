#hier komen unit tests
from tests.integratie.integration_helpers import ALL_APP_FIELDS


def test_configs():
    """
    Test if the configuration values are set correctly.
    """
    assert len(ALL_APP_FIELDS) > 0 and "id" in ALL_APP_FIELDS # Check if the ALL_APP_FIELDS list is not empty and contains an "id" field

    import src.config as config # Test the configuration values from config.py.

    from src.database.database import URL_DATABASE

    # Test if database URL is set and not empty or postgresql://user:password@localhost:5432/database
    assert URL_DATABASE is not None and len(URL_DATABASE) > 0 and URL_DATABASE != "postgresql://user:password@localhost:5432/database"

    # Remove the imported modules from memory
    del config
    del URL_DATABASE