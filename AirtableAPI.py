#!/usr/bin/python
# -*- coding: utf-8 -*- 

import datetime
import time
import requests

import datetime
import time
import requests

import json
import posixpath 
import requests
from collections import OrderedDict

API_URL = 'https://api.airtable.com/v%s/'
API_VERSION = '0'


class IsNotInteger(Exception):
    pass


class IsNotString(Exception):
    pass


def check_integer(n):
    if not n:
        return
    elif not isinstance(n, int):
        raise IsNotInteger('Expected an integer')
    else:
        return True


def check_string(s):
    if not s:
        return
    elif not isinstance(s, str):
        raise IsNotString('Expected a string')
    else:
        return True


def create_payload(data):
    return {'fields': {k: v for k, v in data.items() if v is not None}}


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

class Table(object):
	def __init__(self,
    			 name = None):
		self.name = name

	class Record(object):
		def __init__(self,
	    			 record_id = None,
	    			 #fields = None,
	    			 airtable_record = None):
			self.record_id = record_id
			#self.fields = fields
			self.airtable_record = airtable_record
			if airtable_record:
				self.record_id = airtable_record['id']


		'''def payload(self,
					shopify_attributes):
			data = {}
			for key, field in self.fields.items():
				try:
					field_data = field.putFieldValue(shopify_attributes[key])
				except KeyError:
					#print ("Key Error: ",key, " is not in data")
					continue
				if field_data:
					data.update(field_data)
			return data '''


		class Field(object):
			def __init__(self,
		    			 name = None,
		                 data_type = None,
		                 value = None,
		                 record = None):
				self.name = name
				self.data_type = data_type
				self.value = value
				if record:
					try:
						if self.data_type == "attachments":
							self.value = [x['url'] for x in record["fields"][self.name]]
						elif self.data_type == "array_string":
							self.value = record["fields"][self.name][0]
						elif self.data_type == "integer":
							#print (record["fields"][self.name],">>>>>>>>>>>>>>>>>>>>>>>>>")
							if record["fields"][self.name]=='':
								self.value = None
							else:
								self.value = int(record["fields"][self.name])							
						else:
							self.value = record["fields"][self.name]#.encode('utf-8')
					except (KeyError,IndexError):
						self.value = None

			def getFieldValue(self,
						 record):
				if record:
					try:
						if self.data_type == "attachments":
							self.value = [x['url'] for x in record["fields"][self.name]]
						else:
							self.value = record["fields"][self.name]#.encode('utf-8')
					except (KeyError,IndexError):
						self.value = ""

			'''def putFieldValue(self,
							  value):
				if not value:
					return None
				if self.data_type == "string":
					value = str(value)		
				if self.data_type == "decimal":
					value = float(value)
				if self.data_type == "integer":
					value = int(value)	
				if self.data_type == "boolean":
					if value:
						value = True
					else:
						value = False			
				elif self.data_type == "array_string":
					if isinstance(value, str):
						value = value.replace(", ",",")
						if value:
							value = value.split(",")
						else:
							value = []
				return {self.name : value}'''



	def getAllRecordsData(self,
					all_records):

		return [self.Record(airtable_record=record) for record in all_records["records"]]

	def getRecordData(self,
					  record):
		return self.Record(airtable_record=record)


