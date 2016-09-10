import pyodbc;
import pandas as pd;
from TestLog_Generator import *;
import sys;




global_db_conn = 0;                     # here I declare a global pyodbc db connection object 
										# in this way, we only need to create the connection once.
										# when we convert the project into OOP pattern
										# this can be a class variable or private member 
										# COOL ha? Okay im joking. LUL

#######################################################################################
## DRIVER={ODBC Driver 11 for SQL Server};SERVER=dydevsql03;DATABASE=Guest_Writer;UID=TechOps_Guest;PWD=GuestSimSim
## db_conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER=dydevsql03;DATABASE=Guest_Writer;UID=TechOps_Guest;PWD=GuestSimSim');
def create_db_connection(Driver_name, Server, Database, Uid, Pwd):
	connection_string = 'DRIVER={';
	connection_string = connection_string + Driver_name;
	connection_string = connection_string + '};SERVER=';
	connection_string = connection_string + Server;
	connection_string = connection_string + ';DATABASE=';
	connection_string = connection_string + Database;
	connection_string = connection_string + ';UID=';
	connection_string = connection_string + Uid;
	connection_string = connection_string + ';PWD=';
	connection_string = connection_string + Pwd;
	print '';
	print 'DB Connection String:      ', connection_string;
	db_conn = pyodbc.connect(connection_string);
	global global_db_conn;
	global_db_conn = db_conn;
	return db_conn;
#######################################################################################


#######################################################################################
#### I prefer using pure sql query to access the database
#### This means we keep all data operations on the database side 
#### (another word: SQL Server side)
#### Because SQL Sever is much better in processing data compared to pandas dataframe
#######################################################################################
def execute_pure_query_to_pddf(query_sql):   
	try:
		result_df = pd.read_sql(query_sql, global_db_conn);
		return result_df;
	except:
		e = sys.exc_info();
		print '';
		print e;
		print ' SQL:  ', query_sql;
#######################################################################################

#######################################################################################
#### if the sql statement wont return any result set, then we use this method
#######################################################################################
def execute_pure_query(query_sql):
	try:
		cursor = global_db_conn.cursor();
		cursor.execute(query_sql);
		global_db_conn.commit();
	except:
		e = sys.exc_info();
		print '';
		print e;
		print ' SQL: ', query_sql;



#######################################################################################


#######################################################################################
def add_file_Doc_PDF(file_name):
	# print file_name;
	agency_name = file_type = file_name.split('_')[0];
	# print file_type;
	Doc_type_query_sqlstr = 'SELECT * FROM xtr.Doc_Type WHERE Doc_Type_Name=\'' + file_type + '\'';

	doc_type_query_result_df = execute_pure_query_to_pddf(Doc_type_query_sqlstr);
	



	Doc_Type_ID = 0;
	if len(doc_type_query_result_df) == 0:
		print 'No file type found on xtr.Doc_Type!';
		return None;
	else:
		Doc_Type_ID = doc_type_query_result_df.iloc[0]['Doc_Type_ID'];
		# print type(Doc_Type_ID);
		# print str(Doc_Type_ID);

	
	Doc_PDF_add_sqlstr = 'IF NOT EXISTS (SELECT * FROM xtr.Doc_PDF WHERE PDF_File_Name = \'' + file_name + '\')';	
	Doc_PDF_add_sqlstr = Doc_PDF_add_sqlstr + 'INSERT INTO xtr.Doc_PDF (Import_Date_Time, Agency_Name, PDF_File_Name,Extracted_File_Name,Doc_Type_ID, Doc_Version) VALUES ( GETDATE(), \'';
	Doc_PDF_add_sqlstr = Doc_PDF_add_sqlstr + agency_name +'\',\'';
	Doc_PDF_add_sqlstr = Doc_PDF_add_sqlstr + file_name +'\',\'';
	extracted_file_name = file_name[:-4] + '.csv';
	Doc_PDF_add_sqlstr = Doc_PDF_add_sqlstr + extracted_file_name +'\',';
	Doc_PDF_add_sqlstr = Doc_PDF_add_sqlstr + str(Doc_Type_ID) +',';
	Doc_PDF_add_sqlstr = Doc_PDF_add_sqlstr + '\'V2016\'' +');';        #######################################################
																		#### Be careful here, right now the version id is hard
																		#### coded. Later on, we might made this a variable
																		#### so user can define new version for pdf file if 
																		#### the format changes.																	   
																	    #######################################################

	# print Doc_PDF_add_sqlstr;
	execute_pure_query(Doc_PDF_add_sqlstr);
	new_Doc_ID_query_sqlstr = 'SELECT [Doc_ID] FROM [xtr].[Doc_PDF] WHERE [PDF_File_Name] = \'' + file_name + '\';';
	return execute_pure_query_to_pddf(new_Doc_ID_query_sqlstr).iloc[0]['Doc_ID'];

