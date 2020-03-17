import requests
import json
import numpy as np
import pandas as pd
from utils.aggregation_utils import *
from utils.fuzzy_utils import *
from utils.ChI import *
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from actor import Actor
api_key=open('utils/yelp-key.txt').read()
headers = {'Authorization': 'Bearer %s' % api_key}



def search_terms(params):
    url = 'https://api.yelp.com/v3/businesses/search'
    req = requests.get(url, params=params, headers=headers)
    # proceed only if the status code is 200
    print('The status code is {}'.format(req.status_code))

    return json.loads(req.text)


def query_actor(main_actor):
    params = {'term': 'restaurant', 'location': 'Columbia, MO', 'categories':main_actor.cat[0]}
    request = search_terms(params)
    return pd.DataFrame(request['businesses'])


def generic_request():
    params = {'term': 'restaurant', 'location': 'Columbia, MO', 'limit':50}
    request = search_terms(params)
    return pd.DataFrame(request['businesses'])


if __name__ == '__main__':


    # Setup each actor
    bryce = Actor(name = 'Bryce', rating='=5', price='=$$',    travel='>.2', cat=['burger'], confidence=1)
    kate =  Actor(name = 'Kate',   rating='=3.5',   price='=$',   travel='<.5', cat=['chinese'], confidence=1)
    matt =  Actor(name = 'Matt',   rating='>3',   price='=$',    travel='>.6', cat=['italian'], confidence=1)

    c = ['rgba(21, 108, 138, .85)', 'rgba(255, 192, 0, .85)', 'rgba(72, 105, 131, .85)']


    aggs = ['avg']

    for agg in aggs:
        normalize_densities = True
        # Build list of actors
        actors = [bryce, kate, matt]
        fig = make_subplots(rows=len(actors)+1, cols=1)
        # Gotta get the one with the highest confidence
        #restaurants = generic_request()
        restaurants = pd.DataFrame()
        for actor in actors:
                # YELP only allows to search for 50 restaurants, so I do two queries to get more restaurants :
                # 3: Concatenate all results.
                actor_req = query_actor(actor)  # assumes COLUMBIA MO
                restaurants = pd.concat([restaurants, actor_req]).drop_duplicates(subset='id').reset_index(drop=True)


        # This is the only membership function that changes. It assigns memberships based on the 'closest'.
        dist_params = {'a': restaurants['distance'].min(), 'b': restaurants['distance'].max(), 'c': 1e10, 'd': 1e11}

        densities = []
        for actor in actors:
            restaurants[f'{actor.name}-score'] = ""
            densities.append(actor.confidence)
        densities = np.asarray(densities)
        if normalize_densities:
            densities = densities/np.sum(densities)

        for j, actor in enumerate(actors):
            for i, rest in enumerate(restaurants.iterrows()):
                # record score of actor to restaurant
                restaurants.at[i, f'{actor.name}-score'] = actor.match(rest[1], dist_params, aggregation=agg)
            fig.append_trace(go.Bar( y=restaurants[f'{actor.name}-score'], name=f'{actor.name} {actor.confidence}', marker=dict(color=c[j])), row=(j+1), col=1)

        chi = ChoquetIntegral()
        chi.train_chi_sugeno(np.asarray(densities))
        restaurants[f'total-score'] = ""
        for i, rest in enumerate(restaurants.iterrows()):
            inputs = []
            for actor in actors:
                inputs.append(restaurants.at[i, f'{actor.name}-score'])

            restaurants.at[i, f'total-score'] = chi.chi_sugeno(np.asarray(inputs))


        best_rest = restaurants.loc[np.argmax(restaurants['total-score'])]
        fig.append_trace(go.Bar(x=restaurants['alias'], y=restaurants[f'total-score'], name='Totals', marker=dict(color='rgba(0, 0, 0, .85)')), row=(j+2), col=1)

        fig.update_xaxes(tickfont=dict(size=14))
        fig.update_yaxes(tickfont=dict(size=14), range=[0, 1])
        fig.update_layout(title={'text': f'Winner : {best_rest["name"]} - Match : {best_rest["total-score"]:.2f}'})
        fig.show()



        print('a')