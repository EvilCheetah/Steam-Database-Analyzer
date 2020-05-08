'''
	Author: Eugene Moshchyn
'''

import urllib.request
import csv
import re
import json
from time import sleep
from bs4 import BeautifulSoup

import CONST


class Analyzer:

	def __init__(self):
		#Structure of _currencyList dictionary:
		#Key:
		#	- Name of currency						///_currencyList[CURRENCY_NAME][0]
		#	- Place in Table(SUM)						///_currencyList[CURRENCY_NAME][1]
		#	- Number of Games Available					///_currencyList[CURRENCY_NAME][2]
		#	- Sale(SUM)							///_currencyList[CURRENCY_NAME][3]
		#	- Number of Games Unavailable 					///_currencyList[CURRENCY_NAME][4]
		#	  to purchase(Price - N/A)		
		#	- Total Spends							///_currencyList[CURRENCY_NAME][5]
		#
		#Due to the low percent yield of the average formula due to float type limitations
		#all the average values will be holding the SUM. Average values will be derived from
		#SUM[Place or Sale] / Number of Avalilable
		self._currencyList = {}
		
		#Holding the number of FREE games 
		#AND/OR
		#The games that don't exist(don't have the price table)
		#on SteamDB
		self._freeGamesNum =  0
		
		#To keep the 
		self._toBeProcessedGameID = []
		
		self.initializeCurrencyList()
		self.getGamesList()
	
	def initializeCurrencyList(self):
		#Based on the Currency table of Half-Life(ID = 70) will be created
		#Dictionary list
		page = self.getCurrencyTable(CONST.CURRENCY_INIT_APP_ID)
		page = self.processTheTable(page)
		for i in range( len(page) ):
			self._currencyList[ page[i][0] ] = {
					"name": 		page[i][0], 
					"avgPlace": 	  	0.0, 
					"numAvailable":   	0, 
					"avgModifier": 	  	0.0, 
					"numUnavailable": 	0, 
					"spends":		0.0
					}

	def getGamesList(self):
		try:	
			with open("array.txt", 'r') as inFile:
				reader = csv.reader(inFile)
				inArray = ( list(reader) )[0]
				
				for i in range( len(inArray) ):
					self._toBeProcessedGameID.append( int(inArray[i]) )
			
			print(self._toBeProcessedGameID)
			input()
				
			print("Array Of Games was loaded from file...")
			print("It contains:", len(self._toBeProcessedGameID))
		
			input()
		
		except (FileNotFoundError, IndexError) as fileDoesNotExist:
			#ADD FILE IMPORT
			userData  = urllib.request.Request(CONST.STEAM_GAMES_LIST_JSON, headers=CONST.USER_HEADERS)
			r         = urllib.request.urlopen(userData)
			print("HTTP Code:", r.getcode())
			JSON_FILE = json.loads( r.read() )
			
			print("JSON_FILE:", len(JSON_FILE["applist"]["apps"]))
			for i in range( len(JSON_FILE["applist"]["apps"]) ):
				self._toBeProcessedGameID.append( JSON_FILE["applist"]["apps"][i]["appid"] )

	def saveData(self):
		self.writeToCSVFile()
	
	def getCurrencyTable(self, gameID):
		try:
			#Make a delay for requests to Server
			sleep(2)
			UserData = urllib.request.Request(CONST.STEAMDB_APP_URL + str(gameID), headers=CONST.USER_HEADERS)
			r        = urllib.request.urlopen(UserData)

			soup     = BeautifulSoup(r, 'html.parser')
			soup     = soup.find('table', class_='table-prices')

			#If "Prices" tab doesn't exist => return NONE
			if (not soup):
				return 'None'

			return soup.tbody

		except urllib.error.HTTPError:
			#In case, there is an error(e.g HTTP code 429), wait
			sleep(200)
			#Try again
			return self.getCurrencyTable(gameID)

	def processTheTable(self, table):
		table = table.find_all('tr')
		rows = []
		for row in table:
			row = row.find_all('td')
			
			for i in range( len(row) ):
				#<td>...SomeTEXT...</td> => ...SomeTEXT...
				row[i] = row[i].text
				#from Text remove all chars buy CurrencyName
				if ( i == 0 ):
					row[i] = re.search('\n (.*)\n', row[i]).group(1)
			
			#Does the price exist?
			if (row[1] == 'N/A'):
				row[1] = CONST.NA_CONST
				rows.append(row)
				continue
			
			#Removing local currency column
			if ( row[0] != 'U.S. Dollar'):
				row.pop(1)
			#Solution to situation
			#"$3.59 at -10%"
			else:
				row[1] = ( row[1].split() )[0]

			if (len(row) == 4):
				row.insert(2, "0%")
			
			#Remove local currency row and convert to Float
			row[1] = float( row[1][1:] )
			
			if (row[2] != 'Base Price'):
				#Remove the percent sign and any commas and convert to Float
				row[2] = float( (row[2][:-1]).replace(',', '') )
			
			rows.append(row)	
			
		return rows

	def bubbleSort(self, arr):
		n = len(arr)
		for i in range(n):
			for j in range(n - i - 1):
				#Isn't supporting a comparison between string and float
				if ( abs(arr[j][1]) > abs(arr[j+1][1]) ):
					arr[j], arr[j+1] = arr[j+1], arr[j]
	
	def recordData(self, table):
		for i in range( len(table) ):
			currencyName = table[i][0]
			if (table[i][1] == CONST.NA_CONST):
				self._currencyList[currencyName]["numUnavailable"] += 1
				continue
			
			#Formula:
			#new_AVG_Place = (old_AVG_Place * numAvailable + i + 1) / (numAvailable + 1)
			self._currencyList[currencyName]["avgPlace"] += i + 1
			self._currencyList[currencyName]["spends"] += table[i][1]
			
			if (table[i][2] != "Base Price"):
				self._currencyList[currencyName]["avgModifier"] += table[i][2]		
			
			self._currencyList[currencyName]["numAvailable"] += 1

	def outputDict(self):
		for i in self._currencyList:
			print(self._currencyList[i])
	
	def outputTable(self, table):
		for i in range( len(table) ):
			print(table[i])

	def writeToCSVFile(self):
		#recording the Currency Table
		with open("table.csv", 'w', newline='\n', encoding='utf-8') as oFile:
			fieldnames = ["Name", "Average Place (#)", "# of Available (#)", "Average Modifier (%)", "# of Unavailable (#)", "Total Spends ($)"]
			
			writer = csv.DictWriter(oFile, fieldnames=fieldnames)
			writer.writeheader()
			
			for i in self._currencyList:
				if (self._currencyList[i]["numAvailable"] == 0):
					writer.writerow({
						"Name": 		      self._currencyList[i]["name"],
						"Average Place (#)":      float(0),
						"# of Available (#)":     self._currencyList[i]["numAvailable"],
						"Average Modifier (%)":       float(0),
						"# of Unavailable (#)":   self._currencyList[i]["numUnavailable"],
						"Total Spends ($)":       self._currencyList[i]["spends"]
					})
				else:
					writer.writerow({
						"Name":				self._currencyList[i]["name"],
						"Average Place (#)":		'{:.2f}'.format((self._currencyList[i]["avgPlace"] / self._currencyList[i]["numAvailable"])),
						"# of Available (#)":		self._currencyList[i]["numAvailable"],
						"Average Modifier (%)":		'{:.2f}'.format((self._currencyList[i]["avgModifier"] / self._currencyList[i]["numAvailable"])),
						"# of Unavailable (#)":		 self._currencyList[i]["numUnavailable"],
						"Total Spends ($)":       	 self._currencyList[i]["spends"]
					})

			writer = csv.writer(oFile, delimiter=',')
			writer.writerow('')
			writer.writerow(["Free Games (#)", self._freeGamesNum])
			
		with open("array.txt", 'w') as oFile:
			writer = csv.writer(oFile)
			writer.writerow(self._toBeProcessedGameID)

	def saveArray(self):
		with open("array.txt") as oFile:
			oFile.write(self._arrayOfGameID)

	def main(self):
		print("Titles Available:", len(self._toBeProcessedGameID))
		print()
		
		itemsProcessed = 0
		size = len(self._toBeProcessedGameID)
		while ( len(self._toBeProcessedGameID) > 0 ):
			print("Current App: {0}\t\tProcessed {1}/{2}".format(self._toBeProcessedGameID[-1], itemsProcessed, size), end='\r\r')
			
			singleCurrencyTable = self.getCurrencyTable( self._toBeProcessedGameID[-1] )
			
			#RECORD NULL APP && CONTINUE
			if (singleCurrencyTable == 'None'):
				self._freeGamesNum += 1
				itemsProcessed += 1

				self._toBeProcessedGameID.pop()

				continue
			
			singleCurrencyTable = self.processTheTable(singleCurrencyTable)
			self.bubbleSort(singleCurrencyTable)
			
			self.recordData(singleCurrencyTable)
			
			itemsProcessed += 1
			self._toBeProcessedGameID.pop()

		self.writeToCSVFile()

		return 0	
