#!/usr/bin/env python3

import math


# thanks http://stackoverflow.com/a/20007730
def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n/10) % 10 != 1) *
                     (n % 10 < 4)*n % 10::4])
