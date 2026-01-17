import syllapy
import re

from backend.constants import BANNED_AI_WORDS

def check_cliches(text: str) -> list[str]:
    """
    Returns a list of banned words found in the text.
    """
    found = []
    text_lower = text.lower()
    for word in BANNED_AI_WORDS:
        if word in text_lower:
            found.append(word)
    return found

def count_syllables_in_line(line: str) -> int:
    """
    Counts syllables in a single line of text.
    Removes punctuation and splits by whitespace.
    """
    # Remove punctuation except apostrophes
    words = re.findall(r"\b[\w']+\b", line)
    return sum(syllapy.count(word) for word in words)

def get_syllable_counts(text: str) -> list[int]:
    """
    Returns a list of syllable counts for each line in the text.
    """
    if not text:
        return []
    lines = text.splitlines()
    return [count_syllables_in_line(line) for line in lines]
