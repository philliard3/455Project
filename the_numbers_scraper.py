import requests
from bs4 import BeautifulSoup as soup
import pprint
import urllib
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pymongo

# establish Mongo database connection
client = pymongo.MongoClient()

# set up CMSC455 database and movies collection
moviedb = client.CMSC455.movies

# Retrieves weekly chart for the-numbers.com.
# This is now redundant since each movie's weekly data can be retrieved from its box office page.
def get_weekly_chart():

    b4 = datetime.datetime.now()
    url = "http://www.the-numbers.com/daily-box-office-chart"# "http://www.the-numbers.com/weekly-box-office-chart"

    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    page = requests.get(url, headers=headers)
    content = page.content
    page.close()

    page_soup = soup(content, "html.parser")
    chart = page_soup.findAll("table", {"border":"0", "cellpadding":"1", "align":"CENTER"})[0]
    weekly_data = []
    for i, tr in enumerate(chart.findAll("tr")):
        if i != 0:
            weekly_data.append({"place":i})
            for j, td in enumerate(tr.findAll("td")):
                if j == 2:
                    weekly_data[i-1]["title"] = td.findAll("a")[0].text
                    weekly_data[i-1]["movie_href"] = td.findAll("a")[0]["href"]
                elif j == 3:
                    weekly_data[i - 1]["distributor"] = td.findAll("a")[0].text
                    weekly_data[i - 1]["distributor_href"] = td.findAll("a")[0]["href"]
                elif j == 4:
                    weekly_data[i - 1]["gross"] = td.text
                elif j == 6:
                    weekly_data[i - 1]["num_theaters"] = td.text
                elif j == 9:
                    weekly_data[i - 1]["days_out"] = td.text
    print("total time = "+str(datetime.datetime.now()-b4))
    return weekly_data

# Retrieves the budget and day-by-day box office performances for each of the top 100 highest budget movies
def get_budgets(offset=0):

    b4 = datetime.datetime.now()

    # establish connection for scrape
    if offset:
        url = "http://www.the-numbers.com/movie/budgets/all/"+str(int(offset))+"01"
    else:
        url = "http://www.the-numbers.com/movie/budgets/all"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    page = requests.get(url, headers=headers)
    content = page.content
    page.close()

    # set up page data using beautiful soup
    page_soup = soup(content, "html.parser")
    chart = page_soup.findAll("center")[0].findAll("table")[0]
    budget_data = []

    # gets the title, budget, domestic and worldwide gross, and page link for each movie
    bi = 0
    for i, tr in enumerate(chart.findAll("tr")):

        if i > 0 and i%2 == 1:
            budget_data.append({"place": bi+1})
            for j, td in enumerate(tr.findAll("td")):
                if j == 1:
                    budget_data[bi]["release_date"] = td.text
                elif j == 2:
                    budget_data[bi]["title"] = td.text
                    budget_data[bi]["movie_href"] = td.a["href"]
                    budget_data[bi]["movie_href"] = "http://www.the-numbers.com" + str(budget_data[bi]["movie_href"]).split("#")[0] + "#tab=box-office"
                elif j == 3:
                    budget_data[bi]["budget"] = td.text
                elif j == 4:
                    budget_data[bi]["domestic_gross"] = td.text
                elif j == 5:
                    budget_data[bi]["worldwide_gross"] = td.text
            bi += 1

    # records the box office data for each movie by going to its page using the link provided
    for bd in budget_data:
        url = bd["movie_href"]
        box_page = requests.get(url, headers=headers)
        box_content = box_page.content
        box_page.close()

        bd["daily_earnings"] = []

        box_page_soup = soup(box_content, "html.parser")
        # sometimes a movie will not be in theaters yet, so a try is needed
        try:
            box_chart = box_page_soup.findAll("div", {"id":"box_office_chart"})[1].table

            for r_i, row in enumerate(box_chart.findAll("tr")):
                if r_i > 0:
                    bd["daily_earnings"].append({})
                    for c_i, col in enumerate(row.findAll("td")):
                        if c_i == 0:
                            bd["daily_earnings"][r_i-1]["date"] = col.text
                        elif c_i == 1:
                            bd["daily_earnings"][r_i - 1]["daily_rank"] = col.text
                        elif c_i == 2:
                            bd["daily_earnings"][r_i - 1]["daily_gross"] = col.text
                        elif c_i == 4:
                            bd["daily_earnings"][r_i - 1]["num_theaters"] = col.text
                        elif c_i == 6:
                            bd["daily_earnings"][r_i - 1]["total_gross"] = col.text
                        elif c_i == 7:
                            bd["daily_earnings"][r_i - 1]["days_since_release"] = col.text
        except:
            pprint.pprint(bd)

    print("total time = " + str(datetime.datetime.now() - b4))
    return budget_data

if __name__ == "__main__":

    start_page = 0
    end_page = 5
    i = start_page
    while i < end_page:
        movie_data = get_budgets(i)
        print("data gotten",i)
        i += 1
        {
            "title":"Avatar"
        }
        for movie in movie_data:
            # only store movies that have been in the box office for a week
            if len(movie["daily_earnings"]) > 7:
                if len(list(moviedb.find(
                        {"title": movie["title"],
                         "movie_href": movie["movie_href"],
                         "release_date": movie["release_date"]}
                ))) > 0:
                    print("updating")
                    '''moviedb.find_one_and_update(
                        {"title": movie["title"],
                         "movie_href": movie["movie_href"],
                         "release_date": movie["release_date"]
                        },{"$set":{
                            "place": movie["place"],
                            "domestic_gross": movie["domestic_gross"],
                            "worldwide_gross": movie["worldwide_gross"],
                            "daily_earnings": movie["daily_earnings"]}})'''
                else:
                    print("inserting")
                    # moviedb.insert_one(movie)

    pprint.pprint(movie_data[0])
    '''
    movie_test_avatar = list(moviedb.find({"title":"Avatar"}))[0]
    pprint.pprint(movie_test_avatar)
    '''
