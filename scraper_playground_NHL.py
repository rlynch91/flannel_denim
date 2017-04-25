from bs4 import BeautifulSoup
import requests
import pickle
import numpy as np
from selenium import webdriver
import unicodedata
import time

#-----------------------------------------------------------------------

###
def executable(year, month, day, away_team, home_team, home_team_long, home_team_city):

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

	count = 0
	while count < 10:
		try:
			page = requests.get("http://www.hockey-reference.com/boxscores/%s0%s.html"%(year+month+day,home_team))
			soup = BeautifulSoup(page.text)

			scores = []
			records_after = []
			scorebox = soup.find("div", attrs={"class":"scorebox"})
			elements = scorebox.find_all("div")
			for i,div in enumerate(elements):
				if div.has_attr('class'):
					if div['class'][0] == 'score':
						scores += [elements[i].get_text().strip()]
						records_after += [elements[i+1].get_text().strip()]

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

			away_adv_soup = BeautifulSoup(soup.find('div',attrs={"id":"all_advanced"}).find("div", attrs={"class":"placeholder"}).next_element.next_element)
			away_adv_table = away_adv_soup.find("table", attrs={"id":"%s_adv"%away_team})
			away_adv_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in away_adv_table.find("thead").find_all("tr")][0]
			away_adv_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in away_adv_table.find("tbody").find_all("tr",attrs={"class":"ALLAll"})]
			away_adv_players = [row.find('a')['href'] for row in away_adv_table.find("tbody").find_all("tr",attrs={"class":"ALLAll"})]

			home_adv_soup = BeautifulSoup(soup.find('div',attrs={"id":"all_advanced"}).find("div", attrs={"class":"placeholder"}).next_element.next_element)
			home_adv_table = home_adv_soup.find("table", attrs={"id":"%s_adv"%home_team})
			home_adv_headers = [[element.get_text().strip() for element in row.find_all("th")] for row in home_adv_table.find("thead").find_all("tr")][0]
			home_adv_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in home_adv_table.find("tbody").find_all("tr",attrs={"class":"ALLAll"})]
			home_adv_players = [row.find('a')['href'] for row in home_adv_table.find("tbody").find_all("tr",attrs={"class":"ALLAll"})]	
			break
		except AttributeError:
			print count
			count += 1

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
			elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH' or str(header) == 'GW':
				if i >= 7 and i <= 10:
					dictionary['teams'][away_team]['players'][player]['G'+str(header)] = float(stats[i-1])
				elif i >= 11 and i <= 13:
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
			elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH' or str(header) == 'GW':
				if i >= 7 and i <=10:
					dictionary['teams'][home_team]['players'][player]['G'+str(header)] = float(stats[i-1])
				elif i >= 11 and i <= 13:
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
	away_record_after = [int(i) for i in str(records_after[0].strip('(').strip(')')).split('-')]
	if away_dec == 'W':
		away_record_after[0] -= 1
	elif away_dec == 'L':
		away_record_after[1] -= 1
	elif away_dec == 'O':
		away_record_after[2] -= 1
	dictionary['teams'][away_team]['record before']	= away_record_after
	dictionary['teams'][away_team]['result'] = away_dec

	home_record_after = [int(i) for i in str(records_after[1].strip('(').strip(')')).split('-')]
	if home_dec == 'W':
		home_record_after[0] -= 1
	elif home_dec == 'L':
		home_record_after[1] -= 1
	elif home_dec == 'O':
		home_record_after[2] -= 1
	dictionary['teams'][home_team]['record before']	= home_record_after
	dictionary['teams'][home_team]['result'] = home_dec

	#-----------------------------------------------------------------------

	#NHL.com box scores

	count = 0
	while count < 10:
		try:
			driver = webdriver.PhantomJS()
			driver.get("https://www.nhl.com/%s/schedule/%s/ET/list"%(home_team_long,year+'-'+month+'-'+day))
			schedule_soup = BeautifulSoup(driver.page_source)
			nhl_game_num = schedule_soup.find("tbody", attrs={"style":"display: table-row-group;"}).find("a", attrs={"class":"icon-label-pair icon-label-pair-recap"})['href'].split('/')[-1]
			driver.quit()
			break
		except AttributeError:
			driver.quit()
			print count
			count += 1

	count = 0
	while count < 10:
		try:
			driver = webdriver.PhantomJS()
			driver.get("https://www.nhl.com/gamecenter/%s-vs-%s/%s/%s/%s/%s#game=%s,game_state=final,game_tab=stats"%(away_team.lower(),home_team.lower(),year,month,day,nhl_game_num,nhl_game_num))
			soup = BeautifulSoup(driver.page_source)

			team_table = soup.find("div",attrs={"class":"statistics__season-stats"})
			nhl_team_headers = [element.get_text().strip() for element in team_table.find("thead").find("tr").find_all("th")]
			nhl_team_stats = [[element.get_text().strip() for element in row.find_all("td")] for row in team_table.find("tbody").find_all("tr")]
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
			driver.quit()
			break
		except AttributeError:
			driver.quit()
			print count
			count += 1

	#Update dictionary

	###
	for i,header in enumerate(nhl_team_headers):
		if i == 0:
			pass
		elif str(header) == 'FO%':
			dictionary['teams'][away_team][str(header)] = float(str(away_nhl_team_stats[i]).split('%')[0])/100.
			dictionary['teams'][home_team][str(header)] = float(str(home_nhl_team_stats[i]).split('%')[0])/100.
		elif str(header) == 'PP':
			dictionary['teams'][away_team][str(header)] = [float(j) for j in str(away_nhl_team_stats[i]).split('/')]
			dictionary['teams'][home_team][str(header)] = [float(j) for j in str(home_nhl_team_stats[i]).split('/')]
		else:
			dictionary['teams'][away_team][str(header)] = float(away_nhl_team_stats[i])
			dictionary['teams'][home_team][str(header)] = float(home_nhl_team_stats[i])
			
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
						try:
							dictionary['teams'][away_team]['players'][player_link][str(header)] = 60. * float(str(stats[i]).split(':')[0]) + float(str(stats[i]).split(':')[1])
						except ValueError:
							dictionary['teams'][away_team]['players'][player_link][str(header)] = 0.
					
					elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH' or str(header) == 'SAVE-SHOTS':
						dictionary['teams'][away_team]['players'][player_link]['SV ' + str(header)] = [float(j) for j in stats[i].split(u'\u2013')]
					
					elif not str(stats[i]) or str(stats[i]) == '--':
						dictionary['teams'][away_team]['players'][player_link][str(header)] = np.nan
					
					elif str(header) == 'FO%':
						dictionary['teams'][away_team]['players'][player_link][str(header)] = float(stats[i])/100.
					
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
						try:
							dictionary['teams'][home_team]['players'][player_link][str(header)] = 60. * float(str(stats[i]).split(':')[0]) + float(str(stats[i]).split(':')[1])
						except ValueError:
							dictionary['teams'][home_team]['players'][player_link][str(header)] = 0.
					
					elif str(header) == 'EV' or str(header) == 'PP' or str(header) == 'SH' or str(header) == 'SAVE-SHOTS':
						dictionary['teams'][home_team]['players'][player_link]['SV ' + str(header)] = [float(j) for j in stats[i].split(u'\u2013')]
					
					elif not str(stats[i]) or str(stats[i]) == '--':
						dictionary['teams'][home_team]['players'][player_link][str(header)] = np.nan
					
					elif str(header) == 'FO%':
						dictionary['teams'][home_team]['players'][player_link][str(header)] = float(stats[i])/100.
					
					else:
						dictionary['teams'][home_team]['players'][player_link][str(header)] = float(stats[i])
				break

	#-----------------------------------------------------------------------

	#Sportsbookreview.com vegas odds

	count = 0
	while count < 10:
		try:
			driver = webdriver.PhantomJS()
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
							
			away_moneyline = str(moneylines[0])	
			home_moneyline = str(moneylines[1])
			driver.quit()
			break
		except AttributeError:
			driver.quit()
			print count
			count += 1

	count = 0
	while count < 10:
		try:
			driver = webdriver.PhantomJS()
			driver.get('http://www.sportsbookreview.com/betting-odds/nhl-hockey/totals/?date=%s%s%s'%(year,month,day))
			soup = BeautifulSoup(driver.page_source)		

			total_number = ''
			for char in soup.find("div", attrs={"id":"eventLineOpener-%s-1096-o-3"%game_number}).find("span",attrs={"class":"adjust"}).get_text():
				try:
					total_number += str(char)
				except UnicodeEncodeError:
					total_number += str(unicodedata.numeric(char)).strip('0')
			total_line_over = soup.find("div", attrs={"id":"eventLineOpener-%s-1096-o-3"%game_number}).find("span",attrs={"class":"price"}).get_text()
			total_line_under = soup.find("div", attrs={"id":"eventLineOpener-%s-1096-u-3"%game_number}).find("span",attrs={"class":"price"}).get_text()
			driver.quit()
			break
		except AttributeError:
			driver.quit()
			print count
			count += 1

	#Update dictionary
	dictionary['teams'][away_team]['team money line'] = float(away_moneyline)
	dictionary['teams'][home_team]['team money line'] = float(home_moneyline)

	dictionary['O/U'] = {}
	dictionary['O/U']['O/U line'] = float(total_number)
	dictionary['O/U']['O money line'] = float(total_line_over)
	dictionary['O/U']['U money line'] = float(total_line_under)

	#-----------------------------------------------------------------------

	#Return final dictionary
	return dictionary
