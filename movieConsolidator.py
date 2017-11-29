import numpy as np
import matplotlib.pyplot as plt
import datetime
import pprint
import pymongo
from scipy.interpolate import interp1d
import sklearn.linear_model as lm

# establish Mongo database connection
client = pymongo.MongoClient()

# set up CMSC455 database and movies collection
moviedb = client.CMSC455.movies

raw_movies = list(moviedb.find({}))
print("the length is", len(raw_movies))

trimmed_list = []
for movie in raw_movies:
    trimmed_list.append([
        int("".join(((movie["budget"].split("$"))[1]).split(","))),
        (datetime.datetime.strptime(movie["release_date"], "%m/%d/%Y") - datetime.datetime.fromtimestamp(0)).total_seconds(),
        int("".join(((movie["daily_earnings"][6]["total_gross"]).split("$")[1]).split(","))),
        int("".join(movie["daily_earnings"][6]["num_theaters"].split(","))),
        int("".join((movie["domestic_gross"].split("$")[1]).split(",")))
    ])

# this segment trims the list to exclude outliers by number of theaters
# a possible cause of these outliers is advance screenings (one movie only had 4 theaters on its seventh day)

num_theaters = [i[3] for i in trimmed_list]

mean = np.average(num_theaters)
sd = np.std(num_theaters)

print("the mean is", mean)
print("the sd is", sd)

outlier = [(abs(mean-i)>(2*sd)) for i in num_theaters]
print(outlier)
print(sum(outlier))

final_list = []
for i, j in enumerate(outlier):
    if not(j):
        final_list.append(trimmed_list[i])

print("the final length is", len(final_list))

pprint.pprint(final_list)
