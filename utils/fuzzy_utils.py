import pandas as pd
import numpy as np
''' In this file, I've hard coded several of the membership functions for each of the parameters.'''


def trapmf(x, args):
    '''Trapezoidal membership function'''
    a, b, c, d = args['a'], args['b'], args['c'], args['d']
    val = 0
    if x < a or x > d:
        val = 0
    elif a < x and x <= b:
        val = (x - a) / (b - a)
    elif b <= x and x <= c:
        val = 1
    elif c<=x and x <= d:
        val = (d - x) / (d-c)


    return val





