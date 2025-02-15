# All functions in this file are for the fuzzy algorithm to find the most similar item in a list based on a calculated similarity score.
from code.config import TextStyles


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
import time

typo_types = ["duplicate", "nospaces", "plusses", "capitalize", "duplicate", "remove_special_chars", "id"]
random.seed(time.time())

def make_typo(text, appid=0, apps=None):
    """Introduce small typos or grammatical errors into a string."""
    modified_text = text

    typos_amount = random.randint(1, 3) # The amount of typos to make on the string

    for _ in range(typos_amount):
        typo_type = random.choice(typo_types)
        if typo_type == "remove_special_chars" and not any(c for c in text if not c.isalnum() and not c.isspace()):
            typo_type = random.choice([t for t in typo_types if t != "remove_special_chars"])

        if typo_type == "duplicate":
            # Duplicate a random neighbour character in the string
            index = random.randint(0, len(text) - 2)
            modified_text = text[:index] + text[index] + text[index] + text[index + 1:]

            print(f"{TextStyles.green}{TextStyles.bold}Doing typo: {TextStyles.reset}{TextStyles.pink}duplicate chars from: {TextStyles.bold}{text}{TextStyles.reset}{TextStyles.grey} -> {TextStyles.yellow}{modified_text}{TextStyles.reset}")
        elif typo_type == "nospaces" or typo_type == "plusses":
            # Remove spaces with empty strings or replace for plusses
            modified_text = text.replace(" ", "") if typo_type == "nospaces" else text.replace(" ", "+")
            spaces_or_plusses = "nospaces" if typo_type == "nospaces" else "plusses"
            print(f"{TextStyles.green}{TextStyles.bold}Doing typo: {TextStyles.reset}{TextStyles.pink}replace spaces with {spaces_or_plusses} from: {TextStyles.bold}{text}{TextStyles.reset}{TextStyles.grey} -> {TextStyles.yellow}{modified_text}{TextStyles.reset}")
        elif typo_type == "capitalize":
            # capitalize a random letter in the string
            for i in range(3):
                index = random.randint(0, len(text) - 1)
                modified_text = text[:index] + text[index].upper() + text[index + 1:]
            print(f"{TextStyles.green}{TextStyles.bold}Doing typo: {TextStyles.reset}{TextStyles.pink}capitalize a random letter from: {TextStyles.bold}{text}{TextStyles.reset}{TextStyles.grey} -> {TextStyles.yellow}{modified_text}{TextStyles.reset}")
        elif typo_type == "remove_special_chars":
            # remove special characters from the string
            modified_text = "".join(c for c in text if c.isalnum() or c.isspace())
            print(f"{TextStyles.green}{TextStyles.bold}Doing typo: {TextStyles.reset}{TextStyles.pink}remove special characters from: {TextStyles.bold}{text}{TextStyles.reset}{TextStyles.grey} -> {TextStyles.yellow}{modified_text}{TextStyles.reset}")
        elif typo_type == "id" and text == modified_text: # Only do this if the text hasn't been modified yet, for computational efficiency
            # return the appid as a string
            print(f"{TextStyles.green}{TextStyles.bold}FOUND & Doing typo: {TextStyles.reset}{TextStyles.pink}return the appid as a string from: {TextStyles.bold}{text}{TextStyles.reset}{TextStyles.grey} -> {TextStyles.yellow}{appid}{TextStyles.reset}")
            return str(appid)

    # Check if the typo is valid (avoiding test failures)
    if apps and appid:
        most_similar_app, score = _most_similar(modified_text, apps, "name")
        if most_similar_app and most_similar_app.id == appid and modified_text != most_similar_app.name and score > 75:
            print(f"{TextStyles.green}{TextStyles.bold}FOUND Typo:{TextStyles.reset}{TextStyles.yellow} {text}{TextStyles.grey} -> {modified_text} (score: {score}){TextStyles.reset}")
            return modified_text
        else:
            print(f"{TextStyles.red}{TextStyles.bold}FAILED Typo:{TextStyles.reset}{TextStyles.grey} {text} -> {modified_text}{TextStyles.reset}")
            return str(appid)

    return modified_text