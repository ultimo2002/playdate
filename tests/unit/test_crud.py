from tests.unit.unit_helpers import *
from src.database.crud import *


class TestDatabaseFunctions(unittest.TestCase):

    def setUp(self):
        # Maak een mock db-sessie voor alle tests
        self.mock_db = MagicMock(spec=Session)

        # Maak mock objecten voor model en record
        self.mock_model = MagicMock()
        self.mock_record = MagicMock()

    def test_get_by_id(self):
        # Testen van de get_by_id functie
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_record
        result = get_by_id(self.mock_db, self.mock_model, 1)
        self.assertEqual(result, self.mock_record)

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_by_id(self.mock_db, self.mock_model, 1)
        self.assertIsNone(result)

    def test_get_by_name(self):
        # Testen van de get_by_name functie
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_record
        result = get_by_name(self.mock_db, self.mock_model, "TestName")
        self.assertEqual(result, self.mock_record)

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_by_name(self.mock_db, self.mock_model, "TestName")
        self.assertIsNone(result)

    def test_create(self):
        # Testen van de create functie
        self.mock_model.return_value.name = "NewName"  # Simuleer de naam van het object
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None

        new_record = create(self.mock_db, self.mock_model, name="NewName")
        self.assertEqual(new_record.name, "NewName")

        # Testen van een duplicate IntegrityError
        self.mock_db.commit.side_effect = IntegrityError(None, None, None)
        result = create(self.mock_db, self.mock_model, name="DuplicateName")
        self.assertIsNone(result)

    def test_update(self):
        # Testen van de update functie
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_record
        updated_record = update(self.mock_db, self.mock_model, 1, name="UpdatedName")
        self.assertEqual(updated_record.name, "UpdatedName")

        # Testen van het niet kunnen vinden van een record
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = update(self.mock_db, self.mock_model, 1, name="UpdatedName")
        self.assertIsNone(result)

    def test_delete(self):
        # Testen van de delete functie
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_record
        deleted_record = delete(self.mock_db, self.mock_model, 1)
        self.assertEqual(deleted_record, self.mock_record)

        # Testen van het niet kunnen vinden van een record
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = delete(self.mock_db, self.mock_model, 1)
        self.assertIsNone(result)

    # def test_handle_create(self):
    #     # Testen van de handle_create functie voor een nieuw record
    #     self.mock_model.return_value.name = "TestName"  # Simuleer de naam van het object
    #     self.mock_db.query.return_value.filter.return_value.first.return_value = None  # Geen record gevonden
    #     record = handle_create(self.mock_db, self.mock_model, name="TestName")
    #     self.assertEqual(record.name, "TestName")
    #
    #     # Testen van een al bestaand record
    #     self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_record  # Record bestaat al
    #     self.mock_record.name = "TestName"  # Zorg ervoor dat de mock record een naam heeft die overeenkomt
    #     with self.assertRaises(HTTPException) as context:
    #         handle_create(self.mock_db, self.mock_model, name="TestName")
    #
    #     # Controleer of de exception daadwerkelijk is opgegooid met de juiste statuscode en detail
    #     self.assertEqual(context.exception.status_code, 409)
    #     self.assertEqual(str(context.exception.detail), "TestModel already exists")

    def test_handle_update(self):
        # Testen van de handle_update functie
        self.mock_model.__name__ = "TestModel"  # Simuleer de modelnaam
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_record
        record = handle_update(self.mock_db, self.mock_model, 1, name="UpdatedName")
        self.assertEqual(record.name, "UpdatedName")

        # Testen van record niet gevonden
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(HTTPException):
            handle_update(self.mock_db, self.mock_model, 1, name="NonExistentName")

    def test_handle_delete(self):
        # Testen van de handle_delete functie
        self.mock_model.__name__ = "TestModel"  # Simuleer de modelnaam
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_record
        response = handle_delete(self.mock_db, self.mock_model, 1)
        self.assertEqual(response["message"], "TestModel deleted successfully")

        # Testen van record niet gevonden
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(HTTPException):
            handle_delete(self.mock_db, self.mock_model, 1)
