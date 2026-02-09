close_punc_for_open_punc = { '"': '"', '“': "”" }
open_punc_for_close_punc = {v: k for k, v in close_punc_for_open_punc.items()}

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
