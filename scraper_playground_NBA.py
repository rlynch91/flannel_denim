from bs4 import BeautifulSoup
import requests
import pickle
import numpy as np
from selenium import webdriver
import unicodedata
import time

#-----------------------------------------------------------------------

#Initialize variables

year = '2015'
month = '10'
day = '27'
away_team = 'CLE'
home_team = 'CHI'
home_team_long = 'bulls'
home_team_city = "Chicago"

#-----------------------------------------------------------------------

#Initialize dictionary in which to store everything
dictionary = {}

dictionary['date'] = {}
dictionary['date']['day'] = day
dictionary['date']['month'] = month
dictionary['date']['year'] = year

dictionary['teams'] = {}
dictionary['teams'][away_team] = {}
dictionary['teams'][away_team]['location'] = 'away'

dictionary['teams'][home_team] = {}
dictionary['teams'][home_team]['location'] = 'home'

#-----------------------------------------------------------------------

#Basketball-reference.com box scores

page = requests.get("http://www.basketball-reference.com/boxscores//%s0%s.html"%(year+month+day,home_team))
soup = BeautifulSoup(page.text)

scores = []
streaks = []
scorebox = soup.find("div", attrs={"class":"scorebox"})
elements = scorebox.find_all("div")
for i,div in enumerate(elements):
	if div.has_attr('class'):
		if div['class'][0] == 'score':
			scores += [elements[i].get_text().strip()]
			streaks += [elements[i+1].get_text().strip()]

four_factors_soup = BeautifulSoup(soup.find("div", attrs={"id":"all_four_factors"}).find("div",attrs={"class":"placeholder"}).next_element.next_element)
four_factors_table = four_factors_soup.find("table", attrs={"id":"four_factors"})
four_factors_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in four_factors_table.find_all("tr",attrs={"class":"thead"})]
four_factors_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in four_factors_table.find_all("tr")]

away_heading = soup.find("div", attrs={"id":"all_box_%s_basic"%away_team.lower()})
away_record_after = away_heading.find('h2').get_text().strip().split()[-1]

home_heading = soup.find("div", attrs={"id":"all_box_%s_basic"%home_team.lower()})
home_record_after = home_heading.find('h2').get_text().strip().split()[-1]

away_stats_table = soup.find("table", attrs={"id":"box_%s_basic"%away_team.lower()})
away_stats_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in away_stats_table.find("thead").find_all("tr")][1]
away_stats_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in away_stats_table.find("tbody").find_all("tr")]
away_stats_players = [element.find('a') for element in away_stats_table.find("tbody").find_all("th",attrs={"data-stat":"player"})]

away_adv_table = soup.find("table", attrs={"id":"box_%s_advanced"%away_team.lower()})
away_adv_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in away_adv_table.find("thead").find_all("tr")][1]
away_adv_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in away_adv_table.find("tbody").find_all("tr")]
away_adv_players = [element.find('a') for element in away_adv_table.find("tbody").find_all("th",attrs={"data-stat":"player"})]

home_stats_table = soup.find("table", attrs={"id":"box_%s_basic"%home_team.lower()})
home_stats_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in home_stats_table.find("thead").find_all("tr")][1]
home_stats_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in home_stats_table.find("tbody").find_all("tr")]
home_stats_players = [element.find('a') for element in home_stats_table.find("tbody").find_all("th",attrs={"data-stat":"player"})]

home_adv_table = soup.find("table", attrs={"id":"box_%s_advanced"%home_team.lower()})
home_adv_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in home_adv_table.find("thead").find_all("tr")][1]
home_adv_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in home_adv_table.find("tbody").find_all("tr")]
home_adv_players = [element.find('a') for element in home_adv_table.find("tbody").find_all("th",attrs={"data-stat":"player"})]

#Update dictionary
dictionary['teams'][away_team]['points for'] = int(scores[0])
dictionary['teams'][away_team]['points against'] = int(scores[1])
dictionary['teams'][home_team]['points for'] = int(scores[1])
dictionary['teams'][home_team]['points against'] = int(scores[0])
if int(scores[0]) > int(scores[1]):
	dictionary['teams'][away_team]['result'] = 'W'
	dictionary['teams'][home_team]['result'] = 'L'
elif int(scores[1]) > int(scores[0]):
	dictionary['teams'][away_team]['result'] = 'L'
	dictionary['teams'][home_team]['result'] = 'W'
	
###
dictionary['teams'][away_team]['players'] = {}
for (player_raw,stats) in zip(away_stats_players,away_stats_stats):
	if player_raw:
		if str(stats[0]) != 'Did Not Play':
			player = player_raw['href']
			player_name = player_raw.get_text().strip()
			dictionary['teams'][away_team]['players'][player] = {}
			for i,header in enumerate(away_stats_headers):
				if str(header) == 'Starters':
					dictionary['teams'][away_team]['players'][player]['Player'] = str(player_name)
				elif str(header) == 'MP':
					dictionary['teams'][away_team]['players'][player][str(header)] = 60. * float(str(stats[i-1]).split(':')[0]) + float(str(stats[i-1]).split(':')[1])
				elif not str(stats[i-1]):
					dictionary['teams'][away_team]['players'][player][str(header)] = np.nan
				else:
					dictionary['teams'][away_team]['players'][player][str(header)] = float(stats[i-1])
											
