import regex

close_punc_for_open_punc = { '"': '"', '“': "”" }
open_punc_for_close_punc = {v: k for k, v in close_punc_for_open_punc.items()}
invalid_word_exps = [
    r".*[\^=\+\\~].*"
]

def has_balanced_punctuation(s):
    unmatched_chars = []
    for char in s:
        if char in unmatched_chars:
            unmatched_chars.remove(char)
        else:
            if char in close_punc_for_open_punc:
                unmatched_chars.append(close_punc_for_open_punc[char])
            else:
                if char in open_punc_for_close_punc:
                    unmatched_chars.append(open_punc_for_close_punc[char])

        # print("unmatched_chars:", unmatched_chars)
    return len(unmatched_chars) == 0

def contains_line_breaks(s):
    return s.find("\n") != -1

def word_has_bad_char(word):
    for expr in invalid_word_exps:
        if regex.match(expr, word) != None:
            return True
    return False
