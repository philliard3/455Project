
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

movie_test_avatar = moviedb.find_one({"title":"Avatar"})
pprint.pprint(movie_test_avatar)

days = [0]
gross = [0]


for i, date in enumerate(movie_test_avatar["daily_earnings"]):
    days.append(float(date["days_since_release"]))
    gross.append(float("".join(date["daily_gross"].strip('$').split(',')))+gross[i])

old_days = list(days)

days = np.array(days)
gross = np.array(gross)#  * 0.00001

f1 = interp1d(days, gross)
f2 = interp1d(days, gross, kind='cubic')
x = np.linspace(0,max(days), max(days)/10)

plt.plot(days, gross, 'o', color='k', markersize=3.5, label="raw data")
# plt.plot(days, f1(days), '-', color='b', linewidth=1.25)
# plt.plot(x, f2(x), '-', color='r', linewidth=1.25)

# f3 is a logistic regression of the data
'''
f3 = lm.LogisticRegression()
print("gross shape: ", gross.shape)
print("days shape: ", days.shape)
# f3.fit(days.reshape(len(days), 1), gross.reshape(len(gross), 1))
f3.fit(np.ravel(days), np.ravel(gross))
f3_y = [f3.predict(x_i) for x_i in x]
plt.plot(x, f3_y, label="logistic")

new_days = days
for i in range(300, 1000):
    days.append(i)
'''

coefficients = np.polyfit(days, gross, deg=5)
f4 = [(sum([coef*time**(len(coefficients)-j-1) for j, coef in enumerate(coefficients)])) for time in days]
maxError = max(np.array(gross)-np.array(f4))
print("Max Error was: ",maxError)
avgError = np.mean(np.array(gross)-np.array(f4))
print("Avg Error was: ", avgError)
plt.plot(days, f4, label="least squares polynomial")
plt.show()
