import regex

def remove_punctuation(text):
    cleaned = regex.sub(r"^\p{P}+", "", text)
    cleaned = regex.sub(r"\p{P}+$", "", cleaned)
    cleaned = regex.sub(r"’s", "", cleaned)
    return cleaned

def remove_trouble_characters(text):
    # Zero-width joiner
    cleaned = regex.sub(r"\u200D", "", text)
    # Non-breaking space
    cleaned = regex.sub(r"\u00A0", "", cleaned)

    return cleaned

def has_username(text):
    if not text.find("@") == -1:
        return True
    return False
