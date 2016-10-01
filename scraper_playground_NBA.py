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

print scores
print streaks
print four_factors_headers
print four_factors_stats
print away_record_after
print home_record_after
print away_stats_headers
print away_stats_stats
print away_stats_players
print away_adv_headers
print away_adv_stats
print away_adv_players
print home_stats_headers
print home_stats_stats
print home_stats_players
print home_adv_headers
print home_adv_stats
print home_stats_players

"""
#Update dictionary
dictionary['teams'][away_team]['goals for'] = int(scores[0])
dictionary['teams'][away_team]['goals against'] = int(scores[1])
dictionary['teams'][home_team]['goals for'] = int(scores[1])
dictionary['teams'][home_team]['goals against'] = int(scores[0])

###
dictionary['teams'][away_team]['players'] = {}
for (player,stats) in zip(away_skaters_players,away_skaters_stats):
	dictionary['teams'][away_team]['players'][player] = {}
	for i,header in enumerate(away_skaters_headers):
		if i ==0:
			continue
		elif str(header) == 'Player':
			dictionary['teams'][away_team]['players'][player][str(header)] = str(stats[i-1]).strip()
		elif str(header) == 'TOI':
			dictionary['teams'][away_team]['players'][player][str(header)] = 60. * float(str(stats[i-1]).split(':')[0]) + float(str(stats[i-1]).split(':')[1])
		elif not str(stats[i-1]):
			dictionary['teams'][away_team]['players'][player][str(header)] = np.nan
		elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH':
			if i >= 6 and i <=8:
				dictionary['teams'][away_team]['players'][player]['G'+str(header)] = float(stats[i-1])
			elif i >= 10 and i <= 12:
				dictionary['teams'][away_team]['players'][player]['A'+str(header)] = float(stats[i-1])
		else:
			dictionary['teams'][away_team]['players'][player][str(header)] = float(stats[i-1])

for (player,stats) in zip(away_goalies_players,away_goalies_stats):
	dictionary['teams'][away_team]['players'][player] = {}
	for i,header in enumerate(away_goalies_headers):
		if i ==0:
			continue
		elif str(header) == 'Player':
			dictionary['teams'][away_team]['players'][player][str(header)] = str(stats[i-1]).strip()
		elif str(header) == 'DEC':
			if str(stats[i-1]):
				dictionary['teams'][away_team]['players'][player][str(header)] = str(stats[i-1]).strip()
				away_dec = str(stats[i-1]).strip()
			else:
				dictionary['teams'][away_team]['players'][player][str(header)] = np.nan
		elif str(header) == 'TOI':
			dictionary['teams'][away_team]['players'][player][str(header)] = 60. * float(str(stats[i-1]).split(':')[0]) + float(str(stats[i-1]).split(':')[1])
		elif not str(stats[i-1]):
			dictionary['teams'][away_team]['players'][player][str(header)] = np.nan
		else:
			dictionary['teams'][away_team]['players'][player][str(header)] = float(stats[i-1])
	
for (player,stats) in zip(away_adv_players,away_adv_stats):
	for i,header in enumerate(away_adv_headers):
		if i ==0:
			continue
		elif not str(stats[i-1]):
			dictionary['teams'][away_team]['players'][player][str("-".join(header.split(u'\u2011')))] = np.nan
		else:
			dictionary['teams'][away_team]['players'][player][str("-".join(header.split(u'\u2011')))] = float(stats[i-1])

###
dictionary['teams'][home_team]['players'] = {}
for (player,stats) in zip(home_skaters_players,home_skaters_stats):
	dictionary['teams'][home_team]['players'][player] = {}
	for i,header in enumerate(home_skaters_headers):
		if i ==0:
			continue
		elif str(header) == 'Player':
			dictionary['teams'][home_team]['players'][player][str(header)] = str(stats[i-1]).strip()
		elif str(header) == 'TOI':
			dictionary['teams'][home_team]['players'][player][str(header)] = 60. * float(str(stats[i-1]).split(':')[0]) + float(str(stats[i-1]).split(':')[1])
		elif not str(stats[i-1]):
			dictionary['teams'][home_team]['players'][player][str(header)] = np.nan
		elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH':
			if i >= 6 and i <=8:
				dictionary['teams'][home_team]['players'][player]['G'+str(header)] = float(stats[i-1])
			elif i >= 10 and i <= 12:
				dictionary['teams'][home_team]['players'][player]['A'+str(header)] = float(stats[i-1])		
		else:
			dictionary['teams'][home_team]['players'][player][str(header)] = float(stats[i-1])

for (player,stats) in zip(home_goalies_players,home_goalies_stats):
	dictionary['teams'][home_team]['players'][player] = {}
	for i,header in enumerate(home_goalies_headers):
		if i ==0:
			continue
		elif str(header) == 'Player':
			dictionary['teams'][home_team]['players'][player][str(header)] = str(stats[i-1]).strip()
		elif str(header) == 'DEC':
			if str(stats[i-1]):
				dictionary['teams'][home_team]['players'][player][str(header)] = str(stats[i-1]).strip()
				home_dec = str(stats[i-1]).strip()
			else:
				dictionary['teams'][home_team]['players'][player][str(header)] = np.nan
		elif str(header) == 'TOI':
			dictionary['teams'][home_team]['players'][player][str(header)] = 60. * float(str(stats[i-1]).split(':')[0]) + float(str(stats[i-1]).split(':')[1])
		elif not str(stats[i-1]):
			dictionary['teams'][home_team]['players'][player][str(header)] = np.nan
		else:
			dictionary['teams'][home_team]['players'][player][str(header)] = float(stats[i-1])
	
for (player,stats) in zip(home_adv_players,home_adv_stats):
	for i,header in enumerate(home_adv_headers):
		if i ==0:
			continue
		elif not str(stats[i-1]):
			dictionary['teams'][home_team]['players'][player][str("-".join(header.split(u'\u2011')))] = np.nan
		else:
			dictionary['teams'][home_team]['players'][player][str("-".join(header.split(u'\u2011')))] = float(stats[i-1])

###
away_record_after = [int(i) for i in str(away_record_after.strip('(').strip(')')).split('-')]
if away_dec == 'W':
	away_record_after[0] -= 1
elif away_dec == 'L':
	away_record_after[1] -= 1
elif away_dec == 'O':
	away_record_after[2] -= 1
dictionary['teams'][away_team]['record before']	= away_record_after
dictionary['teams'][away_team]['result'] = away_dec

home_record_after = [int(i) for i in str(home_record_after.strip('(').strip(')')).split('-')]
if home_dec == 'W':
	home_record_after[0] -= 1
elif home_dec == 'L':
	home_record_after[1] -= 1
elif home_dec == 'O':
	home_record_after[2] -= 1
dictionary['teams'][home_team]['record before']	= home_record_after
dictionary['teams'][home_team]['result'] = home_dec
"""
#-----------------------------------------------------------------------
"""
#-----------------------------------------------------------------------

#Sportsbookreview.com vegas odds

driver.get('http://www.sportsbookreview.com/betting-odds/nhl-hockey/?date=%s%s%s'%(year,month,day))
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
				
away_moneyline = moneylines[0]	
home_moneyline = moneylines[1]

driver.get('http://www.sportsbookreview.com/betting-odds/nhl-hockey/totals/?date=%s%s%s'%(year,month,day))
soup = BeautifulSoup(driver.page_source)		

total_number = 0.
for i in soup.find("div", attrs={"id":"eventLineOpener-%s-1096-o-3"%game_number}).find("span",attrs={"class":"adjust"}).get_text():
	total_number += unicodedata.numeric(i)
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

#test on blackhawks home and away to make sure home and away are the same
#test on muliple goalie games
#see if we need to put driver.get in loops to make fail-safe
"""
