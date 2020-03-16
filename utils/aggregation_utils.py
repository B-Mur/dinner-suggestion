import pandas as pd
import numpy as np
from functools import reduce


def aggregate(matches, method='avg'):
    '''This will perform the aggregation'''
    values = matches.values()
    values = [x for x in values if not np.isnan(x)]
    values.sort()
    # t-norms
    if method == 'min':
        agg = min(values)
    elif method == 'soft-min':
        agg = .6*values[0] + .2*values[1] + .1*values[2]

    elif method == 'dounbi-tnorm':
        lam, temp = .25, 0
        for val in values:
            val += np.finfo(float).tiny
            temp += ((1 / val) - 1) ** lam
        agg = (1 + temp ** (1/lam)) ** -1

    elif method == 'sklar1-tnorm':
        p, temp = .2, 0
        temp = reduce((lambda x, y: x**p + y**p), values)
        agg = max([0, temp - 1]) ** (1/p)

    elif method == 'sklar4-tnorm':
        p, num, den, mult = .2, 1, 0, 0
        num = reduce((lambda x, y: x * y), values)
        den = reduce((lambda x, y: x**p + y**p), values)
        mult = reduce((lambda x, y: x**p * y**p), values)

        agg = (num / (den - mult)**(1/p))

    elif method == 'multiply':
        agg = reduce((lambda x, y: x * y), values)

    # t-conorms
    elif method == 'dounbi-tconorm':
        lam, temp = .25, 0
        for val in values:
            val += np.finfo(float).tiny
            temp += ((1 / val) - 1) ** lam
        agg = (1 + temp ** (-1 / lam)) ** -1

    elif method == 'sklar1-tconorm':
        p, temp = .2, 0
        for val in values:
            temp += (1-val)**p

        agg = 1 - max([0, temp - (len(values) - 1)]) ** (1/p)

    elif method == 'sklar4-tconorm':
        p, num, den, mult = .6, 1, 0, 1

        for val in values:
            num *= (1-val)**p
            den += (1-val)**p
            mult *= (1-val)**p

        agg = 1 - (num / ((den - mult)**(1/p)))

    elif method == 'max':
        agg = max(values)

    elif method == 'avg':
        agg = np.mean(values)

    elif method == 'soft-max':
        agg = .6*values[3] + .2*values[2] + .1*values[1]

    return agg

