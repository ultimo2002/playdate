import tests.unit.unit_helpers
from tests.unit.unit_helpers import *
from src.algoritmes.fuzzy import levenshtein_distance, jaccard_similarity, similarity_score, _most_similar, make_typo


def test_levenshtein_distance():
    assert levenshtein_distance('abcd', 'cba') == 3


def test_jaccard_similarity():
    assert jaccard_similarity('hello world', 'Hello World') == 100
    assert jaccard_similarity('hello world', 'goodbye planet') == 0


# @patch('levenshtein_distance', return_value=0)
def test_similarity_score():
    with patch('src.algoritmes.fuzzy.levenshtein_distance', MagicMock(return_value=0)):
        assert similarity_score('hello world', 'Hello World') == 100
