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
import math
import pprint
from operator import itemgetter

## retrieve + organize data

data = pd.read_csv('database.csv')

data_user_id = data['user_id'].values
data_discount_id = data['discount_id'].values
data_score = data['score'].values
data_discount_name = data['discount_name'].values
data_category = data['category'].values
data_array = []

# all individual discount ids
discount_ids = []
for i in range(len(data_discount_id)):
    if data_discount_id[i] not in discount_ids:
        discount_ids.append(data_discount_id[i])

# all individual user ids
users = []
for i in range(len(data_user_id)):
    if data_user_id[i] != data_user_id[i-1]:
        users.append(data_user_id[i])

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

def get_discount_name(discount):
    for i in range(len(data_array)):
        if data_array[i].get('discount_id') == discount:
            return data_array[i].get('discount_name')
    return None

def get_discount_category(discount):
    for i in range(len(data_array)):
        if data_array[i].get('discount_id') == discount:
            return data_array[i].get('category')
    return None

def user_category_pair_exists(user, category):
    for i in range(len(user_avg_category_scores)):
        if user == user_avg_category_scores[i][0] and category == user_avg_category_scores[i][1]:
            return i
    return -1

for i in range(len(data_array)):
    user_id = data_array[i].get('user_id')
    score = data_array[i].get('score')
    category = data_array[i].get('category')

    index = user_category_pair_exists(user_id, category)
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

# SIMILARITY
## iterate over users and store the similarity between user1 and user2 in a array of dicts as such: similarity[] = [{'user1', 'user2', 'score'}, ...]
## similarity function: pearson correlation
similarity = []

def get_user_category_score(user, cat):
    for i in range(len(user_avg_category_scores)):
        if user_avg_category_scores[i][0] == user and user_avg_category_scores[i][1] == cat:
            return user_avg_category_scores[i][2]
    return None

def get_user_discount_entry(user, d_id):
    for i in range(len(data_array)):
        if data_array[i].get('user_id') == user and data_array[i].get('discount_id') == d_id:
            return data_array[i]
    return None

def get_similarity(u1, u2):
    for i in range(len(similarity)):
        if similarity[i].get('user1') == u1 and similarity[i].get('user2') == u2:
            return similarity[i].get('score')
        if similarity[i].get('user1') == u2 and similarity[i].get('user2') == u1:
            return similarity[i].get('score')
    return None

def calculate_similarity_users(u1, u2):
    if u1 == u2:
        print("similarity error: u1 = " + str(u1) + " u2 = " + str(u2))
        return None

    if get_similarity(u1, u2) != None:
        print("similarity already calculated for " + str(u1) + ' ' + str(u2) + ": not None")
        return

    divident = 0
    divisor1 = 0
    divisor2 = 0
    for i in range(len(discount_ids)):
        ud1 = get_user_discount_entry(u1, discount_ids[i])
        ud2 = get_user_discount_entry(u2, discount_ids[i])
        rc1 = ud1.get('score') - get_user_category_score(ud1.get('user_id'), ud1.get('category'))
        rc2 = ud2.get('score') - get_user_category_score(ud2.get('user_id'), ud2.get('category'))

        divident = divident + rc1 * rc2
        divisor1 = divisor1 + rc1 ** 2
        divisor2 = divisor2 + rc2 ** 2

    sim_score = divident / math.sqrt(divisor1 * divisor2)
    similarity.append({
        'user1': u1,
        'user2': u2,
        'score': score
    })
    print('Similarity score between users (' + str(u1) + ', ' + str(u2) + ') = ' + str(sim_score))
    return sim_score


'''
## fill similarity array
for i in range(len(users)):
    for k in range(len(users)):
        calculate_similarity_users(users[i], users[k])
'''

## calculate normalized scores for each discount for a certain user
def calculate_user_normalized_scores(user):
    # array of {discount_id, normalized_score:}
    discount_normalized_scores = []

    # get user similarity with other users and normalizing factor
    k = 0
    for i in range(len(users)):
        if users[i] != user:
            sim = calculate_similarity_users(user, users[i])
            if sim != None:
                k = k + sim
    k = 1 / k

    for i in range(len(discount_ids)):
        user_rc = get_user_category_score(user, get_discount_category(discount_ids[i]))
        sim_sum = 0
        for j in range(len(users)):
            if users[j] == user:
                continue
            ud = get_user_discount_entry(users[j], discount_ids[i])
            rc = ud.get('score') - get_user_category_score(ud.get('user_id'), ud.get('category'))
            sim = get_similarity(user, users[j])

            sim_sum = sim_sum + sim * rc
        print('Normalized discount score for ' + str(discount_ids[i]) + ' = ' + str(user_rc + k * sim_sum))
        discount_normalized_scores.append({'discount_id': discount_ids[i],
                                           'discount name': get_discount_name(discount_ids[i]),
                                           'normalized score': int(user_rc + k * sim_sum),
                                           'category': get_discount_category(discount_ids[i])})

    return discount_normalized_scores


# loads up user categories and starts the loop
def recommend(user_id):
    # [cat_name, score]
    user_categories = []
    total_cat_scores = 0
    for i in range(len(user_avg_category_scores)):
        if user_avg_category_scores[i][0] == user_id:
            user_categories.append([user_avg_category_scores[i][1], user_avg_category_scores[i][2]])
            total_cat_scores = total_cat_scores + user_avg_category_scores[i][2]

    discounts = calculate_user_normalized_scores(user_id)

    return recommend_loop(user_id, user_categories, total_cat_scores, discounts)

# finds category and discount to recommend
# if found none inside the chosen category, retry without it
def recommend_loop(user_id, user_categories, total_cat_scores, discounts):
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

    # find most scored discount in category, which the user hasn't given a 3 or 5
    discount_id = 0
    top_score = 0
    for i in range(len(discounts)):
        discount_category = get_discount_category(discounts[i].get('discount_id'))
        if discount_category == category_name:
            # find user with user_id and discount_id matching the case
            user = next(item for item in data_array if item['user_id'] == user_id and item['discount_id'] == discounts[i].get('discount_id'))
            if discounts[i].get('normalized score') > top_score and user['score'] < 3:
                # update top score and corresponding discount
                top_score = discounts[i].get('normalized score')
                discount_id = discounts[i].get('discount_id')

    # if the category that was randomly found has already been 100% used up by the user, run the recommend algo again
    if discount_id == 0:
        for i in range(len(user_categories)):
            if user_categories[i][0] == category_name:
                total_cat_scores = total_cat_scores - user_categories[i][1]
                print('All discounts for ' + str(user_categories[i][0]) + ' have already been used')
                del user_categories[i]
                break
        return recommend_loop(user_id, user_categories, total_cat_scores, discounts)
    else:
        print('\nNormalized discount scores not grade by user:')
        discounts.sort(key=itemgetter('normalized score'), reverse=True)

        for i in range(len(discounts)):
            user = next(item for item in data_array if item['user_id'] == user_id and item['discount_id'] == discounts[i].get('discount_id'))
            if user['score'] < 3:
                print(discounts[i])

        discount_name = get_discount_name(discount_id)
        result = [discount_id, discount_name, category_name]
        return result


# CALL RECOMMEND FUNCTION
user_id = 1
print('\nRecommend this discount -> ' + str(recommend(user_id)) + ' for user ' + str(user_id))

print("\nUser's category scores:")
for row in user_avg_category_scores:
    if row[0] == user_id:
        print(row)