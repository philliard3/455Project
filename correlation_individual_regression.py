'''
This creates an individual linear  and polynomial fit for the data, one data field at a time.
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pprint
import pymongo
import statsmodels.api as sm

# establish Mongo database connection
client = pymongo.MongoClient()

# set up CMSC455 database and movies collection
moviedb = client.CMSC455.movies

raw_movies = list(moviedb.find({}))
# print("the length is", len(raw_movies))

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

# print("the mean is", mean)
# print("the sd is", sd)

outlier = [(abs(mean-i)>(2*sd)) for i in num_theaters]
# print(outlier)
print("number of outliers by number of theaters:", sum(outlier))

final_list = []
for i, j in enumerate(outlier):
    if not(j):
        final_list.append(trimmed_list[i])

print("the final length is", len(final_list))

'''
The following segment begins sections of commented materials that correspond to the fields of the data.
As long as the same line is active in each "###" segment, the data will be displayed correctly.
'''

y = np.array([i[4] for i in final_list])

###
# x = np.array([i[0] for i in final_list])
# x = np.array([i[1] for i in final_list])
# x = np.array([i[2] for i in final_list])
x = np.array([i[3] for i in final_list])
###

correlation = np.corrcoef(x, y)
print("correlation:", correlation)

plt.scatter(x, y, c='b', label=("correlation coefficient = "+str(correlation[0][1])))

A = np.vstack([x, np.ones(len(x))]).T
m, c = np.linalg.lstsq(A, y)[0]
linear_y = [m*x_i + c for x_i in x]

linear_average_percent_error = np.average([abs(y_i-linear_y[i])/y_i for i, y_i in enumerate(y)])
linear_mse = np.average([(y_i-linear_y[i])**2 for i, y_i in enumerate(y)])

plt.plot(x, linear_y, c='r', label="linear least squares fit\naverage percent error:"+str(linear_average_percent_error)+"\nmse:"+str(linear_mse))

poly_coeff = np.polyfit(x, y, 3)
polyfit = np.poly1d(poly_coeff)

polyfit_x = list(x)
polyfit_x.sort()

polyfit_average_percent_error = np.average([abs(y[i] - polyfit(x_i))/y[i] for i, x_i in enumerate(x)])
polyfit_mse = np.average([(y[i] - polyfit(x_i))**2 for i, x_i in enumerate(x)])

plt.plot(polyfit_x, [polyfit(x_i) for x_i in polyfit_x], c='g', label="least squares fit (degree=3)\naverage percent error:"+str(polyfit_average_percent_error)+"\nmse:"+str(polyfit_mse))

###
# plt.title("The Effect of Budget on Total Domestic Gross")
# plt.title("The Effect of Release Date on Total Domestic Gross")
# plt.title("The Effect of 7-Day Gross on Total Domestic Gross")
plt.title("The Effect of Number of Theaters on Total Domestic Gross")
###

###
# plt.xlabel("Budget (USD)")
# plt.xlabel("Release Date")
# plt.xlabel("7-Day Gross (USD)")
plt.xlabel("Number of Theaters")
###

plt.ylabel("Total Gross (USD)")
plt.legend()
plt.show()
