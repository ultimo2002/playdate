from tests.unit.unit_helpers import *
import sys
from src.database.database import Engine, SessionLocal, get_db


class TestDatabaseConnection(unittest.TestCase):

    # @patch('sqlalchemy.create_engine')
    # def test_database_connection_success(self, mock_create_engine):
    #     # Mock de database engine creatie
    #     mock_engine = MagicMock()
    #     mock_create_engine.return_value = mock_engine
    #
    #     # Simuleer succesvolle database URL environment variable
    #     with patch("os.getenv", return_value="sqlite:///test.db"):
    #         # Verzeker dat de import van Engine pas na de patching plaatsvindt
    #         from src.database.database import Engine  # Dit zou de engine aanmaken
    #
    #         # Assert dat de engine is aangemaakt met de juiste URL
    #         mock_create_engine.assert_called_once_with("sqlite:///test.db")
    #         self.assertEqual(mock_create_engine.return_value, mock_engine)  # Controleer of de juiste engine is teruggegeven

    @patch('sqlalchemy.create_engine')
    @patch('sys.exit')  # We patchen sys.exit om te voorkomen dat de applicatie daadwerkelijk stopt
    def test_database_connection_failure(self, mock_exit, mock_create_engine):
        # Simuleer een fout scenario
        mock_create_engine.side_effect = Exception("Connection failed")

        with patch("os.getenv", return_value="invalid_url"):
            # Controleer of de applicatie stopt na het falen van het maken van de engine
            try:
                # Verzeker dat de import van Engine pas na de patching plaatsvindt
                from src.database.database import Engine  # Dit zou een SystemExit moeten triggeren als de verbinding faalt
            except SystemExit as e:
                # Controleer of de exit met de juiste statuscode werd aangeroepen
                self.assertEqual(e.code, 1)  # Verwacht dat exit(1) werd aangeroepen
                mock_exit.assert_called_once_with(1)  # Bevestig dat sys.exit met 1 werd aangeroepen


class TestGetDbFunction(unittest.TestCase):

    @patch('src.database.database.SessionLocal')  # Mock SessionLocal, welke sessionmaker is
    def test_get_db(self, mock_sessionmaker):
        # Mock het session object dat teruggegeven zou moeten worden door SessionLocal
        mock_db_session = MagicMock()
        mock_sessionmaker.return_value = mock_db_session

        # Roep get_db aan en controleer of het session-object wordt opgehaald en gesloten
        with patch('src.database.database.get_db', return_value=mock_db_session):
            db = next(get_db())
            self.assertEqual(db, mock_db_session)
            db.close.assert_called_once()

    @patch('src.database.database.SessionLocal')
    def test_get_db_create_session(self, mock_sessionmaker):
        # Mock het session object
        mock_db_session = MagicMock()
        mock_sessionmaker.return_value = mock_db_session

        # Roep get_db aan en controleer of het session-object wordt teruggegeven
        db = next(get_db())
        self.assertEqual(db, mock_db_session)
        mock_sessionmaker.assert_called_once()

    @patch('src.database.database.SessionLocal')
    def test_get_db_session_close(self, mock_sessionmaker):
        # Mock het session object
        mock_db_session = MagicMock()
        mock_sessionmaker.return_value = mock_db_session

        # Zorg ervoor dat het session-object wordt gesloten na gebruik
        db = next(get_db())
        db.close.assert_called_once()
