import regex

def remove_punctuation(text):
    return regex.sub(r"’s", "", regex.sub(r"\p{P}+$", "", regex.sub(r"^\p{P}+", "", text)))