class AirTable(object):

	def __init__(self, config_file):
		self.airtable_url = API_URL % API_VERSION
		self.base_url = posixpath.join(self.airtable_url, config_file["base_id"])
		self.headers = {'Authorization': 'Bearer %s' % config_file["api_key"]}

	def __request(self, method, url, params=None, payload=None):
		if method in ['POST', 'PUT', 'PATCH']:
			self.headers.update({'Content-type': 'application/json'})
		r = requests.request(method,
		                     posixpath.join(self.base_url, url),
		                     params=params,
		                     data=payload,
		                     headers=self.headers)
		if r.status_code == requests.codes.ok:
			return r.json(object_pairs_hook=OrderedDict)
		else:
			try:
				message = None
				r.raise_for_status()
			except requests.exceptions.HTTPError as e:
				message = e.message
			return {
			    'error': dict(code=r.status_code, message=message)
			}

	def get(
		    self, table_name, record_id=None, limit=0, offset=None,
		    filter_by_formula=None, view=None):
		params = {}
		if check_string(record_id):
			url = posixpath.join(table_name, record_id)
		else:
			url = table_name
			if limit and check_integer(limit):
				params.update({'pageSize': limit})
			if offset and check_string(offset):
				params.update({'offset': offset})
			if filter_by_formula is not None:
				params.update({'filterByFormula': filter_by_formula})
			if view is not None:
				params.update({'view': view})
		return self.__request('GET', url, params)

	def iterate(
	        self, table_name, batch_size=0, filter_by_formula=None, view=None):
		"""Iterate over all records of a table.

		Args:
		    table_name: the name of the table to list.
		    batch_size: the number of records to fetch per request. The default
		        (0) is using the default of the API which is (as of 2016-09)
		        100. Note that the API does not allow more than that (but
		        allow for less).
		    filter_by_formula: a formula used to filter records. The formula
		        will be evaluated for each record, and if the result is not 0,
		        false, "", NaN, [], or #Error! the record will be included in
		        the response. If combined with view, only records in that view
		        which satisfy the formula will be returned.
		    view: the name or ID of a view in the table. If set, only the
		        records in that view will be returned. The records will be
		        sorted according to the order of the view.
		Yields:
		    A dict for each record containing at least three fields: "id",
		    "createdTime" and "fields".
		"""
		offset = None
		while True:
			response = self.get(
			    table_name, limit=batch_size, offset=offset,
			    filter_by_formula=filter_by_formula, view=view)
			for record in response.pop('records'):
				yield record
			if 'offset' in response:
				offset = response['offset']
			else:
				break

	def create(self, table_name, data):
		if check_string(table_name):
			payload = create_payload(data)
			return self.__request('POST', table_name,
			                      payload=json.dumps(payload))

	def update(self, table_name, record_id, data):
		if check_string(table_name) and check_string(record_id):
			url = posixpath.join(table_name, record_id)
			payload = create_payload(data)
			return self.__request('PATCH', url,
			                      payload=json.dumps(payload))

	def update_all(self, table_name, record_id, data):
		if check_string(table_name) and check_string(record_id):
			url = posixpath.join(table_name, record_id)
			payload = create_payload(data)
			return self.__request('PUT', url,
			                      payload=json.dumps(payload))

	def delete(self, table_name, record_id):
		if check_string(table_name) and check_string(record_id):
			url = posixpath.join(table_name, record_id)
			return self.__request('DELETE', url)


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

	def updateTableRecord(self, table, record_id, data):
		response = requestErrorCheck(self.update, table, record_id, data)
		if 'error' in response:			
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.updateTableRecord(table, record_id, data)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None
		else:
			return response

	def createTableRecord(self, table, data):
		response = requestErrorCheck(self.create, table, data)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.createTableRecord(table, data)
			elif response["error"]['code'] == 404:
				print ("Airtable Client Error")
				return None
			else:
				return None			
		else:
			return response
		
	def deleteTableRecord(self, table, record_id):
		response = requestErrorCheck(self.delete, table, record_id)
		if 'error' in response:
			print (response)
			if 500 <= response["error"]['code'] <= 504:
				print ("Airtable connection error")
				print ("Waiting 5 minutes")
				time.sleep(300)
				return self.deleteTableRecord(table, record_id)
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
			return record["fields"][field]#.encode('utf-8')
		except KeyError:
			return ""
		except AttributeError:
			return record["fields"][field]

	
	def getAllXDataFromXTable(self,
									 x_table,
									 getXData):

		all_records = self.getAllTableRecords(x_table)
		x_list = getXData(all_records)
		if 'offset' in all_records:
			offset = all_records['offset']
		else:
			offset = None
		while offset:
			all_records = self.getAllTableRecordsFromOffset(x_table,offset)
			temp_x_list = getXData(all_records)
			x_list.extend(temp_x_list)
		
			if 'offset' in all_records:
				offset = all_records['offset']
			else:
				break

		return x_list

	def getAllXDataFromXTableFromRecordID(self,
									 x_table,
									 record_id,
									 getXData):

		record = self.getSingleTableRecord(x_table,record_id)
		x_dict = getXData(record)

		return x_dict



	def getAllXDataFromXTableView(self,
									 x_table,
									 x_view,
									 getXData):

		all_records = self.getAllTableViewRecords(x_table, x_view)
		x_list = getXData(all_records)
		if 'offset' in all_records:
			offset = all_records['offset']
		else:
			offset = None
		while offset:
			all_records = self.getAllTableViewRecordsFromOffset(x_table,x_view,offset)
			temp_x_list = getXData(all_records)
			x_list.extend(temp_x_list)
		
			if 'offset' in all_records:
				offset = all_records['offset']
			else:
				break

		return x_list


	def getAllAirtableRecordsFromTable(self,
										table,
										dict_key=None):

		try:
			all_records = self.getAllXDataFromXTable(table.table_id,
							  					   table.getAllRecordsData)
		except AttributeError:
			all_records = self.getAllXDataFromXTable(table.name,
							  					   table.getAllRecordsData)		

		if dict_key:
			ids_dict ={x.fields[dict_key].value:x.record_id for x in all_records}
			return all_records, ids_dict
		else:
			return all_records


	def getAllAirtableRecordsFromTableView(self,
										table,
										view,
										dict_key=None):

		all_records = self.getAllXDataFromXTableView(table.table_id,
													view,
							  					   table.getAllRecordsData)

		if dict_key:
			ids_dict ={x.fields[dict_key].value:x.record_id for x in all_records}
			return all_records, ids_dict
		else:
			return all_records


	def getTableRecordFromTableRecordID(self,
										table,
										table_record_id):

		table_data = self.getAllXDataFromXTableFromRecordID(table.table_id,
															  table_record_id,
															  table.getRecordData)

		return table_data



