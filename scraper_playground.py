from bs4 import BeautifulSoup
import requests
import pickle
import numpy as np
from selenium import webdriver
import unicodedata

#-----------------------------------------------------------------------

#Initialize variables

year = '2016'
month = '03'
day = '20'
away_team = 'MIN'
home_team = 'CHI'
home_team_long = 'blackhawks'
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

#Hockey-reference.com box scores

page = requests.get("http://www.hockey-reference.com/boxscores/%s0%s.html"%(year+month+day,home_team))
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

away_heading = soup.find("div", attrs={"id":"all_%s_skaters"%away_team})
away_record_after = away_heading.find('h2').get_text().strip().split()[-1]

home_heading = soup.find("div", attrs={"id":"all_%s_skaters"%home_team})
home_record_after = home_heading.find('h2').get_text().strip().split()[-1]

away_skaters_table = soup.find("table", attrs={"id":"%s_skaters"%away_team})
away_skaters_headers = [row.get_text().strip() for row in away_skaters_table.find("thead").find_all("tr")][1]
away_skaters_stats = [row.get_text().strip() for row in away_skaters_table.find("tbody").find_all("tr")]
away_skaters_players = [datum.find('a')['href'] for datum in away_skaters_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

home_skaters_table = soup.find("table", attrs={"id":"%s_skaters"%home_team})
home_skaters_headers = [row.get_text().strip() for row in home_skaters_table.find("thead").find_all("tr")][1]
home_skaters_stats = [row.get_text().strip() for row in home_skaters_table.find("tbody").find_all("tr")]
home_skaters_players = [datum.find('a')['href'] for datum in home_skaters_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

away_goalies_table = soup.find("table", attrs={"id":"%s_goalies"%away_team})
away_goalies_headers = [row.get_text().strip() for row in away_goalies_table.find("thead").find_all("tr")][1]
away_goalies_stats = [row.get_text().strip() for row in away_goalies_table.find("tbody").find_all("tr")]
away_goalies_players = [datum.find('a')['href'] for datum in away_goalies_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

home_goalies_table = soup.find("table", attrs={"id":"%s_goalies"%home_team})
home_goalies_headers = [row.get_text().strip() for row in home_goalies_table.find("thead").find_all("tr")][1]
home_goalies_stats = [row.get_text().strip() for row in home_goalies_table.find("tbody").find_all("tr")]
home_goalies_players = [datum.find('a')['href'] for datum in home_goalies_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

away_adv_soup = BeautifulSoup(soup.find('div',attrs={"id":"all_%s_adv"%away_team}).find("div", attrs={"class":"placeholder"}).next_element)
away_adv_table = away_adv_soup.find("table", attrs={"id":"%s_adv"%away_team})
away_adv_headers = [row.get_text().strip() for row in away_adv_table.find("thead").find_all("tr")]
away_adv_stats = [row.get_text().strip() for row in away_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]
away_adv_players = [row.find('a')['href'] for row in away_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]

home_adv_soup = BeautifulSoup(soup.find('div',attrs={"id":"all_%s_adv"%home_team}).find("div", attrs={"class":"placeholder"}).next_element)
home_adv_table = home_adv_soup.find("table", attrs={"id":"%s_adv"%home_team})
home_adv_headers = [row.get_text().strip() for row in home_adv_table.find("thead").find_all("tr")]
home_adv_stats = [row.get_text().strip() for row in home_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]
home_adv_players = [row.find('a')['href'] for row in home_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]


#Update dictionary
dictionary['teams'][away_team]['goals for'] = int(scores[0])
dictionary['teams'][away_team]['goals against'] = int(scores[1])
dictionary['teams'][home_team]['goals for'] = int(scores[1])
dictionary['teams'][home_team]['goals against'] = int(scores[0])

dictionary['teams'][away_team]['players'] = {}
for (player,stats) in zip(away_skaters_players,away_skaters_stats):
	dictionary['teams'][away_team]['players'][player] = {}
	headers = away_skaters_headers.split()
	stats = stats.split()
	
	player_name = ""
	i_name = 1
	while True:
		try:
			__ = float(stats[i_name])
			break
		except ValueError:
			player_name += str(stats[i_name]) + " "
			i_name += 1
	dictionary['teams'][away_team]['players'][player][str(headers[1])] = player_name.strip()
	for i in np.arange(2,7):
		dictionary['teams'][away_team]['players'][player][str(headers[i])] = float(stats[i+i_name-2])
	for i in np.arange(7,11):
		dictionary['teams'][away_team]['players'][player][str(headers[i])+' goals'] = float(stats[i+i_name-2])
	for i in np.arange(11,14):
		dictionary['teams'][away_team]['players'][player][str(headers[i])+' assists'] = float(stats[i+i_name-2])
	dictionary['teams'][away_team]['players'][player][str(headers[14])] = float(stats[14+i_name-2])
	if len(stats) == 18:
		dictionary['teams'][away_team]['players'][player][str(headers[15])] = np.nan
		dictionary['teams'][away_team]['players'][player][str(headers[16])] = float(stats[16+i_name-3])
	elif len(stats) == 19:
		dictionary['teams'][away_team]['players'][player][str(headers[15])] = float(stats[15+i_name-2])
		dictionary['teams'][away_team]['players'][player][str(headers[16])] = float(stats[16+i_name-2])
	dictionary['teams'][away_team]['players'][player][str(headers[-1])] = str(stats[-1])

dictionary['teams'][home_team]['players'] = {}
for (player,stats) in zip(home_skaters_players,home_skaters_stats):
	dictionary['teams'][home_team]['players'][player] = {}
	headers = home_skaters_headers.split()
	stats = stats.split()
	
	player_name = ""
	i_name = 1
	while True:
		try:
			__ = float(stats[i_name])
			break
		except ValueError:
			player_name += str(stats[i_name]) + " "
			i_name += 1
	dictionary['teams'][home_team]['players'][player][str(headers[1])] = player_name.strip()
	for i in np.arange(2,7):
		dictionary['teams'][home_team]['players'][player][str(headers[i])] = float(stats[i+i_name-2])
	for i in np.arange(7,11):
		dictionary['teams'][home_team]['players'][player][str(headers[i])+' goals'] = float(stats[i+i_name-2])
	for i in np.arange(11,14):
		dictionary['teams'][home_team]['players'][player][str(headers[i])+' assists'] = float(stats[i+i_name-2])
	dictionary['teams'][home_team]['players'][player][str(headers[14])] = float(stats[14+i_name-2])
	if len(stats) == 18:
		dictionary['teams'][home_team]['players'][player][str(headers[15])] = np.nan
		dictionary['teams'][home_team]['players'][player][str(headers[16])] = float(stats[16+i_name-3])
	elif len(stats) == 19:
		dictionary['teams'][home_team]['players'][player][str(headers[15])] = float(stats[15+i_name-2])
		dictionary['teams'][home_team]['players'][player][str(headers[16])] = float(stats[16+i_name-2])
	dictionary['teams'][home_team]['players'][player][str(headers[-1])] = str(stats[-1])

#Get goalie info, parse for game decision
#Link advanced stats to each player
#Use decision to find team record before game
	

#-----------------------------------------------------------------------

#NHL.com box scores

schedule_page = requests.get("https://www.nhl.com/%s/schedule/%s/ET"%(home_team_long,year+'-'+month+'-'+day))
schedule_soup = BeautifulSoup(schedule_page.text)
nhl_game_num = schedule_soup.find("a", attrs={"title":"Recap"})['href'].split('/')[-1]

driver = webdriver.PhantomJS()
driver.get("https://www.nhl.com/gamecenter/%s-vs-%s/%s/%s/%s/%s#game=%s,game_state=final,game_tab=boxscore"%(away_team.lower(),home_team.lower(),year,month,day,nhl_game_num,nhl_game_num))
soup = BeautifulSoup(driver.page_source)

team_table = soup.find("div",attrs={"class":"statistics__season-stats"})
nhl_team_headers = team_table.find("thead").find("tr").get_text().strip().split()
nhl_team_stats = [row.get_text().split() for row in team_table.find("tbody").find_all("tr")]
away_nhl_team_stats = nhl_team_stats[0]
home_nhl_team_stats = nhl_team_stats[1]

away_nhl_headers = []
away_nhl_stats = []
away_nhl_players = []
away_tables = soup.find("div", attrs={"class":"away"}).find_all("div",attrs={"class":"responsive-datatable"})
for away_table in away_tables:
	away_nhl_headers += [away_table.find("thead").find("tr").get_text().strip().split()]
	away_nhl_rows = away_table.find("tbody").find_all("tr")
	for row in away_nhl_rows:
		away_nhl_stats += [[datum.get_text().strip() for datum in row.find_all('td')]]
		away_nhl_players += [" ".join(row.find('a')['href'].split('/player/')[-1].split('-')[0:2]).title()]

home_nhl_headers = []
home_nhl_stats = []
home_nhl_players = []
home_tables = soup.find("div", attrs={"class":"home"}).find_all("div",attrs={"class":"responsive-datatable"})
for home_table in home_tables:
	home_nhl_headers += [home_table.find("thead").find("tr").get_text().strip().split()]
	home_nhl_rows = home_table.find("tbody").find_all("tr")
	for row in home_nhl_rows:
		home_nhl_stats += [[datum.get_text().strip() for datum in row.find_all('td')]]
		home_nhl_players += [" ".join(row.find('a')['href'].split('/player/')[-1].split('-')[0:2]).title()]

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
				
away_moneylines = moneylines[0]	
home_moneylines = moneylines[1]

driver.get('http://www.sportsbookreview.com/betting-odds/nhl-hockey/totals/?date=%s%s%s'%(year,month,day))
soup = BeautifulSoup(driver.page_source)		

total_number = 0.
for i in soup.find("div", attrs={"id":"eventLineOpener-%s-1096-o-3"%game_number}).find("span",attrs={"class":"adjust"}).get_text():
	total_number += unicodedata.numeric(i)
total_line_over = soup.find("div", attrs={"id":"eventLineOpener-%s-1096-o-3"%game_number}).find("span",attrs={"class":"price"}).get_text()
total_line_under = soup.find("div", attrs={"id":"eventLineOpener-%s-1096-u-3"%game_number}).find("span",attrs={"class":"price"}).get_text()

#-----------------------------------------------------------------------

driver.quit()
