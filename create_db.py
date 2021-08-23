# import numpy as np
# import pandas as pd
# import pickle
import csv
# from bs4 import BeautifulSoup
# from urllib.request import urlopen, Request
# import string
# import requests
import random
import time
from operator import itemgetter

database = []

nr_users = 40

scores = [0, 1, 3, 5]

discounts = [
    ["queima", "social"],
    ["discoteca A", "social"],
    ["discoteca B", "social"],
    ["uber", "mobility"],
    ["cabify", "mobility"],
    ["daTerra", "food"],
    ["McDonalds", "food"],
    ["uber eats", "food"],
    ["avengers", "movies"],
    ["netflix", "movies"],
    ["spotify", "music"],
    ["apple music", "music"],
    ["tidal", "music"],
    ["zara", "fashion"],
    ["pull&bear", "fashion"],
    ["airbnb", "travel"],
    ["abreu", "travel"],
    ["sportszone", "sport"],
    ["gym", "sport"],
    ["bertrand", "study"],
    ["wook", "study"]]

# user_id, discount_id, score, discount_name, discount_category
database_entry = []

print("\nCreating Database\n")

db_pairs = [[False for i in range(len(discounts))] for j in range(nr_users)]

# create a database with a connection between every user and every discount
for i in range(nr_users):
    for j in range(len(discounts)):
        user_id = i
        discount_id = j
        score = random.choice(scores)
        database_entry = {
            'user_id': user_id+1,
            'discount_id': discount_id+1,
            'score': score,
            'discount_name': discounts[discount_id][0],
            'category': discounts[discount_id][1]
       }
        database.append(database_entry)

database.sort(key=itemgetter('user_id'))

print('Saving database to csv file')

with open('database.csv', 'w', newline='') as db_file:
    csv_writer =  csv.writer(db_file)
    csv_writer.writerow(['user_id', 'discount_id', 'score', 'discount_name', 'category'])
    for i in range(len(database)):
        csv_writer.writerow([
            database[i].get('user_id'),
            database[i].get('discount_id'),
            database[i].get('score'),
            database[i].get('discount_name'),
            database[i].get('category')
        ])