import numpy as np
import pickle

#Initialize dictionary
dictionary = {}

#-----------------------------------------------------------------------

#Anaheim
dictionary['ANA'] = {}
dictionary['ANA']['team'] = 'ANA'
dictionary['ANA']['team long'] = 'ducks'
dictionary['ANA']['team city'] = 'Anaheim'

#Arizona
dictionary['ARI'] = {}
dictionary['ARI']['team'] = 'ARI'
dictionary['ARI']['team long'] = 'coyotes'
dictionary['ARI']['team city'] = 'Arizona'

#Boston
dictionary['BOS'] = {}
dictionary['BOS']['team'] = 'BOS'
dictionary['BOS']['team long'] = 'bruins'
dictionary['BOS']['team city'] = 'Boston'

#Buffalo
dictionary['BUF'] = {}
dictionary['BUF']['team'] = 'BUF'
dictionary['BUF']['team long'] = 'sabres'
dictionary['BUF']['team city'] = 'Buffalo'

#Calgary
dictionary['CGY'] = {}
dictionary['CGY']['team'] = 'CGY'
dictionary['CGY']['team long'] = 'flames'
dictionary['CGY']['team city'] = 'Calgary'

#Carolina
dictionary['CAR'] = {}
dictionary['CAR']['team'] = 'CAR'
dictionary['CAR']['team long'] = 'hurricanes'
dictionary['CAR']['team city'] = 'Carolina'

#Chicago
dictionary['CHI'] = {}
dictionary['CHI']['team'] = 'CHI'
dictionary['CHI']['team long'] = 'blackhawks'
dictionary['CHI']['team city'] = 'Chicago'

#Colorado
dictionary['COL'] = {}
dictionary['COL']['team'] = 'COL'
dictionary['COL']['team long'] = 'avalanche'
dictionary['COL']['team city'] = 'Colorado'

#Columbus
dictionary['CBJ'] = {}
dictionary['CBJ']['team'] = 'CBJ'
dictionary['CBJ']['team long'] = 'bluejackets'
dictionary['CBJ']['team city'] = 'Columbus'

#Dallas
dictionary['DAL'] = {}
dictionary['DAL']['team'] = 'DAL'
dictionary['DAL']['team long'] = 'stars'
dictionary['DAL']['team city'] = 'Dallas'

#Detroit
dictionary['DET'] = {}
dictionary['DET']['team'] = 'DET'
dictionary['DET']['team long'] = 'redwings'
dictionary['DET']['team city'] = 'Detroit'

#Edmonton
dictionary['EDM'] = {}
dictionary['EDM']['team'] = 'EDM'
dictionary['EDM']['team long'] = 'oilers'
dictionary['EDM']['team city'] = 'Edmonton'

#Florida
dictionary['FLA'] = {}
dictionary['FLA']['team'] = 'FLA'
dictionary['FLA']['team long'] = 'panthers'
dictionary['FLA']['team city'] = 'Florida'

#Los Angeles
dictionary['LAK'] = {}
dictionary['LAK']['team'] = 'LAK'
dictionary['LAK']['team long'] = 'kings'
dictionary['LAK']['team city'] = 'Los Angeles'

#Minnesota
dictionary['MIN'] = {}
dictionary['MIN']['team'] = 'MIN'
dictionary['MIN']['team long'] = 'wild'
dictionary['MIN']['team city'] = 'Minnesota'

#Montreal
dictionary['MTL'] = {}
dictionary['MTL']['team'] = 'MTL'
dictionary['MTL']['team long'] = 'canadiens'
dictionary['MTL']['team city'] = 'Montreal'

#Nashville
dictionary['NSH'] = {}
dictionary['NSH']['team'] = 'NSH'
dictionary['NSH']['team long'] = 'predators'
dictionary['NSH']['team city'] = 'Nashville'

#New Jersey
dictionary['NJD'] = {}
dictionary['NJD']['team'] = 'NJD'
dictionary['NJD']['team long'] = 'devils'
dictionary['NJD']['team city'] = 'New Jersey'

#New York Islanders
dictionary['NYI'] = {}
dictionary['NYI']['team'] = 'NYI'
dictionary['NYI']['team long'] = 'islanders'
dictionary['NYI']['team city'] = 'N.Y. Islanders'

#New York Rangers
dictionary['NYR'] = {}
dictionary['NYR']['team'] = 'NYR'
dictionary['NYR']['team long'] = 'rangers'
dictionary['NYR']['team city'] = 'N.Y. Rangers'

#Ottawa
dictionary['OTT'] = {}
dictionary['OTT']['team'] = 'OTT'
dictionary['OTT']['team long'] = 'senators'
dictionary['OTT']['team city'] = 'Ottawa'

#Philadelphia
dictionary['PHI'] = {}
dictionary['PHI']['team'] = 'PHI'
dictionary['PHI']['team long'] = 'flyers'
dictionary['PHI']['team city'] = 'Philadelphia'

#Pittsburgh
dictionary['PIT'] = {}
dictionary['PIT']['team'] = 'PIT'
dictionary['PIT']['team long'] = 'penguins'
dictionary['PIT']['team city'] = 'Pittsburgh'

#San Jose
dictionary['SJS'] = {}
dictionary['SJS']['team'] = 'SJS'
dictionary['SJS']['team long'] = 'sharks'
dictionary['SJS']['team city'] = 'San Jose'

#St. Louis
dictionary['STL'] = {}
dictionary['STL']['team'] = 'STL'
dictionary['STL']['team long'] = 'blues'
dictionary['STL']['team city'] = 'St. Louis'

#Tampa Bay
dictionary['TBL'] = {}
dictionary['TBL']['team'] = 'TBL'
dictionary['TBL']['team long'] = 'lightning'
dictionary['TBL']['team city'] = 'Tampa Bay'

#Toronto
dictionary['TOR'] = {}
dictionary['TOR']['team'] = 'TOR'
dictionary['TOR']['team long'] = 'mapleleafs'
dictionary['TOR']['team city'] = 'Toronto'

#Vancouver
dictionary['VAN'] = {}
dictionary['VAN']['team'] = 'VAN'
dictionary['VAN']['team long'] = 'canucks'
dictionary['VAN']['team city'] = 'Vancouver'

#Washington
dictionary['WSH'] = {}
dictionary['WSH']['team'] = 'WSH'
dictionary['WSH']['team long'] = 'capitals'
dictionary['WSH']['team city'] = 'Washington'

#Winnipeg
dictionary['WPG'] = {}
dictionary['WPG']['team'] = 'WPG'
dictionary['WPG']['team long'] = 'jets'
dictionary['WPG']['team city'] = 'Winnipeg'

#-----------------------------------------------------------------------

pickle.dump(dictionary,open('NHL_teams_names.pkl','wt'))
