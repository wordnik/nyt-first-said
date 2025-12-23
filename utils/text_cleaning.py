import regex

def remove_punctuation(text):
    cleaned = regex.sub(r"^\p{P}+", "", text)
    cleaned = regex.sub(r"\p{P}+$", "", cleaned)
    cleaned = regex.sub(r"’s", "", cleaned)
    return cleaned
