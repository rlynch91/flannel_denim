from bs4 import BeautifulSoup
import requests
import pickle
import numpy as np

#-----------------------------------------------------------------------

away_team = 'CHI'
home_team = 'MIN'
date = '2013'+'01'+'30'

page = requests.get("http://www.hockey-reference.com/boxscores/%s0%s.html"%(date,home_team))
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
