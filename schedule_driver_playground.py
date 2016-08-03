from bs4 import BeautifulSoup
import requests
import pickle
import numpy as np
from selenium import webdriver
import unicodedata
import time
import datetime

#-----------------------------------------------------------------------

#Define July 1st to be day 0 of the year
def day_number_to_date(season_year,days_from_july1):
	"""
	Assumes July 1st to be day 0 of season for a given year, converts day number to date
	"""
	day_july1 = datetime.datetime(int(season_year), 7, 1, 0, 0).timetuple().tm_yday
	date = datetime.datetime(int(season_year), 1, 1) + datetime.timedelta(int(days_from_july1) + day_july1 - 1)
	return str(date.date()).split('-')

def date_to_day_number(season_year, date_year, date_month, date_day):
	"""
	Assumes July 1st to be day 0 of season for a given year, date to day number
	"""
	return (datetime.datetime(int(date_year), int(date_month), int(date_day), 0, 0) - datetime.datetime(int(season_year), 7, 1, 0, 0)).days


#-----------------------------------------------------------------------

#Initialize variables

year = '2016'

#-----------------------------------------------------------------------

#Hockey-reference.com schedules

page = requests.get("http://www.hockey-reference.com/leagues/NHL_%s_games.html"%(year))
soup = BeautifulSoup(page.text)

schedule_table = soup.find("table", attrs={"id":"games"})
schedule_dates = [str(element.get_text().strip()).split('-') for element in schedule_table.find("tbody").find_all("th",attrs={"data-stat":"date_game"})]
schedule_away_teams = [str(element['csk'].strip()).split('.')[0] for element in schedule_table.find("tbody").find_all("td",attrs={"data-stat":"visitor_team_name"})]
schedule_home_teams = [str(element['csk'].strip()).split('.')[0] for element in schedule_table.find("tbody").find_all("td",attrs={"data-stat":"home_team_name"})]

#-----------------------------------------------------------------------

print day_number_to_date(int(year),4)
print date_to_day_number(int(year),2016,7,5)