'''*******************************************************************************************************
TAVS BASE INHERITED CLASS

**********************************************************************************************************'''

class TavsAirTable(AirTable):

	def __init__(self,
			     config):

		AirTable.__init__(self,config)



	class BattingTable(Table):

		name = "BATTING"
		table_id = "tblvujQ914fqhvrEW"
		tavs_innings_view = "viwgwYkOLRMiPvJ1J"

		def __init__(self):
			Table.__init__(self,self.name)
		
		class Record(Table.Record):

			def __init__(self,airtable_record=None):
				
				Table.Record.__init__(self,airtable_record=airtable_record)

				self.fields = {}
				self.fields['name'] = self.Field(name="Name", data_type="string", record=airtable_record) 
				self.fields['match'] = self.Field(name="Match (String)", data_type="string", record=airtable_record)
				self.fields['date'] = self.Field(name="Date", data_type="array_string", record=airtable_record) 
				self.fields['runs'] = self.Field(name="Runs", data_type="integer", record=airtable_record) 
				self.fields['fours'] = self.Field(name="Fours", data_type="integer", record=airtable_record) 
				self.fields['sixes'] = self.Field(name="Sixes", data_type="integer", record=airtable_record) 
				self.fields['batting_order'] = self.Field(name="Batting Order", data_type="integer", record=airtable_record) 
				self.fields['dismissal'] = self.Field(name="Dismissal", data_type="string", record=airtable_record) 
				self.fields['out_bool'] = self.Field(name="Out", data_type="boolean", record=airtable_record) 
				self.fields['innings_bool'] = self.Field(name="Innings", data_type="boolean", record=airtable_record) 
				self.fields['match_type'] = self.Field(name="Match Type", data_type="array_string", record=airtable_record) 
				self.fields['season'] = self.Field(name="Season", data_type="array_string", record=airtable_record)
				self.fields['balls_faced'] = self.Field(name="Balls Faced", data_type="integer", record=airtable_record)
				#self.fields['photo_url'] = self.Field(name="Photo", data_type="attachments", record=airtable_record)
				self.fields['catcher'] = self.Field(name="Catcher Name", data_type="string", record=airtable_record)
				self.fields['team'] = self.Field(name="Team Name", data_type="string", record=airtable_record) 
				self.fields['fow_runs'] = self.Field(name="Fall of Wicket (Runs)", data_type="integer", record=airtable_record)  
				self.fields['fow_overs'] = self.Field(name="Fall of Wicket (Overs)", data_type="decimal", record=airtable_record) 

	batting_table = BattingTable()


	class BowlingTable(Table):

		name = "BOWLING"
		table_id = "tblLrcba4YskltHU1"
		tavs_innings_view = "viwO4s1Ne5LcS9pG5"

		def __init__(self):
			Table.__init__(self,self.name)
		
		class Record(Table.Record):

			def __init__(self,airtable_record=None):
				
				Table.Record.__init__(self,airtable_record=airtable_record)

				self.fields = {}
				self.fields['name'] = self.Field(name="Name", data_type="string", record=airtable_record) 
				self.fields['match'] = self.Field(name="Match (String)", data_type="string", record=airtable_record)
				self.fields['date'] = self.Field(name="Date", data_type="array_string", record=airtable_record) 
				self.fields['runs'] = self.Field(name="Runs", data_type="integer", record=airtable_record) 
				self.fields['fours'] = self.Field(name="Fours", data_type="integer", record=airtable_record) 
				self.fields['sixes'] = self.Field(name="Sixes", data_type="integer", record=airtable_record)
				self.fields['overs'] = self.Field(name="Overs", data_type="decimal", record=airtable_record) 
				self.fields['wickets'] = self.Field(name="Wickets", data_type="integer", record=airtable_record)  
				self.fields['maidens'] = self.Field(name="Maidens", data_type="integer", record=airtable_record) 
				self.fields['wides'] = self.Field(name="Wides", data_type="integer", record=airtable_record) 
				self.fields['no_balls'] = self.Field(name="No Balls", data_type="integer", record=airtable_record) 

				self.fields['bowling_order'] = self.Field(name="Bowling Order", data_type="integer", record=airtable_record) 
				self.fields['dismissal_types'] = self.Field(name="Dismissal Types", data_type="list", record=airtable_record) 
				self.fields['match_type'] = self.Field(name="Match Type", data_type="array_string", record=airtable_record)
				self.fields['season'] = self.Field(name="Season", data_type="array_string", record=airtable_record) 
				#self.fields['photo_url'] = self.Field(name="Photo", data_type="attachments", record=airtable_record)
				self.fields['team'] = self.Field(name="Team Name", data_type="string", record=airtable_record) 



	bowling_table = BowlingTable()


	class MatchesTable(Table):

		name = "MATCHES"
		table_id = "tbl5vXBFOxLvwA9X5"
		tavs_matches_view = "viwETmTbL8do9Ur1c"

		def __init__(self):
			Table.__init__(self,self.name)
		
		class Record(Table.Record):

			def __init__(self,airtable_record=None):
				
				Table.Record.__init__(self,airtable_record=airtable_record)

				self.fields = {}
				self.fields['opposition'] = self.Field(name="Opposition", data_type="string", record=airtable_record) 
				self.fields['ground'] = self.Field(name="Ground (String)", data_type="string", record=airtable_record)
				self.fields['date'] = self.Field(name="Date", data_type="date", record=airtable_record) 
				self.fields['result'] = self.Field(name="Result", data_type="string", record=airtable_record) 
				self.fields['bat_first'] = self.Field(name="Bat First", data_type="string", record=airtable_record) 
				self.fields['tav_runs'] = self.Field(name="Tav Runs", data_type="integer", record=airtable_record)  
				self.fields['tav_wickets_down'] = self.Field(name="Tav Wickets Down", data_type="integer", record=airtable_record) 
				self.fields['oppo_runs'] = self.Field(name="Oppo Runs", data_type="integer", record=airtable_record)  
				self.fields['oppo_wickets_down'] = self.Field(name="Oppo Wickets Down", data_type="integer", record=airtable_record) 
				self.fields['match_type'] = self.Field(name="Match Type", data_type="string", record=airtable_record)
				self.fields['season'] = self.Field(name="Season", data_type="string", record=airtable_record) 
				self.fields['captains_tankard'] = self.Field(name="Captains Tankard (String)", data_type="string", record=airtable_record)  
				self.fields['match_report'] = self.Field(name="Match Report", data_type="string", record=airtable_record)


	matches_table = MatchesTable()
