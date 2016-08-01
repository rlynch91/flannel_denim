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
away_skaters_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in away_skaters_table.find("thead").find_all("tr")][1]
away_skaters_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in away_skaters_table.find("tbody").find_all("tr")]
away_skaters_players = [element.find('a')['href'] for element in away_skaters_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

home_skaters_table = soup.find("table", attrs={"id":"%s_skaters"%home_team})
home_skaters_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in home_skaters_table.find("thead").find_all("tr")][1]
home_skaters_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in home_skaters_table.find("tbody").find_all("tr")]
home_skaters_players = [element.find('a')['href'] for element in home_skaters_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

away_goalies_table = soup.find("table", attrs={"id":"%s_goalies"%away_team})
away_goalies_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in away_goalies_table.find("thead").find_all("tr")][1]
away_goalies_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in away_goalies_table.find("tbody").find_all("tr")]
away_goalies_players = [element.find('a')['href'] for element in away_goalies_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

home_goalies_table = soup.find("table", attrs={"id":"%s_goalies"%home_team})
home_goalies_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in home_goalies_table.find("thead").find_all("tr")][1]
home_goalies_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in home_goalies_table.find("tbody").find_all("tr")]
home_goalies_players = [element.find('a')['href'] for element in home_goalies_table.find("tbody").find_all("td",attrs={"data-stat":"player"})]

away_adv_soup = BeautifulSoup(soup.find('div',attrs={"id":"all_%s_adv"%away_team}).find("div", attrs={"class":"placeholder"}).next_element)
away_adv_table = away_adv_soup.find("table", attrs={"id":"%s_adv"%away_team})
away_adv_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in away_adv_table.find("thead").find_all("tr")][0]
away_adv_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in away_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]
away_adv_players = [row.find('a')['href'] for row in away_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]

home_adv_soup = BeautifulSoup(soup.find('div',attrs={"id":"all_%s_adv"%home_team}).find("div", attrs={"class":"placeholder"}).next_element)
home_adv_table = home_adv_soup.find("table", attrs={"id":"%s_adv"%home_team})
home_adv_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in home_adv_table.find("thead").find_all("tr")][0]
home_adv_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in home_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]
home_adv_players = [row.find('a')['href'] for row in home_adv_table.find("tbody").find_all("tr",attrs={"class":"All-ALL"})]

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

#fix degeneracy between goals and assists

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
	away_nhl_rows = away_table.find("tbody").find_all("tr")
	for row in away_nhl_rows:
		away_nhl_headers += [[element.get_text().strip() for element in away_table.find("thead").find("tr").find_all("th")]]
		away_nhl_stats += [[datum.get_text().strip() for datum in row.find_all('td')]]
		away_nhl_players += [" ".join(row.find('a')['href'].split('/player/')[-1].split('-')[0:-1]).title()]

home_nhl_headers = []
home_nhl_stats = []
home_nhl_players = []
home_tables = soup.find("div", attrs={"class":"home"}).find_all("div",attrs={"class":"responsive-datatable"})
for home_table in home_tables:
	home_nhl_rows = home_table.find("tbody").find_all("tr")
	for row in home_nhl_rows:
		home_nhl_headers += [[element.get_text().strip() for element in home_table.find("thead").find("tr").find_all("th")]]
		home_nhl_stats += [[datum.get_text().strip() for datum in row.find_all('td')]]
		home_nhl_players += [" ".join(row.find('a')['href'].split('/player/')[-1].split('-')[0:-1]).title()]

#Update dictionary

#get team stats

###
for player,headers,stats in zip(away_nhl_players,away_nhl_headers,away_nhl_stats):
	for player_link in dictionary['teams'][away_team]['players']:
		if dictionary['teams'][away_team]['players'][player_link]['Player'].lower() == player.lower():
			for i,header in enumerate(headers):
				if i == 1:
					dictionary['teams'][away_team]['players'][player_link]['Position'] = str(header)
				elif dictionary['teams'][away_team]['players'][player_link].has_key(str(header)):
					pass
				elif str(header) == 'TOI' or str(header) == 'PP TOI' or str(header) == 'SH TOI':
					dictionary['teams'][away_team]['players'][player_link][str(header)] = 60. * float(str(stats[i]).split(':')[0]) + float(str(stats[i]).split(':')[1])
				elif stats[i]== u'\u2013':
					dictionary['teams'][away_team]['players'][player_link][str(header)] = np.nan
				elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH':
					dictionary['teams'][away_team]['players'][player_link]['SV ' + str(header)] = [float(j) for j in str(stats[i]).split('-')]
				elif str(header) == 'SAVE-SHOTS':
					pass
				else:
					dictionary['teams'][away_team]['players'][player_link][str(header)] = float(stats[i])
			break

###
for player,headers,stats in zip(home_nhl_players,home_nhl_headers,home_nhl_stats):
	for player_link in dictionary['teams'][home_team]['players']:
		if dictionary['teams'][home_team]['players'][player_link]['Player'].lower() == player.lower():
			for i,header in enumerate(headers):
				if i == 1:
					dictionary['teams'][home_team]['players'][player_link]['Position'] = str(header)
				elif dictionary['teams'][home_team]['players'][player_link].has_key(str(header)):
					pass
				elif str(header) == 'TOI' or str(header) == 'PP TOI' or str(header) == 'SH TOI':
					dictionary['teams'][home_team]['players'][player_link][str(header)] = 60. * float(str(stats[i]).split(':')[0]) + float(str(stats[i]).split(':')[1])
				elif stats[i]== u'\u2013':
					dictionary['teams'][home_team]['players'][player_link][str(header)] = np.nan
				elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH':
					dictionary['teams'][home_team]['players'][player_link]['SV ' + str(header)] = [float(j) for j in str(stats[i]).split('-')]
				elif str(header) == 'SAVE-SHOTS':
					pass
				else:
					dictionary['teams'][home_team]['players'][player_link][str(header)] = float(stats[i])
			break

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

#Update dictionary

#-----------------------------------------------------------------------

driver.quit()

#test on blackhawks home and away to make sure home and away are the same
#test on muliple goalie games
#see if we need to put driver.get in loops to make fail-safe
