'''

This is used to create a multivariable linear regression.

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

print("number of outliers by number of theaters:", sum(outlier))

final_list = []
for i, j in enumerate(outlier):
    if not(j):
        final_list.append(trimmed_list[i])

indices = np.random.rand(int(len(final_list)))*len(final_list)
indices = list(set([int(i) for i in indices]))
if len(indices) > len(final_list)/2:
    indices = indices[:int(len(final_list)/2)]

training = []
testing = []
for i, row in enumerate(final_list):
    if i in indices:
        training.append(row)
    else:
        testing.append(row)

final_list = training
print(len(final_list))

y = np.array([i[4] for i in final_list])


df = pd.DataFrame({"budget": [i[0] for i in final_list], "release_date": [i[1] for i in final_list], "7-day_gross": [i[2] for i in final_list], "num_theaters": [i[3] for i in final_list], "domestic_gross": [i[4] for i in final_list]})

X = df[["7-day_gross", "budget", "num_theaters", "release_date"]]
y = df["domestic_gross"]

X = sm.add_constant(X)

model = sm.OLS(y, X).fit()
predictions = model.predict(X)

prediction_correlation = np.corrcoef(predictions, y)[0][1]
prediction_average_percent_error= np.average([abs(predictions[i] - y_i)/y_i for i, y_i in enumerate(y)])
prediction_mse = np.average([(predictions[i] - y_i)**2 for i, y_i in enumerate(y)])

plt.scatter(predictions, y, s=30, c='r', marker='+', zorder=10, label="correlation:"+str(prediction_correlation)+"\naverage percent error:"+str(prediction_average_percent_error)+"\nmse:"+str(prediction_mse))
plt.plot(y, y, label="y=x")

# Comment out one of the following according to what part of the data is used.
# plt.title("Prediction Model for Domestic Gross (Full Data)")
plt.title("Prediction Model for Domestic Gross (Training Data)")

axes = plt.axes()
axes.set_xscale("log")
axes.set_yscale("log")

plt.xlabel("Predicted Revenue from Model")
plt.ylabel("Actual Revenue")
plt.legend(loc="upper left")
plt.show()
print("MSE:", model.mse_model)
print(model.summary())

plt.cla()

# This creates a second graph based on the testing data. It should fail if the testing data is not the same size
#  as the training data. One example of such an instance would be an odd-numbered data set. Another such  example
#  would be the the times that the full data set is used in training.

predictions = model.predict(pd.DataFrame({"budget": [i[0] for i in testing], "release_date": [i[1] for i in testing], "7-day_gross": [i[2] for i in testing], "num_theaters": [i[3] for i in testing], "domestic_gross": [i[4] for i in testing]}))

prediction_correlation = np.corrcoef(predictions, y)[0][1]
prediction_average_percent_error = np.average([abs(predictions[i]-y_i)/y_i for i, y_i in enumerate(y)])
prediction_mse = np.average([(predictions[i] - y_i)**2 for i, y_i in enumerate(list(y))])


plt.scatter(predictions, y, s=30, c='r', marker='+', zorder=10, label="correlation:"+str(prediction_correlation)+"\naverage percent error:"+str(prediction_average_percent_error)+"\nmse:"+str(prediction_mse))
plt.plot(y, y, label="y=x")
plt.title("Prediction Model for Domestic Gross (Testing Data)")
axes = plt.axes()
axes.set_xscale("log")
axes.set_yscale("log")

plt.xlabel("Predicted Revenue from Model")
plt.ylabel("Actual Revenue")
plt.legend(loc="lower left")
plt.show()

