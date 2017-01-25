#!/usr/bin/env python3

from string import ascii_lowercase


def rank_label(rank):
    assert rank > 0
    rank -= 1
    quotient, remainder = divmod(rank, len(ascii_lowercase))
    return chr(ord('a') + remainder) * (quotient + 1)
