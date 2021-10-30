#!/usr/bin/python
# -*- coding: utf-8 -*- 

from airtable.airtable import Airtable
import datetime
import time
import requests
import pandas as pd


#Not sure if this is a reasonable way of dealing with these timeout errors.
#Revisit if/when requests.urllib3 problem is sorted
def requestErrorCheck(method, *args):
	try:
		return method(*args)
	except requests.exceptions.ConnectionError as e:
		print (e)
		print ("Connection Error: Waiting 3 minutes from", datetime.datetime.now())
		time.sleep(180)
		return requestErrorCheck(method,*args)
	except requests.exceptions.ChunkedEncodingError as e:
		print (e)
		print ("Chunked Encoding Error: Waiting 3 minutes from", datetime.datetime.now())
		time.sleep(180)
		return requestErrorCheck(method,*args)

class AirTable(Airtable):

	def __init__(self,
			 	config_file):
		Airtable.__init__(self,config_file["base_id"], config_file["api_key"])

	def getAllTableRecords(self,table):

		response = requestErrorCheck(self.get,table)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.getAllTableRecords(table)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None				
		else:
			return response

	
	def getAllTableRecordsFromOffset(self,table,offset_id):

		response = requestErrorCheck(self.getAllTableRecordsFromOffset_,table,offset_id)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.getAllTableRecordsFromOffset(table,offset_id)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None				
		else:
			return response

	#I THINK I CAN DEAL WITH THIS USING KWARGS
	def getAllTableRecordsFromOffset_(self,table,offset_id):

		return self.get(table, offset=offset_id)

	def getAllTableViewRecords(self,table,view):

		response = requestErrorCheck(self.getAllTableViewRecords_,table,view)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.getAllTableViewRecords(table,view)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None				
		else:
			return response

	def getAllTableViewRecords_(self,table,view):

		return self.get(table,view=view)		
	
	def getAllTableViewRecordsFromOffset(self,table,view,offset_id):

		response = requestErrorCheck(self.getAllTableViewRecordsFromOffset_,table,view,offset_id)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.getAllTableViewRecordsFromOffset(table,view,offset_id)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None				
		else:
			return response

	#I THINK I CAN DEAL WITH THIS USING KWARGS
	def getAllTableViewRecordsFromOffset_(self,table,view,offset_id):

		return self.get(table, view=view, offset=offset_id)

	def getSingleTableRecord(self,table, record_id):

		response = requestErrorCheck(self.getSingleTableRecord_,table,record_id)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.getSingleTableRecord(table,record_id)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None				
		else:
			return response

	def getSingleTableRecord_(self,table,record_id):

		return self.get(table,record_id=record_id)

	def updateTableField(self, table, record_id, data):
		response = requestErrorCheck(self.update, table, record_id, data)
		if 'error' in response:			
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.updateTableField(table, record_id, data)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None
		else:
			return response

	def createTableField(self, table, data):
		response = requestErrorCheck(self.create, table, data)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.createTableField(table, data)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None			
		else:
			return response
		
	def deleteTableField(self, table, record_id):
		response = requestErrorCheck(self.delete, table, record_id)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.deleteTableField(table, record_id)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None			
		else:
			return response

	def getField(self,
				 record,
				 field):
		try:
			return record["fields"][field]
		except KeyError:
			return ""
		except AttributeError:
			return record["fields"][field]

	def getBattingData(self,all_records):

		data_list = []
		for record in all_records["records"]:
			name = self.getField(record,'Name')
			match = self.getField(record,'Match (String)')
			ta = datetime.datetime.strptime(self.getField(record,'Date')[0],"%Y-%m-%d")
			date = datetime.datetime(ta.year,ta.month,ta.day,ta.hour,ta.minute)
			try:
				runs = int(self.getField(record,'Runs'))
			except ValueError:
				runs = None
			try:
				fours = int(self.getField(record,'Fours'))
			except ValueError:
				fours = None
			try:
				sixes = int(self.getField(record,'Sixes'))
			except ValueError:
				sixes = None
			batting_order = int(self.getField(record,'Batting Order'))
			dismissal = self.getField(record,'Dismissal')
			out_bool = int(self.getField(record,'Out'))
			innings_bool = int(self.getField(record,'Innings'))
			match_type = self.getField(record,'Match Type')[0]
			season = self.getField(record,'Season')[0]
			try:
				balls_faced = int(self.getField(record,'Balls Faced'))
			except ValueError:
				balls_faced = None
			try:
				photo_url = self.getField(record,'Photo')[0]["url"]
			except IndexError:
				photo_url = None	

			catcher = self.getField(record,'Catcher Name')
			team = self.getField(record,'Team Name')

			try:
				fow_runs = int(self.getField(record,'Fall of Wicket (Runs)'))
			except ValueError:
				fow_runs = None

			try:
				fow_overs = float(self.getField(record,'Fall of Wicket (Overs)'))
			except ValueError:
				fow_overs = None

			data_list.append([name,
							  match,
							  date,
							  runs,
							  fours,
							  sixes,
							  batting_order,
							  dismissal,
							  out_bool,
							  innings_bool,
							  match_type,
							  season,
							  photo_url,
							  balls_faced,
							  catcher,
							  team,
							  fow_runs,
							  fow_overs])

		return data_list 


	def getAllBattingDataFromBattingTable(self):

		all_records = self.getAllTableViewRecords("BATTING","viwgwYkOLRMiPvJ1J")
		data_list = self.getBattingData(all_records)
		if 'offset' in all_records:
			offset = all_records['offset']
		else:
			offset = None
		while offset:
			all_records = self.getAllTableViewRecordsFromOffset("BATTING","viwgwYkOLRMiPvJ1J",offset)
			temp_data_list = self.getBattingData(all_records)
			data_list.extend(temp_data_list)
		
			if 'offset' in all_records:
				offset = all_records['offset']
			else:
				break

		return pd.DataFrame(data_list, columns=['name',
												  'match',
												  'date',
												  'runs',
												  'fours',
												  'sixes',
												  'batting_order',
												  'dismissal',
												  'out_bool',
												  'innings_bool',
												  'match_type',
												  'season',
												  'photo_url',
												  'balls_faced',
												  'catcher',
												  'team',
												  'fow_runs',
												  'fow_overs'])


	def getBowlingData(self,all_records):

		data_list = []
		for record in all_records["records"]:
			name = self.getField(record,'Name')
			match = self.getField(record,'Match (String)')
			ta = datetime.datetime.strptime(self.getField(record,'Date')[0],"%Y-%m-%d")
			date = datetime.datetime(ta.year,ta.month,ta.day,ta.hour,ta.minute)
			try:
				overs = int(self.getField(record,'Overs'))
			except ValueError:
				overs = None
			try:
				wickets = int(self.getField(record,'Wickets'))
			except ValueError:
				wickets = None
			try:
				maidens = int(self.getField(record,'Maidens'))
			except ValueError:
				maidens = None
			try:
				runs = int(self.getField(record,'Runs'))
			except ValueError:
				runs = None
			try:
				wides = int(self.getField(record,'Wides'))
			except ValueError:
				wides = None
			try:
				no_balls = int(self.getField(record,'No Balls'))
			except ValueError:
				no_balls = None
			try:
				fours = int(self.getField(record,'Fours'))
			except ValueError:
				fours = None
			try:
				sixes = int(self.getField(record,'Sixes'))
			except ValueError:
				sixes = None
			bowling_order = int(self.getField(record,'Bowling Order'))
			dismissal_types = self.getField(record,'Dismissal Types')
			#print dismissal_types
			match_type = self.getField(record,'Match Type')[0]
			season = self.getField(record,'Season')[0]
			try:
				photo_url = self.getField(record,'Photo')[0]["url"]
			except IndexError:
				photo_url = None
			team = self.getField(record,'Team Name')

			data_list.append([name,
							  match,
							  date,
							  overs,
							  wickets,							  
							  runs,
							  maidens,
							  wides,
							  no_balls,
							  fours,
							  sixes,
							  bowling_order,
							  dismissal_types,
							  match_type,
							  season,
							  photo_url,
							  team])

		return data_list 


	def getAllBowlingDataFromBowlingTable(self):

		all_records = self.getAllTableViewRecords("BOWLING","viwO4s1Ne5LcS9pG5")
		data_list = self.getBowlingData(all_records)
		if 'offset' in all_records:
			offset = all_records['offset']
		else:
			offset = None
		while offset:
			all_records = self.getAllTableViewRecordsFromOffset("BOWLING","viwO4s1Ne5LcS9pG5",offset)
			temp_data_list = self.getBowlingData(all_records)
			data_list.extend(temp_data_list)
		
			if 'offset' in all_records:
				offset = all_records['offset']
			else:
				break

		return pd.DataFrame(data_list, columns=['name',
												  'match',
												  'date',
												  'overs',
												  'wickets',
												  'runs',
												  'maidens',
												  'wides',
												  'no_balls',
												  'fours',
												  'sixes',
												  'bowling_order',
							  					  'dismissal_types',
												  'match_type',
												  'season',
												  'photo_url',
												  'team'])




	def getMatchesData(self,all_records):

		data_list = []
		for record in all_records["records"]:
			opposition = self.getField(record,'Opposition')
			ta = datetime.datetime.strptime(self.getField(record,'Date'),"%Y-%m-%d")
			date = datetime.datetime(ta.year,ta.month,ta.day,ta.hour,ta.minute)
			ground = self.getField(record,'Ground (String)')
			result = self.getField(record,'Result')
			bat_first = self.getField(record,'Bat First')
			try:
				tav_runs = int(self.getField(record,'Tav Runs'))
			except ValueError:
				continue
			try:
				tav_wickets_down = int(self.getField(record,'Tav Wickets Down'))
			except ValueError:
				tav_wickets_down = None
			try:
				oppo_runs = int(self.getField(record,'Oppo Runs'))
			except ValueError:
				oppo_runs = None
			try:
				oppo_wickets_down = int(self.getField(record,'Oppo Wickets Down'))
			except ValueError:
				oppo_wickets_down = None
			match_type = self.getField(record,'Match Type')
			season = self.getField(record,'Season')
			captains_tankard = self.getField(record,'Captains Tankard (String)')
			match_report = self.getField(record,'Match Report')#		
			

			data_list.append([opposition,
							  date,
							  ground,
							  result,
							  bat_first,
							  tav_runs,
							  tav_wickets_down,
							  oppo_runs,
							  oppo_wickets_down,
							  match_type,
							  season,
							  captains_tankard,
							  match_report])

		return data_list 

	def getAllMatchDataFromMatchesTable(self):

		all_records = self.getAllTableViewRecords("MATCHES","viwETmTbL8do9Ur1c")
		data_list = self.getMatchesData(all_records)
		if 'offset' in all_records:
			offset = all_records['offset']
		else:
			offset = None
		while offset:
			all_records = self.getAllTableViewRecordsFromOffset("MATCHES","viwETmTbL8do9Ur1c",offset)
			temp_data_list = self.getMatchesData(all_records)
			data_list.extend(temp_data_list)
		
			if 'offset' in all_records:
				offset = all_records['offset']
			else:
				break

		return pd.DataFrame(data_list, columns=['opposition',
												  'date',
												  'ground',
												  'result',
												  'bat_first',
												  'tav_runs',
												  'tav_wickets_down',
												  'oppo_runs',
												  'oppo_wickets_down',
												  'match_type',
												  'season',
												  'captains_tankard',
												  'match_report'])