#######################################################################################

#######################################################################################
def add_deal_Doc_Deal(file_name):
	deal_name_dict = {'GinnieMae':'GNR', 'Fannie Mae':'FNR', 'Freddie Mac':'FHR'};    #### will be extended later on
	agency_name = file_name[0:9];
	deal_name = deal_name_dict[agency_name];
	month_str = file_name[-9:-7];
	deal_month = int(month_str);
	doc_id_query_sqlstr = 'SELECT [Doc_ID] FROM [xtr].[Doc_PDF] WHERE [PDF_File_Name] = \'' + file_name + '\';';
	temp_doc_entry = execute_pure_query_to_pddf(doc_id_query_sqlstr);
	Doc_ID = temp_doc_entry.iloc[0]['Doc_ID'];

	Doc_ID = int(Doc_ID);
	Doc_Deal_add_sqlstr = 'IF NOT EXISTS (SELECT * FROM [xtr].[Doc_Deal] WHERE [Doc_ID] = ' + str(Doc_ID) + ')';	
	Doc_Deal_add_sqlstr = Doc_Deal_add_sqlstr + 'INSERT INTO [xtr].[Doc_Deal] (Doc_ID, Deal_Name, Deal_Month) VALUES (';
	Doc_Deal_add_sqlstr = Doc_Deal_add_sqlstr + str(Doc_ID) +',\'';
	Doc_Deal_add_sqlstr = Doc_Deal_add_sqlstr + deal_name +'\',';
	Doc_Deal_add_sqlstr = Doc_Deal_add_sqlstr + str(deal_month) +');';        #######################################################
	execute_pure_query(Doc_Deal_add_sqlstr);

#######################################################################################


#######################################################################################
def add_Tranche_Doc_Tranche(file_name, tranche_list, cusip_list):
	doc_id_query_sqlstr = 'SELECT [Doc_ID] FROM [xtr].[Doc_PDF] WHERE [PDF_File_Name] = \'' + file_name + '\';';
	temp_doc_entry = execute_pure_query_to_pddf(doc_id_query_sqlstr);
	Doc_ID = temp_doc_entry.iloc[0]['Doc_ID'];
	Doc_ID = int(Doc_ID);

	deal_id_query_sqlstr = 'SELECT [Deal_ID] FROM [xtr].[Doc_Deal] WHERE [Doc_ID] ='  + str(Doc_ID) + ';';

	temp_deal_entry = execute_pure_query_to_pddf(deal_id_query_sqlstr);
	Deal_ID = temp_deal_entry.iloc[0]['Deal_ID'];
	Deal_ID = int(Deal_ID);

	Doc_Tranche_add_sqlstr = 'IF NOT EXISTS (SELECT * FROM [xtr].[Doc_Tranche] WHERE [Deal_ID] = ' + str(Deal_ID) + ')';
	Doc_Tranche_add_sqlstr = Doc_Tranche_add_sqlstr + 'INSERT INTO [xtr].[Doc_Tranche] (Deal_ID, Tranche_Name, cusip) VALUES ';
	if len(tranche_list) == len(cusip_list):
		for i in range(0, len(tranche_list)):
			Doc_Tranche_add_sqlstr = Doc_Tranche_add_sqlstr + '(' + str(Deal_ID) + ',\'' + str(tranche_list[i][0]) + '\',\'' + str(cusip_list[i][0]) + '\'), ';

		Doc_Tranche_add_sqlstr = Doc_Tranche_add_sqlstr[:-2] + ';';

		execute_pure_query(Doc_Tranche_add_sqlstr);

		return_Tranche_ID_sqlstr = 'SELECT [Tranche_ID] FROM [xtr].[Doc_Tranche] WHERE [Deal_ID] = ' + str(Deal_ID) + ' ORDER BY [Tranche_ID] ASC;';

		deal_tranche_ID_list = execute_pure_query_to_pddf(return_Tranche_ID_sqlstr);
		return deal_tranche_ID_list['Tranche_ID'].tolist();

	else:
		print 'The number of tranche and the number of cusip don\'t match. Please review the pdf extraction process.';
		return;