for (player_raw,stats) in zip(away_adv_players,away_adv_stats):
	if player_raw:
		if str(stats[0]) != 'Did Not Play':
			player = player_raw['href']	
			for i,header in enumerate(away_adv_headers):
				if str(header) == 'Starters':
					continue
				elif str(header) == 'MP':
					continue
				elif not str(stats[i-1]):
					dictionary['teams'][away_team]['players'][player][str(header)] = np.nan
				else:
					dictionary['teams'][away_team]['players'][player][str(header)] = float(stats[i-1])

###
dictionary['teams'][home_team]['players'] = {}
for (player_raw,stats) in zip(home_stats_players,home_stats_stats):
	if player_raw:
		if str(stats[0]) != 'Did Not Play':
			player = player_raw['href']
			player_name = player_raw.get_text().strip()
			dictionary['teams'][home_team]['players'][player] = {}
			for i,header in enumerate(home_stats_headers):
				if str(header) == 'Starters':
					dictionary['teams'][home_team]['players'][player]['Player'] = str(player_name)
				elif str(header) == 'MP':
					dictionary['teams'][home_team]['players'][player][str(header)] = 60. * float(str(stats[i-1]).split(':')[0]) + float(str(stats[i-1]).split(':')[1])
				elif not str(stats[i-1]):
					dictionary['teams'][home_team]['players'][player][str(header)] = np.nan
				else:
					dictionary['teams'][home_team]['players'][player][str(header)] = float(stats[i-1])
											
for (player_raw,stats) in zip(home_adv_players,home_adv_stats):
	if player_raw:
		if str(stats[0]) != 'Did Not Play':
			player = player_raw['href']	
			for i,header in enumerate(home_adv_headers):
				if str(header) == 'Starters':
					continue
				elif str(header) == 'MP':
					continue
				elif not str(stats[i-1]):
					dictionary['teams'][home_team]['players'][player][str(header)] = np.nan
				else:
					dictionary['teams'][home_team]['players'][player][str(header)] = float(stats[i-1])

###
away_record_after = [int(i) for i in str(away_record_after.strip('(').strip(')')).split('-')]
if dictionary['teams'][away_team]['result'] == 'W':
	away_record_after[0] -= 1
elif dictionary['teams'][away_team]['result'] == 'L':
	away_record_after[1] -= 1
dictionary['teams'][away_team]['record before']	= away_record_after

home_record_after = [int(i) for i in str(home_record_after.strip('(').strip(')')).split('-')]
if dictionary['teams'][home_team]['result'] == 'W':
	home_record_after[0] -= 1
elif dictionary['teams'][home_team]['result'] == 'L':
	home_record_after[1] -= 1
dictionary['teams'][home_team]['record before']	= home_record_after

###
dictionary['teams'][away_team]['four factors'] = {}
dictionary['teams'][home_team]['four factors'] = {}
for i,header in enumerate(four_factors_headers[1]):
	if i == 0:
		continue
	else:
		dictionary['teams'][away_team]['four factors'][str(header)] = float(four_factors_stats[2][i-1])
		dictionary['teams'][home_team]['four factors'][str(header)] = float(four_factors_stats[3][i-1])

#-----------------------------------------------------------------------

#Sportsbookreview.com vegas odds

driver = webdriver.PhantomJS()
driver.get('http://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=%s%s%s'%(year,month,day))
soup = BeautifulSoup(driver.page_source)

team_name_soup = soup.find_all("span",attrs={"class":"team-name"})
for team in team_name_soup:
	if team.get_text() == home_team_city:
		game_number = team.find("a")['href'].split('-')[-1].strip('/')
		break

moneylines = []
team_lines = soup.find_all("div", attrs={"class":"eventLine-book-value"})
i_team = 0	
for line in team_lines:
	if line.has_attr('id'):
		if line['id'].split('-')[1] == game_number and line['id'].split('-')[2] == '1096':
			moneylines += [line.get_text()]
			if i_team >= 1:
				break
			else:
				i_team += 1

away_moneyline = str(moneylines[0])
home_moneyline = str(moneylines[1])

driver.get('http://www.sportsbookreview.com/betting-odds/nba-basketball/totals/?date=%s%s%s'%(year,month,day))
soup = BeautifulSoup(driver.page_source)		

total_number = ''
for char in soup.find("div", attrs={"id":"eventLineOpener-%s-1096-o-3"%game_number}).find("span",attrs={"class":"adjust"}).get_text():
	try:
		total_number += str(char)
	except UnicodeEncodeError:
		total_number += str(unicodedata.numeric(char)).strip('0')
total_line_over = soup.find("div", attrs={"id":"eventLineOpener-%s-1096-o-3"%game_number}).find("span",attrs={"class":"price"}).get_text()
total_line_under = soup.find("div", attrs={"id":"eventLineOpener-%s-1096-u-3"%game_number}).find("span",attrs={"class":"price"}).get_text()

#Update dictionary
dictionary['teams'][away_team]['team money line'] = float(away_moneyline)
dictionary['teams'][home_team]['team money line'] = float(home_moneyline)

dictionary['O/U'] = {}
dictionary['O/U']['O/U line'] = float(total_number)
dictionary['O/U']['O money line'] = float(total_line_over)
dictionary['O/U']['U money line'] = float(total_line_under)

#-----------------------------------------------------------------------

driver.quit()

#test on bulls home and away to make sure home and away are the same
#see if we need to put driver.get in loops to make fail-safe

