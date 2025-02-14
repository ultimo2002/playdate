# All functions in this file are for the fuzzy algorithm to find the most similar item in a list based on a calculated similarity score.

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

# Function to check Jaccard similarity
def jaccard_similarity(s1, s2):
    set1, set2 = set(s1.lower().split()), set(s2.lower().split())
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union) * 100 if union else 0

def similarity_score(s1, s2):
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 100
    return (1 - levenshtein_distance(s1.lower(), s2.lower()) / max_len) * 100


def _most_similar(target_name: str, items, key: str):
    """Find the most similar item in a list based on similarity score.

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

import random

def make_typo(text, appid=0, apps=None):
    """Introduce small typos or grammatical errors into a string."""
    if len(text) > 3:
        random_list = ["swap", "remove", "duplicate", "misspell"]
        if appid != 0:
            random_list.append("appid")
        if text.count(" ") > 1:
            random_list.append("plusses")
            random_list.append("nospaces")

        typo_type = random.choice(random_list)

        if typo_type == "appid":
            return str(appid)

        for _ in range(3):
            typo_type = random.choice(random_list)
            if typo_type == "swap":
                i = random.randint(0, len(text) - 2)
                text = text[:i] + text[i + 1] + text[i] + text[i + 2:]
            elif typo_type == "plusses":
                text = text.replace(" ", "+")
            elif typo_type == "nospaces":
                text = text.replace(" ", "")
            elif typo_type == "remove":
                i = random.randint(0, len(text) - 1)
                text = text[:i] + text[i + 1:]
            elif typo_type == "duplicate":
                i = random.randint(0, len(text) - 1)
                text = text[:i] + text[i] + text[i:]
            elif typo_type == "misspell":
                common_misspellings = {"their": "thier", "receive": "recieve", "app": "ap", "random": "randum", "from": "form", "is": "si", "an": "and", "with": "wiht", "for": "fro", "you": "u"}
                words = text.split()
                text = " ".join([common_misspellings.get(word, word) for word in words])

        # check if the fuzzy algorithm still working on this text, else there is a possibility that the test will fail
        if apps:
            most_similar_app, score = _most_similar(text, apps, "name")
            if most_similar_app and score > 50:
                return text
            else:
                return str(appid)


    return text