#######################################################################################


#######################################################################################
def add_Doc_Field_Name(tranche_id_list, calcrt_id_field_name_list):
	field_name_id_list = [];
	for calcrt_id_field_name_item in calcrt_id_field_name_list:
		# print type(calcrt_id_item);
		calcrt_id_item = str(calcrt_id_field_name_item[0]).replace(' ','');
		field_name_item = str(calcrt_id_field_name_item[1]);
		for tranche_id_item in tranche_id_list: 
			Doc_Field_Name_add_sqlstr = 'IF NOT EXISTS (SELECT * FROM [xtr].[Doc_Field_Name] WHERE ([Tranche_ID] = ' + str(tranche_id_item) + ' AND [Calcrt_ID] = \'' + str(calcrt_id_item) + '\'))';
			Doc_Field_Name_add_sqlstr = Doc_Field_Name_add_sqlstr + 'INSERT INTO [xtr].[Doc_Field_Name] ([Tranche_ID], [Calcrt_ID], [Field_Name]) VALUES (' + str(tranche_id_item) + ', \''  + str(calcrt_id_item) + '\', \'' + field_name_item +'\');';
			# print Doc_Field_Name_add_sqlstr;

			execute_pure_query(Doc_Field_Name_add_sqlstr);
			Field_Name_ID_query_sqlstr = 'SELECT [Field_Name_ID] FROM [xtr].[Doc_Field_Name] WHERE ([Tranche_ID] = ' + str(tranche_id_item) + ' AND [Calcrt_ID] = \'' + str(calcrt_id_item) + '\') ORDER BY [Field_Name_ID] ASC;';
			# print Field_Name_ID_query_sqlstr;

			field_name_id_list_df = execute_pure_query_to_pddf(Field_Name_ID_query_sqlstr);
			field_name_id_list.append([field_name_id_list_df.iloc[0]['Field_Name_ID']]);
	
	return field_name_id_list;
#######################################################################################

#######################################################################################
####	method add_Doc_Field_Value()											   ####
####    this method is used for update/insert new data objects into the            ####
####    db table Doc_Field_Value                                                   ####
####    this method is a complicated one                                           ####
#######################################################################################

