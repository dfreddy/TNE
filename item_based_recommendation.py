import numpy as np
import pandas as pd
import pickle
import csv
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import string
import requests
import random
import time
from operator import itemgetter

## retrieve + organize data

data = pd.read_csv('database.csv')

data_user_id = data['user_id'].values
data_discount_id = data['discount_id'].values
data_score = data['score'].values
data_discount_name = data['discount_name'].values
data_category = data['category'].values
data_array = []

# all categories and discounts stored here
discounts = set()

# all individual user ids
users = []

## put all rows entries into a array of dicts
for i in range(len(data_user_id)):
    data_array_entry = {'user_id': data_user_id[i],
                        'discount_id': data_discount_id[i],
                        'score': data_score[i],
                        'discount_name': data_discount_name[i],
                        'category': data_category[i]
                        }
    data_array.append(data_array_entry)

# USER CATEGORY SCORES
## iterate data_array and find all user's average category scores
user_avg_category_scores = [] # stored as such: [ [user_id, category, sum_scores, nr_discounts_per_category], ... ]

def user_category_pair_exists(user, category, array):
    for i in range(len(array)):
        if user == array[i][0] and category == array[i][1]:
            return i
    return -1

for i in range(len(data_array)):
    user_id = data_array[i].get('user_id')
    score = data_array[i].get('score')
    category = data_array[i].get('category')

    index = user_category_pair_exists(user_id, category, user_avg_category_scores)
    if index == -1:
        user_avg_category_scores.append([user_id, category, score, 1])
    else:
        user_avg_category_scores[index][2] = user_avg_category_scores[index][2] + score
        user_avg_category_scores[index][3] = user_avg_category_scores[index][3] + 1

# updated structure as follows: [ [user_id, category, avg_scores], ... ]
for row in user_avg_category_scores:
    row[2] = row[2] / row[3]
    del row[3]

'''# prints the average scores for each user's categories
for row in user_avg_category_scores:
   print(row)
'''

# DISCOUNT GLOBAL SCORES
## iterate over the data the same way, in order to find each discount's avg score
discounts_global_scores = [] # stored as such [ [discount_id, discount_name, sum_scores, nr_discounts_with_scores, category], ... ]

def discount_already_stored(discount_id, array):
    for i in range(len(array)):
        if discount_id == array[i][0]:
            return i
    return -1

for i in range(len(data_array)):
    discount_name = data_array[i].get('discount_name')
    discount_id = data_array[i].get('discount_id')
    score = data_array[i].get('score')
    cat = data_array[i].get('category')

    index = discount_already_stored(discount_id, discounts_global_scores)
    if index == -1:
        discounts_global_scores.append([discount_id, discount_name, score, 1, cat])
    else:
        discounts_global_scores[index][2] = discounts_global_scores[index][2] + score
        discounts_global_scores[index][3] = discounts_global_scores[index][3] + 1

# updated structure as follows: [ [discount_id, discount_name, global_scores, category], ... ]
for row in discounts_global_scores:
    row[2] = row[2] / row[3]
    del row[3]

'''
for row in discounts_global_scores:
   print(row)
'''

# loads up user categories and starts the loop
def recommend(user_id):
    # [cat_name, score]
    user_categories = []
    total_cat_scores = 0
    for i in range(len(user_avg_category_scores)):
        if user_avg_category_scores[i][0] == user_id:
            user_categories.append([user_avg_category_scores[i][1], user_avg_category_scores[i][2]])
            total_cat_scores = total_cat_scores + user_avg_category_scores[i][2]

    return recommend_loop(user_id, user_categories, total_cat_scores)

# finds category and discount to recommend
# if found none inside the chosen category, retry without it
def recommend_loop(user_id, user_categories, total_cat_scores):
    # avert infinite loops
    if 1 > len(user_categories):
        print("Error: couldn't find a discount, as they have all been used by the user")
        return -1

    rand = random.uniform(0, total_cat_scores)
    index = 0
    rand_counter = 0
    for i in range(len(user_categories)):
        rand_counter = rand_counter + user_categories[i][1]
        if rand <= rand_counter:
            index = i
            break


    # found the randomly selected category
    category_name = user_categories[index][0]

    # find most scored discount in category, which the user hasn't give a 3 or 5
    discount_name = ''
    discount_id = 0
    top_score = 0
    for i in range(len(discounts_global_scores)):
        if discounts_global_scores[i][3] == category_name:
            # find user with user_id and discount_id matching the case
            user = next(item for item in data_array if item['user_id'] == user_id and item['discount_id'] == discounts_global_scores[i][0])
            if discounts_global_scores[i][2] > top_score and user['score'] < 3:
                # update top score and corresponding discount
                top_score = discounts_global_scores[i][2]
                discount_id = discounts_global_scores[i][0]
                discount_name = discounts_global_scores[i][1]

    # if the category that was randomly found has already been 100% used up by the user, run the recommend algo again
    if discount_id == 0:
        for i in range(len(user_categories)):
            if user_categories[i][0] == category_name:
                total_cat_scores = total_cat_scores - user_categories[i][1]
                del user_categories[i]
                break
        return recommend_loop(user_id, user_categories, total_cat_scores)
    else:
        result = [discount_id, discount_name, category_name]
        return result


# CALL RECOMMEND FUNCTION
user_id = 1
print('\nRecommend this discount -> ' + str(recommend(user_id)) + ' for user ' + str(user_id))

print("\nUser's category scores:")
for row in user_avg_category_scores:
    if row[0] == user_id:
        print(row)

print('\nGlobal discount scores not grade by user:')
discounts_global_scores.sort(key = lambda x: x[2], reverse = True)

for i in range(len(discounts_global_scores)):
    user = next(item for item in data_array if
                item['user_id'] == user_id and item['discount_id'] == discounts_global_scores[i][0])
    if user['score'] < 3:
        print(discounts_global_scores[i])