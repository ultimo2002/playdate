from tests.unit.unit_helpers import *
from src.algoritmes.fuzzy import levenshtein_distance, jaccard_similarity, similarity_score, _most_similar


class MockData:
    def __init__(self, name):
        self.name = name

# @pytest.fixture
# def test_data():
#     text = "hollow knight!"
#     appid = 367520
#     apps = None
#     return text, appid, apps


def test_levenshtein_distance():
    assert levenshtein_distance('abcd', 'cba') == 3


def test_jaccard_similarity():
    assert jaccard_similarity('hello world', 'Hello World') == 100
    assert jaccard_similarity('hello world', 'goodbye planet') == 0


def test_similarity_score():
    with patch('src.algoritmes.fuzzy.levenshtein_distance', MagicMock(return_value=0)):
        assert similarity_score('hello world', 'Hello World') == 100


def test__most_similar():
    items = [MockData("hello world"), MockData("goodbye planet")]

    with patch('src.algoritmes.fuzzy.similarity_score', MagicMock(return_value=80)), \
            patch('src.algoritmes.fuzzy.jaccard_similarity', MagicMock(return_value=90)):
        result, score = _most_similar('hello world', items, 'name')

        assert result == items[0]
        assert score == 90


# def test_make_typo_duplicate(test_data):
#     text, appid, apps = test_data
#
#     # Test duplicatie van een karakter
#     with patch('random.choice', MagicMock(return_value="duplicate")), \
#          patch('random.randint', MagicMock(return_value=1)):  # Mock index voor duplicatie
#
#         result = make_typo(text, appid, apps)
#         assert result == "hoollow knight!", f"Expected 'hoollow knight!', but got {result}"
#
#
# def test_make_typo_nospaces(test_data):
#     text, appid, apps = test_data
#
#     # Test verwijderen van spaties (nospaces)
#     with patch('random.choice', MagicMock(return_value="nospaces")):
#         result = make_typo(text, appid, apps)
#         assert result == "hollowknight!", f"Expected 'hollowknight!', but got {result}"
#
#
# def test_make_typo_plusses(test_data):
#     text, appid, apps = test_data
#
#     # Test vervangen van spaties door plussen
#     with patch('random.choice', MagicMock(return_value="plusses")):
#         result = make_typo(text, appid, apps)
#         assert result == "hollow+knight!", f"Expected 'hollow+knight!', but got {result}"
#
#
# def test_make_typo_capitalize(test_data):
#     text, appid, apps = test_data
#
#     # Mock random.choice and random.randint
#     with patch('random.choice', MagicMock(return_value="capitalize")), \
#          patch('random.randint', MagicMock(side_effect=iter([1, 4, 7]))):  # Use iter to create an infinite iterator
#
#         result = make_typo(text, appid, apps)
#         expected_results = ["Hollow knight!", "hoLlow knight!", "holLow knight!", "hollOw knight!"]
#         assert result in expected_results, f"Expected one of {expected_results}, but got {result}"
#
#
# def test_make_typo_remove_special_chars(test_data):
#     text, appid, apps = test_data
#
#     # Test met special character removal
#     with patch('random.choice', MagicMock(return_value="remove_special_chars")):
#         result = make_typo(text, appid, apps)
#         assert result == "hollow knight", f"Expected 'hollow knight', but got {result}"
#
#
# def test_make_typo_id_fallback(test_data):
#     text, appid, apps = test_data
#
#     # Test met ID return als fallback
#     with patch('random.choice', MagicMock(return_value="id")):
#         result = make_typo(text, appid, apps)
#         assert result == str(appid), f"Expected '{appid}', but got {result}"
