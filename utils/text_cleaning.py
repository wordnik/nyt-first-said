import regex
from unicodedata import normalize

trouble_chars = [
    r"\t",
    r"\n",
    r"\x0b",
    r"\x0c",
    r"\r",
    r"\xc2\x85",
    r"\xc2\xa0",
    r"\xe1\x9a\x80",
    r"\xe1\xa0\x8e",
    r"\xe2\x80\x80",
    r"\xe2\x80\x81",
    r"\xe2\x80\x82",
    r"\xe2\x80\x83",
    r"\xe2\x80\x84",
    r"\xe2\x80\x85",
    r"\xe2\x80\x86",
    r"\xe2\x80\x87",
    r"\xe2\x80\x88",
    r"\xe2\x80\x89",
    r"\xe2\x80\x8a",
    r"\xe2\x80\x8b",
    r"\xe2\x80\x8c",
    r"\xe2\x80\x8d",
    r"\xe2\x80\xa8",
    r"\xe2\x80\xa9",
    r"\xe2\x80\xaf",
    r"\xe2\x81\x9f",
    r"\xe2\x81\xa0",
    r"\xe3\x80\x80",
    r"\xef\xbb\xbf",
    r"\xa0",
    r"\u200D",
    r"\u200D",
    r"¯"
    ]

def remove_punctuation(text):
    cleaned = regex.sub(r"^\p{P}+", "", text)
    cleaned = regex.sub(r"\p{P}+$", "", cleaned)
    cleaned = regex.sub(r"’s", "", cleaned)
    return cleaned

def remove_trouble_characters(text):
    # https://stackoverflow.com/questions/2227921/simplest-way-to-get-a-complete-list-of-all-the-utf-8-whitespace-characters-in-ph

    cleaned = text
    # Zero-width joiner
    # cleaned = regex.sub(r"\u200D", "", text)
    # Non-breaking space
    # cleaned = regex.sub(r"\u00A0", "", cleaned)
    for trub in trouble_chars:
        cleaned = regex.sub(trub, " ", cleaned)

    # Keep things in the Basic Multilingual Plane, so we don't get fake bold
    # characters like 𝗱𝗮𝘁𝗮 and further restrict it to Latin character blocks.
    cleaned = "".join([c for c in cleaned if is_in_latin_block(c)])
    # Remove double+ spaces.
    cleaned = regex.sub(r"\s+", " ", cleaned)
    # Remove soft hyphen.
    cleaned = cleaned.replace(chr(0xad), "")

    return cleaned

def has_username(text):
    if not text.find("@") == -1:
        return True
    return False

# https://unicodeplus.com/block
# We want the first five blocks, which contain characters that can be found
# in English, plus punctuation.
def is_in_latin_block(char):
    code_point = ord(char)
    return code_point <= 0x02AF or (code_point > 0x1FFF and code_point <= 0x206F)

def prepare_text_for_textblob(text):
    # u200b is a zero-width space (https://en.wikipedia.org/wiki/Zero-width_space)
    # that trips up TextBlob.
    cleaned = text.replace(u"\u200b", " ")
    # Get TextBlob to parse things on the sides of the emdash as separate words.
    cleaned = cleaned.replace("—", "-")
    cleaned = cleaned.replace("–", "-")
    cleaned = cleaned.replace("‑", "-")
    # Zero-width nonbreaking space
    cleaned = cleaned.replace("﻿", "")

    return cleaned
