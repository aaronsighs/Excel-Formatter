
#dependecies
###############################
import pandas as pd
import openpyxl
import os,re,logging,time
from difflib import SequenceMatcher as seqM
from datetime import datetime,date
###############################


months = {'jan': '1','feb': '2','mar': '3','apr':'4','may':'5','jun':'6'
	 ,'jul':'7','aug':'8','sep':'9','oct':'10','nov':'11','dec':'12'}


class formater:
	def __init__(self, dir="files", **kwargs):
		self.column_names = kwargs.get("column_names",[])
		self.settings = kwargs.get("settings",{})
		self.set_dir(dir)
		self.flags = {}



	# set file directory, if the directory does not exist make a 'files' folder in cwd.
	def set_dir(self,dir="files"):
		if os.path.exists(dir):
					self.dir = dir
		else:
			self.dir = os.getcwd() + '/files'
			if not os.path.exists("files"): os.makedirs("files")
			logging.warning(" directory: '{}' does not exist.\nUsing directory {} instead.".format(dir,self.dir))
		self.fileList = [file for file in os.listdir(self.dir) if ".xls" in file ]




	def raise_flag(self,type,error,value,return_value=0,max_len=5):
		# create a list of error-loading files and their  ( error type,value)
		if type not in  self.flags: self.flags[type] = [(error,value)]
		# if a list already exists append to it
		else:
			# if the list is over the max length 'max_len' remove the first / longest-time item
			if len(self.flags[type]) == max_len: self.flags[type].pop()
			self.flags[type].append((error,value))
		logging.warning("'{}' Error , ref: ({}) -> '{}'".format(type,error,value))
		return return_value


	# takes a list of dataframes || single dataframe and returns a list
	# of dataframes with new column names based on the desired columns names (given or already set)
	# see set_column_names for further information
	def set_columns_names(self, dfs, columns=None ,threshold=0.45):
		df_list = []
		if type(dfs) is not list: dfs = [dfs]
		for df in dfs:
			df = self.set_column_names(df,colums,threshold)
			if type(df) is not int:df_list.append(df)
		if not len(df_list): self.raise_flag("set_columns_names",10,"input dataframes are empty")
		return df_list



	#takes a dataframe as input and matches the column names to the desired column
	# names (given or previously set) using SequenceMatcher ratio that are above
	# the threshold amount: 0 to. 1
	# column format:
	# columns = [(desired_name,closer_name_to_match,...),"desired_name"]
	# the tuple[0] position or single string will always be the new column name
	# but can be matched closer using following names
	# returns a single dataframe
	def set_column_names(self,df = None, columns = None,threshold = 0.45):
		# checks to make sure data is correct
		if columns is None:
			if not len(self.column_names):
				self.raise_flag(" set_columns",1,"no column names given ")
				return 0
			else:
				columns = self.column_names
		if df is None or df.empty:
			self.raise_flag("set_columns",15,"no data in frame")
			return 0

		used_numbers = [] # list of column positions already taken
		used_names   = [] # list of desired named already taken
		cur_names = df.columns # current column names
		new_names = {}    # dict of new names: {old_name : new_name}
		for name in columns:
			if type(name) is not tuple: name = [str(name)]
			highest = (0,"-------------","--------")  # easily replaced highest value
			for value in name:
				for pos,column in enumerate(cur_names.str.lower()):
					rating  = seqM(None,value,column).ratio()
					highest = (rating,column,pos) if rating > highest[0] else highest
			if highest[0] > threshold:
				if highest[2] not in used_numbers and name[0] not in used_names:
					new_names[cur_names[highest[2]]] = name[0]
					used_numbers.append(highest[2])
					used_names.append(name[0])
		df.rename(columns=new_names, inplace=True)
		new_df = pd.DataFrame()



		# dropping all the values that were not in my columns list
		for value in columns: # for value in passed in column list
			if type(value) is not tuple: value = [value] # make sure the value is a list/tuple type
			print(value[0],df.columns)
			if value[0] in df.columns:                   # if value is now in the columns list
				new_df[value[0]] = df[value[0]]			# add the columns to a new list ignoring uncared for columns
		return new_df



	def verifyDf(self,df = None):
		if type(df)!=pd.core.frame.DataFrame or df.empty:
			self.raise_flag("verifyDf",15,"no data in frame")
			return 0
		return 1

	# set columns in list 'column_names' to a single value in list 'values'
	# column_names[0] = values[0] and so forth for all rows


	# setm = set multiple
	# see setColumnValues for more information
	#takes a list of dfs and returns a list of dfs that were set
	def setm_column_values(self,dfs,column_names,values):
		df_list = []
		if type(dfs) is not list: dfs = [dfs]
		for df in dfs:
			df = self.set_column_values(df,column_names,values)
			if self.verifyDf(df): df_list.append(df)
		return df_list




	def set_column_values(self,df,column_names,values):
		if not self.verifyDf(df): return 0
		if len(values)!=len(column_names) and len(values)!=0:
			self.raise_flag("setting_dates",12,"date_names and dates do not have the same length")
			return df
		for i in range(len(values)):
			df[column_names[i]] = values[i]

		return df



	# set the date columns of name 'date_names'
	# specialized version of setColumnValues, specifically for date data in form;
	# dates = [ [m,d,y],...] - > m/d/y for each corresponding column in date_names = ["",...]
	def set_dates(self,df,dates,date_names):

		if len(dates[0])!=3: return self.raise_flag("setting_dates",13,"dates do not have the correct length")
		dates = ["{}/{}/{}".format(date[0],date[1],date[2]) for date in dates]
		return self.set_column_values(df,date_names,dates)










	# returns 0 if input df is not valid, or a df if an input column error or if success
	def remove_expired(self,df = None, column=None, days_past_today=0):
		if not self.verifyDf(df): return 0
		if column is None or column not in df.columns:
			self.raise_flag("remove_expired",16," error in input column: "+column)
			return df # return unmodified df
		today = pd.to_datetime(date.today() + timedelta(days=days_past_today))
		df = df[pd.to_datetime(df[column])>today]
		df = df[df[column].apply(lambda x: not str(x).isdigit())]
		return df

	# inputs -> dataframe: 'df' , name of column : 'column' , value wanted : 'value'
	# removes all rows that do not contain a column : 'column' with value : 'value'
	# if df is invalid return 0 else return df, modified or unmodified
	def remove_all_Except(self,df,column,value):
		if not self.verifyDf(df): return 0
		if column not in df.columns:
			self.raise_flag("removing_all_except",14," input column did not exist")
			return df # return unmodified df
		df.dropna( subset = [column], inplace=True)
		 # keep only the values in which the column : 'column'
		 # has the same matching string of value within it, ignoring case
		df = df[ df[column].str.lower().str.replace(" ","").str.contains(value)]
		return df









	def get_name_info(self, file_name,key_words={"carrier":["msc",'gmt']}):
		number_list = []
		string_list = []
		actual_name = file_name.lower().replace("\\","/").split("/")[-1].split(".")[0] # get file name
		for s in actual_name.split(" "):   # split the file into words and numbers : 'string_list' , 'number_list'
			if s[0:3] in months: s = months[s[0:3]]   # converts a word: jan,feb..  month into a number 1,2..
			if len(re.sub("[^0-9]", "", s)): number_list.append(s)   # if 'contains' a number add to number list
			elif len(s): string_list.append(s)                       # else add to word list



		dates = [[0,0,0], [0,0,0]]
		if len(number_list)>2:


			sel = [(i for i in range(3)),(i for i in range(3)),(i for i in range(3))] # list of 3 generators with range: 0,1,2

			for number in number_list:
				# sel[2] : 'year'
				if number.isdigit() and len(number)==4: indx = 2 # year index for 'sel'
				elif(number.isdigit()): indx = 0 # month index for 'sel'
				else: indx = 1
				dates[next(sel[indx])][indx] = int(re.sub("[^0-9]", "", number))

			# scenarios
			# formats: month day - month day year
			# [m,d,y],[m,d,0]
			# 	if 1st month  is greater than last month then
			# 	year1  = year2 - 1
			# formats: month day year - month day year
			# [m,d,y],[m,d,y]
			# 	---> everything is given : good
			#formats:  day - month day year
			# [ m, d, y] , [0 , d , 0]
			#	if day is less than year, than next month = month + 1
			#  and if month1 is 12 then year1 = year2 - 1 else year1=year2
			# formats day day month year
			# [m,d,y] [0,d,y]

			# day day month year
			today = date.today()

			todays_date = [today.month,today.day,today.year]

			# [0,0,0]
			if not dates[1][0] + dates[1][1] + dates [1][1]:
				dates[1] = dates[0]
				dates[0] = todays_date
			# [0,d,0]
			elif not dates[1][2] and dates[1][0] and dates[1][1]: # year
				 dates[1][2] = dates[0][2]
				 if dates[0][0] > dates[1][0]:
					 dates[0][2] -= 1
			for i in range(3): # going through selectors
				if next(sel[i])!=2:  # if the current selector has 2 pos filled then both data inputs are good else ->
						if not dates[1][i]:  # if the value is still 0. at date index : 'k'  ,  date_value(month,day,year): 'i'
							dates[0][i] = dates[1][i] # replace the value of the 0. position with the opposing date_value
							# example: date[0][1] : 1st date, sel: day  == 0 (not filled in) then date[0][1] = date[1][1]
		else:
			dates = []


		found_keywords = {}
		for key in key_words:
			for s in string_list:
				found_keywords[key] = ""
				if s in key_words[key]:
					found_keywords[key] = s

		return(dates,found_keywords)



























	# look through initalized list of files in directory folder (given,or saved)
	# add each dataframe to a list 'df_list' if the file was correctly loaded
	# and return the list
	def load_files(self, dir=None, max_rows=4000):
		df_list = []
		if dir is not None: self.set_dir(dir)
		for file in self.fileList:
			df = self.load_file(file,max_rows)
			if type(df) is not int: df_list.append(df)
		return df_list




	def load_file(self, file_name,max_rows=4000):

		# check to see if the given file : 'file_name' exists
		# if it's not a full path check to see if the file is in the given dir
		# if it doesn't exist raise an error in the flag list that the file didn't load: error 1 "file not found"
		if not os.path.exists(file_name):
			if os.path.exists(self.dir + "/" + file_name):
				file_name = self.dir + "/" + file_name
			else:
				self.raise_flag("loading", 1, file_name)
				return 0

		# get file type
		# if incorrect type raise an error in the 'loading' flag list that the file is of the "wrong type": error 2
		file_type = file_name[file_name.find("."):]
		if ".xls" not in file_type:
			self.raise_flag("loading", 2, file_name)
			return 0

		remove_list = []  # list of rows to remove
		main_row = -1     # starting row / rows to skip
		sheet_name = 0    # name of sheet, 0  depicts first sheet_name for ".xls" files

		# if the file is of the newer excel type: xlsx
		if file_type == ".xlsx":
			# get the workbook and the sheet name 'sheet_name'
			# check to see what the 1st sheet name is in some files they are hidden names, if hidden ignore them.
			# default to 'Sheet1' : "default excel sheet name"
			sheet_name = "Sheet1"
			workbook = openpyxl.load_workbook(file_name, data_only=False)
			for name in workbook.sheetnames:
				if workbook[name].sheet_state != "hidden":
					sheet_name = name
					break
			sheet = workbook[sheet_name]

			# xlsx can have striked values, look through through one col: 'B'
			# and get a list of all the strike value row-positions ( assuming if one strike value exists remove the whole row )
			# while using 'main_row' to find the main column_names row
			# if the number of rows is over 'max_rows' return 0 and flag 3: 'file to Long'
			if "remove_strikes" in self.settings and self.settings["remove_strikes"]:
				for row_count,cell in enumerate(sheet["B"]):
					if row_count > max_rows :
						self.raise_flag("loading",3,file_name)
						return 0
					elif( main_row==-1 and cell.value != None ):
						main_row = row_count - 1
					if cell.font.strike:
						remove_list.append(row_count-1)

		# read in the excel file with pandas: what we are manipulating data with
		# by default make sure the main_row is not '- 1' if it was never set
		# read rows a to ae,  then remove the row numbers in the remove_list from the dataframe using .drop
		# remove rows if they have more than '3' nan values per row
		if main_row == -1: main_row = 0
		df = pd.read_excel(file_name, skiprows = main_row, usecols= "A:AE", sheet_name = sheet_name)
		while ( 'Unnamed' in df.columns[0] and 'Unnamed' in df.columns[0]):
			new_header = df.iloc[0] # get the first row
			df = df[1:]             # removes the last header
			df.columns = new_header # sets the header to prv first row





		df.columns = df.columns.str.lower()
		df.drop(remove_list, inplace=True)
		df.dropna(thresh=3, inplace=True)
		# return frame
		if df.empty:
			self.raise_flag("loading",15,name)
			return 0
		return df



col_names = [("pol_region","port of loading"),("carrier","carriers"),
    ("t_t_to_pod","transit_time"),("pod__via_port","dest (via port)"),
    ("destination_details","place of delivery"),"effective_date",
    "expiring_date",("20gp","20'gp"),("40gp","40'GP"),
    ("40hq","40'HQ"),"comm_details",("rate_remarks","remarks")]









f = formater(settings={"remove_strikes":1}, column_names = col_names)
df = f.load_file(f.fileList[2])
print(df)
print(df.columns)
df = f.set_column_names(df,columns=col_names)
print(df.columns)
name_info = f.get_name_info(f.fileList[0],key_words={"carrier":["msc","cmk","hapag","maersk"]})
dates = name_info[0]
carrier = name_info[1]["carrier"]
df = f.remove_all_Except(df,column="carrier",value=carrier)

df = f.setm_column_values(df,["carrier"],["dog"])[0]




print(df)
df = f.set_dates(df,dates,["effective_date","expiring_date"])
print(df)




print(f.flags)
