import syllapy
import re

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
