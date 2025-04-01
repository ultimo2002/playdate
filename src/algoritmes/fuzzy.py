# All functions in this file are for the fuzzy algorithm to find the most similar item in a list based on a calculated similarity score.


def levenshtein_distance(input, reference):
    """calculates levenshtein distance using the Levenshtein algorithm
    :param input: input string
    :param reference: reference string
    :return: levenshtein distance
    """
    if len(input) < len(reference):
        return levenshtein_distance(reference, input)

    if len(reference) == 0:
        return len(input)

    previous_row = list(range(len(reference) + 1))
    for i, c1 in enumerate(input):
        current_row = [i + 1]
        for j, c2 in enumerate(reference):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def jaccard_similarity(input, reference):
    """checks similarity based on amount of matching words in two strings
    :param input: input string
    :param reference: reference string
    :return: percentage of words that match
    """
    set1, set2 = set(input.lower().split()), set(reference.lower().split())
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union) * 100 if union else 0

def similarity_score(input, reference):
    """checks similarity based on the levenshtein distance
    :param input: input string
    :param reference: reference string
    :return: similarity based on levenshtein distance
    """
    max_len = max(len(input), len(reference))
    if max_len == 0:
        return 100
    return (1 - levenshtein_distance(input.lower(), reference.lower()) / max_len) * 100


def _most_similar(target_name: str, items, key: str):
    """Find the most similar item in a list based on similarity scores.

    :param target_name: The string name to compare.
    :param items: The list of items to search through.
    :param key: The attribute of the item to compare.
    :return: (item, score) The most similar item and its similarity score, or None.
    """
    target_name = target_name.strip().lower()
    most_similar_item = None
    highest_similarity = 0

    for item in items:
        name = getattr(item, key)
        similarity = max(similarity_score(target_name, name), jaccard_similarity(target_name, name))

        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_item = item

    if most_similar_item:
        return most_similar_item, round(highest_similarity, 2)

    return None, None
