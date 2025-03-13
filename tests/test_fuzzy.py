from unittest.mock import Mock
from src.algoritmes.fuzzy import levenshtein_distance, jaccard_similarity, similarity_score, _most_similar, make_typo


def test_levenshtein_distance():
    assert levenshtein_distance('abcd', 'cba') == 3


def test_jaccard_similarity():
    assert jaccard_similarity('hello world', 'Hello World') == 100
    assert jaccard_similarity('hello world', 'goodbye planet') == 0


# def test_similarity_score():
#     mock_levenstein_distance = Mock(return_value=0)
#     score =
#
# 
# # def test_most_similar():
# #     mock_jaccard_similarity = Mock(return_value=0)
# #     mock_similarity_score = Mock(return_value=0)
# #
# #     assert