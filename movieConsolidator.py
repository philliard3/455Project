'''
This was the sandbox file where everything was tested.
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

'''
data_file = open("movie_data.txt", "w+")
data_file.write("budget,release_date,total_gross_seventh_day,num_theaters_seventh_day,final_domestic_gross\n")
for movie in final_list:
    movie_str = [str(m) for m in movie]
    data_file.write(",".join(movie_str)+"\n")
data_file.close()
'''

'''
trimmed_list = final_list

seven_day_gross = [i[2] for i in trimmed_list]

mean = np.average(seven_day_gross)
sd = np.std(seven_day_gross)

# print("the mean is", mean)
# print("the sd is", sd)

outlier = [(abs(mean-i)>(2*sd)) for i in seven_day_gross]
# print(outlier)
print("number of outliers by seven day gross:", sum(outlier))

final_list = []
for i, j in enumerate(outlier):
    if not(j):
        final_list.append(trimmed_list[i])

'''

indices = np.random.rand(int(len(final_list)))*len(final_list)
indices = list(set([int(i) for i in indices]))
if len(indices) > len(final_list)/2:
    indices = indices[:int(len(final_list)/2)]
print(len(final_list))
training = []
testing = []
for i, row in enumerate(final_list):
    if i in indices:
        training.append(row)
    else:
        testing.append(row)

print(len(testing))
print(len(training))

final_list = training

# final_list = [final_list[i] for i in list(set([int(i) for i in indices]))]
#

print("the final length is", len(final_list))

# pprint.pprint(final_list)


y = np.array([i[4] for i in final_list])
# x = np.array([i[0] for i in final_list])
# x = np.array([i[1] for i in final_list])
# x = np.array([i[2] for i in final_list])
x = np.array([i[3] for i in final_list])

'''
sd_x = np.sqrt(abs(np.average(x**2)-np.average(x)**2))
sd_y = np.sqrt(abs(np.average(y**2)-np.average(y)**2))
covariance = (np.average([x_i*y_i for x_i in x for y_i in y]) - np.average(x)*np.average(y))
correlation = covariance/(sd_x*sd_y)
print(correlation)
'''

correlation = np.corrcoef(x, y)
print("correlation:", correlation)

plt.scatter(x, y, c='b', label=("correlation coefficient = "+str(correlation[0][1])))

A = np.vstack([x, np.ones(len(x))]).T
m, c = np.linalg.lstsq(A, y)[0]
plt.plot(x, [m*x_i + c for x_i in x], c='r', label="linear least squares fit")

poly_coeff = np.polyfit(x, y, 3)
polyfit = np.poly1d(poly_coeff)
plt.plot(np.linspace(min(x), max(x), 10**5), [polyfit(x_i) for x_i in np.linspace(min(x), max(x), 10**5)], c='g', label="least squares fit (degree=3)")

# plt.title("The Effect of Budget on Total Domestic Gross")
# plt.title("The Effect of Release Date on Total Domestic Gross")
# plt.title("The Effect of 7-Day Gross on Total Domestic Gross")
plt.title("The Effect of Number of Theaters on Total Domestic Gross")

# plt.xlabel("Budget (USD)")
# plt.xlabel("Release Date")
# plt.xlabel("7-Day Gross (USD)")
plt.xlabel("Number of Theaters")

plt.ylabel("Total Gross (USD)")
plt.legend()
# plt.show()



plt.cla()

df = pd.DataFrame({"budget": [i[0] for i in final_list], "release_date": [i[1] for i in final_list], "7-day_gross": [i[2] for i in final_list], "num_theaters": [i[3] for i in final_list], "domestic_gross": [i[4] for i in final_list]})
# print(df)

X = df[["7-day_gross", "budget", "num_theaters", "release_date"]]
y = df["domestic_gross"]

X = sm.add_constant(X)

model = sm.OLS(y, X).fit()
predictions = model.predict(X)
# pd.DataFrame({"budget": [i[0] for i in testing], "release_date": [i[1] for i in testing], "7-day_gross": [i[2] for i in testing], "num_theaters": [i[3] for i in testing], "domestic_gross": [i[4] for i in testing]}))

plt.scatter(predictions, y, s=30, c='r', marker='+', zorder=10)
plt.plot(y, y)
plt.title("Prediction Model for Domestic Gross (Training Data)")
axes = plt.axes()
axes.set_xscale("log")
axes.set_yscale("log")

plt.xlabel("Predicted Revenue from Model")
plt.ylabel("Actual Revenue")
plt.show()
print("MSE:", model.mse_model)
print(model.summary())

plt.cla()

predictions = model.predict(pd.DataFrame({"budget": [i[0] for i in testing], "release_date": [i[1] for i in testing], "7-day_gross": [i[2] for i in testing], "num_theaters": [i[3] for i in testing], "domestic_gross": [i[4] for i in testing]}))

plt.scatter(predictions, y, s=30, c='r', marker='+', zorder=10)
plt.plot(y, y)
plt.title("Prediction Model for Domestic Gross (Testing Data)")
axes = plt.axes()
axes.set_xscale("log")
axes.set_yscale("log")

plt.xlabel("Predicted Revenue from Model")
plt.ylabel("Actual Revenue")
plt.show()


'''
coefficients = []
for index in range(len(final_list)-len(final_list[0])):
    a = [i[:-1] for i in final_list[index:index+len(final_list[0])-1]]
    pprint.pprint(a)
    b = [i[-1] for i in final_list[index:index+len(final_list[0])-1]]
    print(b)
    solution = np.linalg.solve(a, b)
    max_err = 0
    for movie in final_list:
        max_err = max(max_err, abs((movie[4] - sum([solution[j]*movie[j] for j in range(len(solution))]))))
    min_err = min(min_err, max_err)
    print(solution, max_err)

print(min_err)

'''


