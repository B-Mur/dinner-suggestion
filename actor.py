import numpy as np
import pandas as pd
from utils.aggregation_utils import *
from utils.fuzzy_utils import *

class Actor:
    """Class for each actor
    Expects inputs in the following formats :
    # name : str
    # rating : > or < or = followed by float from 1-5
    # price : > or < or = followed by up to 4 $'s
    # travel : scale of 0 - 1 for how close you prefer - 0 is the closest
    # confidence : how much do you care about which restaurant 0 - 1 - 1 being you care a lot."""



    def __init__(self, name = '', rating='', price='', travel='', cat=[''], confidence=''):
        self.name, self.rating, self.price, self.travel, self.cat = name, rating, price, travel, cat
        self.matches, self.confidence = {}, confidence
        self.validate_input()


    def match(self, restaurant, distance_params, aggregation):

        self.matches['rating'] = 1 - self.match_rating(restaurant['rating'])
        self.matches['price']   = 1 - self.match_price(restaurant['price'])
        self.matches['travel'] = 1 - self.match_distance(restaurant['distance'], distance_params)
        self.matches['cat']   = 1 - self.match_cat(restaurant['categories'])

        score = aggregate(self.matches, method=aggregation)

        if score < 0:
            print('a')
        return score


    def match_rating(self, rating):
        '''Match the restaurant rating.

        There are 3 different cases. Exact rating, less than or equal to rating,
        and greater than or equal to rating.'''
        if np.isnan(rating):
            return 0        # perfect match bc restaurant doesn't have this info
        if self.rating == '':
            return 0        # perfect match bc actor doesn't care

        rating_dist = (rating / 5) - (float(self.rating[1:]) / 5)

        if self.rating[0] == '=':
            rating_dist = np.abs(rating_dist)           # it wants the distance regardless of greater than or less than
        elif self.rating[0] == '>':
            if rating_dist > 0:
                rating_dist = 0                         # acceptable if greater than requested rating
            else:
                rating_dist = np.abs(rating_dist)       # not acceptable if less than requested rating
        else:
            if rating_dist < 0:
                rating_dist = 0                         # acceptable if less than requested rating
            else:
                rating_dist = np.abs(rating_dist)       # not acceptable if less than requested rating


        return rating_dist


    def match_price(self, price):
        '''Match the restaurant cost.

        There are 3 different cases. Exact cost, less than or equal to cost,
        and greater than or equal to cost.'''

        if self.price=='':
            return 0    # perfect match bc this actor doesn't care
        if type(price) is not type('str'):
            if np.isnan(price):
                return 0    # perfect match bc this actor doesn't care


        actor_dollar = len(self.price) - 1
        resta_dollar = len(price)

        price_dist = resta_dollar/3 - actor_dollar/3

        if self.price[0] == '=':
            price_dist = np.abs(price_dist)  # it wants the distance regardless of greater than or less than
        elif self.price[0] == '>':
            if price_dist > 0:
                price_dist = 0  # acceptable if greater than requested rating
            else:
                price_dist = np.abs(price_dist)  # not acceptable if less than requested rating
        else:
            if price_dist < 0:
                price_dist = 0  # acceptable if less than requested rating
            else:
                price_dist = np.abs(price_dist)  # not acceptable if less than requested rating

        return price_dist


    def match_cat(self, type):
        '''Match the restaurant type.

        If the word is in any of the categories, it's a match'''
        if self.cat == '':      # Perfect match because the actor doesn't care
            return 0
        for t in type:
            for c in self.cat:
                if c.lower() in t['title'].lower():
                    return 0                    # We matched

        return 1            # Never Matched


    def match_distance(self, distance, distance_params):
        '''Match the travel distance from curent location.

        Right now this one returns the relative closeness. This one needs to be fixed. '''

        if self.travel=='':
            return 0            # Doesn't care how far they have to travel.


        travel_dist = trapmf(distance, distance_params) - float(self.travel[1:])

        if self.travel[0] == '=':
            travel_dist = np.abs(travel_dist)  # it wants the distance regardless of greater than or less than
        elif self.travel[0] == '>':
            if travel_dist > 0:
                travel_dist = 0  # acceptable if greater than requested rating
            else:
                travel_dist = np.abs(travel_dist)  # not acceptable if less than requested rating
        else:
            if travel_dist < 0:
                travel_dist = 0  # acceptable if less than requested rating
            else:
                travel_dist = np.abs(travel_dist)  # not acceptable if less than requested rating

        return travel_dist


    def validate_input(self):
        '''Validate the inputs.

        '''
        if self.rating != '':
            assert self.rating[0] in ['=', '>',
                                          '<'], f'Rating not formatted correctly {self.rating}. Must start with > < ='

        if self.price != '':

            assert self.price[0] in ['=', '>',
                                     '<'], f'Price not formatted correctly {self.price}. Must start with > < ='
            assert self.price[
                       1] == '$', f'Price not formatted correctly {self.price}. Must start with be of the form =$xx'

        if self.travel != '':

            assert self.travel[0] in ['=', '>', '<'], f'Travel not formatted correctly {self.travel}.' \
                                                      f' Must start with > < ='
            t = float(self.travel[1:])
            assert t <= 1 and t > 0, f'Travel must be between (0, 1), not {t}'