def add_Doc_Field_Value(field_name_id_list, combined_all_field_value):
	####################################
	##   Step 1                       ##
	##   query Doc_Field_Name         ##
	##   by filed_name_id_list        ##
	##   get all the pairs of         ##
	##   tranche id and calcrt id     ##
	####################################   
	query_sqlstr_field_name = 'SELECT * FROM [xtr].[Doc_Field_Name] WHERE [Field_Name_ID] IN (';
	for item in field_name_id_list:
		# print item;
		query_sqlstr_field_name = query_sqlstr_field_name + str(item[0]) + ',';

	query_sqlstr_field_name = query_sqlstr_field_name[:-1] + ') ORDER BY [Field_Name_ID] ASC;'
	
	# print query_sqlstr_field_name;	

	field_name_list = execute_pure_query_to_pddf(query_sqlstr_field_name);
	print len(field_name_list);
	
	value_pointer = 0;
	field_index = 0;
	field_name_list['Field_Value'] = '';
	for i in range(0, len(field_name_list)):
		for j in range(0, len(combined_all_field_value)):
			if (field_name_list.iloc[i]['Field_Name'] == combined_all_field_value[j][0]) and (len(combined_all_field_value[j][1]) > 1):
				field_index = j;
				field_name_list.set_value(i,'Field_Value', combined_all_field_value[j][1][value_pointer][0]);
				value_pointer = value_pointer + 1;		
		
			if (field_name_list.iloc[i]['Field_Name'] == combined_all_field_value[j][0]) and (len(combined_all_field_value[j][1]) == 1):
				# print len(combined_all_field_value[j][1]);
				# print 'We reach here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!';
				field_name_list.set_value(i,'Field_Value', combined_all_field_value[j][1][0][0]);


		if value_pointer == len(combined_all_field_value[field_index][1]):
			value_pointer = 0;
			field_index = 0;


			
	     
	print 'Strong signal here!!!!!!!!!!!!!!!!!!!!!!!!'
	for i in range(0, len(field_name_list)):
		# print field_name_list.iloc[i]['Field_Name_ID'],field_name_list.iloc[i]['Tranche_ID'], field_name_list.iloc[i]['Calcrt_ID'].strip(), field_name_list.iloc[i]['Field_Value'];
		# add_Doc_Field_Value_sqlstr = 'IF NOT EXISTS (SELECT * FROM [xtr].[Doc_Field_Value] WHERE ([Field_Name_ID] = ' + str(field_name_list.iloc[i]['Field_Name_ID']) + '))';
		# add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + 'INSERT INTO [xtr].[Doc_Field_Value] (Field_Name_ID, Field_Value, Calcrt_ID, Field_Value_Is_Numeric) VALUES ';
		# add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '(' + str(field_name_list.iloc[i]['Field_Name_ID']) + ', \'' \
		# 							+ str(field_name_list.iloc[i]['Field_Value']) + '\', \'' + str(field_name_list.iloc[i]['Calcrt_ID']) + '\', ISNUMERIC(\'' + str(field_name_list.iloc[i]['Field_Value']) + '\'));';
		
		

		add_Doc_Field_Value_sqlstr = 'UPDATE [xtr].[Doc_Field_Value] SET ' ;
		add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Field_Value] = \'' + str(field_name_list.iloc[i]['Field_Value']) + '\' ,';
		add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Calcrt_ID] = \'' + str(field_name_list.iloc[i]['Calcrt_ID']) + '\',';
		add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Field_Value_Is_Numeric] = ISNUMERIC( \'' + str(field_name_list.iloc[i]['Field_Value']) + '\') WHERE ';
		add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Field_Name_ID] = ' + str(field_name_list.iloc[i]['Field_Name_ID']);
		add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + ' IF @@ROWCOUNT=0 ' + 'INSERT INTO [xtr].[Doc_Field_Value] (Field_Name_ID, Field_Value, Calcrt_ID, Field_Value_Is_Numeric) VALUES (';
		add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + str(field_name_list.iloc[i]['Field_Name_ID']) + ', \'' \
									+ str(field_name_list.iloc[i]['Field_Value']) + '\', \'' + str(field_name_list.iloc[i]['Calcrt_ID']) + '\', ISNUMERIC(\'' + str(field_name_list.iloc[i]['Field_Value']) + '\'));';
		
		# print '*********************************';
		# print add_Doc_Field_Value_sqlstr;
		# print '*********************************';

		# print add_Doc_Field_Value_sqlstr;
		execute_pure_query(add_Doc_Field_Value_sqlstr);

#######################################################################################



#######################################################################################






#######################################################################################