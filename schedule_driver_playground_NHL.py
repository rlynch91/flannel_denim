from bs4 import BeautifulSoup
import requests
import pickle
import numpy as np
from selenium import webdriver
import unicodedata
import time
import datetime
import scraper_playground_NHL

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

year = '2015' #Starting year of season
team_names = pickle.load(open('NHL_teams_names.pkl'))
dictionary = {}

#-----------------------------------------------------------------------

#Hockey-reference.com schedules
count = 0
while count < 10:
	try:
		page = requests.get("http://www.hockey-reference.com/leagues/NHL_%s_games.html"%(int(year)+1))
		soup = BeautifulSoup(page.text)

		schedule_table = soup.find("table", attrs={"id":"games"})
		schedule_dates = [str(element.get_text().strip()).split('-') for element in schedule_table.find("tbody").find_all("th",attrs={"data-stat":"date_game"})]
		schedule_away_teams = [str(element['csk'].strip()).split('.')[0] for element in schedule_table.find("tbody").find_all("td",attrs={"data-stat":"visitor_team_name"})]
		schedule_home_teams = [str(element['csk'].strip()).split('.')[0] for element in schedule_table.find("tbody").find_all("td",attrs={"data-stat":"home_team_name"})]
		break
	except AttributeError:
		print count
		count += 1

#-----------------------------------------------------------------------

#Loop through schedule, scraping each game
games_info = zip(schedule_dates, schedule_away_teams, schedule_home_teams)
for game_num,(game_date,game_away,game_home) in enumerate(games_info):
	try:	
		print game_num, game_date, game_away, game_home
		
		#Convert date to day number
		day_num = date_to_day_number(year,game_date[0],game_date[1],game_date[2])
		
		#Scrape data for this game
		if not day_num in dictionary.keys():
			dictionary[day_num] = {}
		dictionary[day_num][game_num] = scraper_playground_NHL.executable(game_date[0],game_date[1],game_date[2],game_away,game_home,team_names[game_home]['team long'],team_names[game_home]['team city'])
	
	except Exception as e:
		dictionary[day_num][game_num] = np.nan
			
#Save dictionary
pickle.dump(dictionary,open('data/scraped_%s_%s.pkl'%(int(year),int(year)+1),'wt'))
