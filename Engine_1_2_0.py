from DB_Controller_1_2_0 import *;
from PDF_Extractor_1_2_0 import *;
from Extra_Logic_1_2_0 import *;
from IntRate_Logic_1_2_0 import *;
from TestLog_Generator import *;
from PDF_Cropping_V_1_2_0 import *;
import pickle;
import random;
import sys;




image_generation_swtich = 1;      ##### This is a very cool design, every statament that will call the image generation logics will check this signal
								  ##### That mean, if we want to generate image, we should set the switch to be 1;
								  ##### If we don't want spending time on pictures, we turn it 0;

db_conn = 0;



#####################################################################################
def pdf_major_process_with_border_detection(file_name_full):
	print '=======================================================================================================================';
	print '=======================================================================================================================';
	print '=======================================================================================================================';
	start_time = time.time();
	print file_name_full;
	file_name = file_name_full.split('\\')[-1];
	print file_name;
	write_row(test_wb, test_ws, ['','','']);
	

	running_time_table = [];
	running_time_table.append(['----------------','The following is the running time for each phase','----------------------']);


	##############################################################################################
	########################## Update/Insert entry to Doc_PDF table  #############################
	##############################################################################################
	Doc_ID = add_file_Doc_PDF(file_name);
	
	write_row(test_wb, test_ws, ['','','']);


	##############################################################################################
	########################## Update/Insert entry to Doc_Deal table  ############################
	##############################################################################################
	add_deal_Doc_Deal(file_name);

	##############################################################################################
	##################### Get condition set related to this pdf file type     ####################
	#####################   get the component list based on the condition set ####################
	##############################################################################################

	sql_query_1 = 'SELECT * FROM xtr.Doc_Pre INNER JOIN xtr.Doc_PDF ON xtr.Doc_Pre.[Doc_Type_ID] = xtr.Doc_PDF.[Doc_Type_ID] AND xtr.Doc_PDF.[Doc_Version] = xtr.Doc_Pre.[Doc_Version] \
					WHERE xtr.Doc_PDF.[Doc_ID] =' + str(Doc_ID) + ';';


	condition_set_df = execute_pure_query_to_pddf(sql_query_1);
	print len(condition_set_df);	
	
	write_row(test_wb, test_ws, ['Number of Fields', str(len(condition_set_df)), '']);

	condition_set_df_table = [];
	write_row(test_wb, test_ws, ['Doc Version',str(condition_set_df.iloc[0]['Doc_Version'].tolist()),'']);
	condition_set_df_table.append(['','','']);
	condition_set_df_table.append(['','','']);
	condition_set_df_table.append(['----------------','The following is the condition set stored in the [xtr].[Doc_Pre] table for this agency pdf','----------------------']);


	for i in range(0, len(condition_set_df)):
		condition_set_df_table.append(['', '*************************************************************************************************************', '']);
		condition_set_df_table.append(['Field Name', condition_set_df.iloc[i]['Field_Name'], '']);
		condition_set_df_table.append(['Search String', condition_set_df.iloc[i]['Search_String'], '']);
		condition_set_df_table.append(['Page Number', condition_set_df.iloc[i]['Page_Num'], '']);
		condition_set_df_table.append(['Is From Table', condition_set_df.iloc[i]['Is_From_Table'], '']);
		condition_set_df_table.append(['Is Horizontal', condition_set_df.iloc[i]['Is_Horizontal'], '']);	
		condition_set_df_table.append(['Calcrt ID', condition_set_df.iloc[i]['Calcrt_ID'], '']);
		condition_set_df_table.append(['', '*************************************************************************************************************', '']);

	condition_set_df_table.append(['','','']);
	write_table(test_wb, test_ws, condition_set_df_table);
	page_num_list = [];

	for i in range(0,len(condition_set_df)):
		page_num_list.append(condition_set_df.iloc[i]['Page_Num']);

	page_num_list = list(sorted(set(page_num_list)));                                     # HAHAHA!
 	
 	page_range_str = '';
 	for item in page_num_list:
 		page_range_str = page_range_str + str(item) + ' ';

	write_row(test_wb, test_ws, ['Page Range',page_range_str,'These pages are processed only for extracting the information in fixed pages.(Not TERMS SHEET or Available Combinations)']);

	print page_num_list;

	print "database--- %s seconds ---" % (time.time() - start_time);
	running_time_table.append(['Database connection time: ',str(time.time() - start_time), 'seconds']);
	print ' ';
	start_time = time.time();
	pdf_document = opt_pdf_document(file_name_full);
	print 'PDF document object create time: ',time.time() - start_time, ' seconds.';
	running_time_table.append(['PDF object create time: ',str(time.time() - start_time), 'seconds']);
	print ' ';
	start_time = time.time();
	initial_page_list = pdfminer_configuration(pdf_document, page_num_list);
	component_list = split_string_detail_process(initial_page_list, page_num_list);
	print '========================== The length of the component_list is: ' + str(len(component_list));
	sorted_pl_component_list = page_level_process(initial_page_list);
	

	###################
	###################
	###################

	# pkl_name = file_name_full.split('\\')[-1][:-4] + '.pkl';
	# print pkl_name;
	# output_2 = open(pkl_name, 'wb');
	# pickle.dump(sorted_pl_component_list, output_2);
	# output_2.close();
	# pkl_file = open(pkl_name, 'rb');
	# sorted_pl_component_list = pickle.load(pkl_file);

	###################
	###################
	###################


	print '========================== The length of the pl_component_list is: ' + str(len(sorted_pl_component_list));
	print ' ';
	print 'Character level component list and page level component list generating time: ',time.time() - start_time, 'seconds.';
	print ' ';
	start_time = time.time();



	##############################################################################################
	################################ Generate Mid Csv file  ######################################
	##############################################################################################
	title_list = ['Page_Num','Component_Index','Component_Type','Detail_Component_Type','Coor_Min_X','Coor_Min_Y','Coor_Max_X',\
	'Coor_Max_Y','Matrix', 'Font', 'Adv(wid*fsize*scal)','Text','FontSize(pt)','Upright(Bool)','Text_Direction','Box_Width','Box_Height']
	generate_mid_csv(file_name_full,sorted_pl_component_list,title_list);
	print "csv_file_writing--- %s seconds ---" % (time.time() - start_time);
	print ' ';
	running_time_table.append(['CSV mid-file writing time: ',str(time.time() - start_time), 'seconds']);
	start_time = time.time();
	
	
	##############################################################################################
	################################ Core Logic Called here ######################################
	##############################################################################################
	all_fields_result_list = [];
	Calcrt_ID_Field_Name_list = [];
	search_string = '';
	for i in range(0, len(condition_set_df)):

		print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~';
		print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~';

		temp_calcrt_id_field_name = [condition_set_df.iloc[i]['Calcrt_ID'], condition_set_df.iloc[i]['Field_Name']];

		Calcrt_ID_Field_Name_list.append(temp_calcrt_id_field_name);

		sorted_split_component_list = component_list;
		print condition_set_df.iloc[i]['Search_String'];
		search_string = condition_set_df.iloc[i]['Search_String'];


		if condition_set_df.iloc[i]['Is_From_Table']:
			search_string_center_position =	get_search_string_position(sorted_pl_component_list, search_string);
			coordinates_borders = [Minpoint_X,Minpoint_Y,Maxpoint_X,Maxpoint_Y] = border_detect_by_search_string(search_string_center_position, condition_set_df.iloc[i], sorted_split_component_list, sorted_pl_component_list);
			print coordinates_borders;

		if (not condition_set_df.iloc[i]['Is_From_Table']) and (condition_set_df.iloc[i]['Result_Type'] == 'string'):
			[Minpoint_X,Minpoint_Y,Maxpoint_X,Maxpoint_Y] = [0.0,0.0,0.0,0.0];        #### this indicates no border detection logics applied for the non-table text fields

		#########################################################
		#### important modification here!!!!!!               ####
		#### we add four more columns to the condition_set   ####
		#### which contains the four coordinates we          ####
		#### generated from the range detection process      ####
		#########################################################
		modified_condition_set = condition_set_df.iloc[i];
		modified_condition_set['Minpoint_X'] = Minpoint_X;
		modified_condition_set['Minpoint_Y'] = Minpoint_Y;
		modified_condition_set['Maxpoint_X'] = Maxpoint_X;
		modified_condition_set['Maxpoint_Y'] = Maxpoint_Y;

		if modified_condition_set['Field_Name'] == 'Maturity':
			print 'here';
			modified_condition_set['Maxpoint_X'] = 580;

		# print modified_condition_set;
		# print '--------------------------';
		# print type(modified_condition_set);
		# print modified_condition_set.iloc[0];
		[ranged_component_list, table_content_list, col_or_row_content_list, string_content_list] = search_field_by_condition(modified_condition_set, sorted_pl_component_list ,sorted_split_component_list,page_num_list);
		print 'We generated a list with the length: ', len(col_or_row_content_list); 
		print 'We generated a string list with the length: ', len(string_content_list) 
		if len(string_content_list) != 0:
			print string_content_list[0][0];
			if '.' == string_content_list[0][0][0]:
				string_content_list[0][0] = ''.join(['U',string_content_list[0][0]]); 
		# if len(string_content_list) > 0:
		# 	for item in string_content_list:
		# 		print item;
		# print '---------------------------------------------------------------';
		# for item in col_or_row_content_list:
		# 	print item[0], len(item[0]);

		temp_field_object = [];
		if condition_set_df.iloc[i]['Result_Type'] == 'list':
			temp_field_object.append(condition_set_df.iloc[i]['Field_Name']);
			temp_field_object.append(col_or_row_content_list);
			all_fields_result_list.append(temp_field_object);
		if condition_set_df.iloc[i]['Result_Type'] == 'string':
			temp_field_object.append(condition_set_df.iloc[i]['Field_Name']);
			temp_field_object.append(string_content_list);
			all_fields_result_list.append(temp_field_object);

	###########################################################
	##   combined_all_fields_result_list 					 ##				
	##   this list is used for rearrange the field           ##
	##   list. If one field value appears in several         ##
	##   pdf pages, this list will merge them together       ##
	##   under one object                                    ##
	###########################################################		

	# print '^^^^^^^^^^^^^^^^^^^^^^^^';
	combined_all_fields_result_list = [];
	for item in all_fields_result_list:
		# print item;
		if item[0] not in combined_all_fields_result_list:
			combined_all_fields_result_list.append([item[0],[]]);
	# print '^^^^^^^^^^^^^^^^^^^^^^^^';
	# print '------------------------------------------------------';
	# for item in combined_all_fields_result_list:
	# 	print item; 

	for i in range(0,len(combined_all_fields_result_list)):
		for j in range(0, len(all_fields_result_list)):
			if all_fields_result_list[j][0] == combined_all_fields_result_list[i][0]:
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + all_fields_result_list[j][1];

	# print len(combined_all_fields_result_list);
	print '========================================================================';
	# for item in combined_all_fields_result_list:
	# 	print item;
	# 	print ' ';
	# 	print ' ';

	##############################################
	###  Step 1:							   ###	
	###	 Find out the Tranche and Cusip lists  ###
	##############################################		
	Tranche_list = [];
	Cusip_list = [];
	

	##############################################
	#### Append extra classes to the tranche list
	##############################################



	for item in combined_all_fields_result_list:
		field_process_flag = 0;
		if (field_process_flag == 0) and (item[0] == 'Tranche'):
			Tranche_list = Tranche_list + item[1];
			field_process_flag = 1;
		if (field_process_flag == 0) and (item[0] == 'Cusip'):
			Cusip_list = Cusip_list + item[1];
			field_process_flag = 1;
	
	print ' ';
	print ' ';
	print '----------------Start to extract extra classes in vertical tables: ----------------';
	print ' ';
	print ' ';
	[final_result_component_list, initial_page_list_int] = process_vertical_content(file_name_full,pdf_document);	

	# if len(final_result_component_list) != 0:
	# 	for item in final_result_component_list:
	# 		for itemitem in item:
	# 			print itemitem;
	# 		print '-------------------------------------------------';
	print ' ';
	# print ' ';
	# print ' '; 

	# for item in final_result_component_list:
	# 	Tranche_list.append(item[0][0]);
	# 	Cusip_list.append(item[0][5]);
	
	# print ' ';
	# print '&&                        __';
	# for i in range(0, len(combined_all_fields_result_list)):
	# 	print combined_all_fields_result_list[i][0];
	# 	for item in combined_all_fields_result_list[i][1]:
	# 		print item;
	# print '____________________________';
	# print len(Tranche_list);
	# print len(Cusip_list);
	# print '=========================== length here ============================';
	# print len(final_result_component_list);
	if len(final_result_component_list) != 0:	
		for i in range(0, len(combined_all_fields_result_list)):
			if combined_all_fields_result_list[i][0] == 'Maturity':
				# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!here';
				# print len(combined_all_fields_result_list[i][1]);
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + final_result_component_list[6];
				# print len(combined_all_fields_result_list[i][1]);
			if combined_all_fields_result_list[i][0] == 'Class Balance':
				# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!here';
				# print len(combined_all_fields_result_list[i][1]);
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + final_result_component_list[1];
				# print len(combined_all_fields_result_list[i][1]);
			if combined_all_fields_result_list[i][0] == 'Descriptors':
				# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!here';
				# print len(combined_all_fields_result_list[i][1]);
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + final_result_component_list[2];
				# print len(combined_all_fields_result_list[i][1]);	
			if combined_all_fields_result_list[i][0] == 'Descriptors_IntType':
				# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!here';
				# print len(combined_all_fields_result_list[i][1]);
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + final_result_component_list[4];
				# print len(combined_all_fields_result_list[i][1]);
			if combined_all_fields_result_list[i][0] == 'Class Coupon':
				# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!here';
				# print len(combined_all_fields_result_list[i][1]);
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + final_result_component_list[3];
				# print len(combined_all_fields_result_list[i][1]);
			if combined_all_fields_result_list[i][0] == 'Tranche':
				# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!here';
				# print len(combined_all_fields_result_list[i][1]);
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + final_result_component_list[0];
				# print len(combined_all_fields_result_list[i][1]);
			if combined_all_fields_result_list[i][0] == 'Cusip':
				# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!here';
				# print len(combined_all_fields_result_list[i][1]);
				combined_all_fields_result_list[i][1] = combined_all_fields_result_list[i][1] + final_result_component_list[5];
				# print len(combined_all_fields_result_list[i][1]);
		Tranche_list = Tranche_list + final_result_component_list[0];
		Cusip_list = Cusip_list + final_result_component_list[5];
	

	random_pick_index = random.randint(0, len(Cusip_list)-1);
	print 'RAND!!!!!!!!!!!!!!!!!!!';
	print random_pick_index;


	# print ' ';
	# print len(Tranche_list);
	# print len(Cusip_list);
	# print '';
	# print '';
	# for i in range(0, len(combined_all_fields_result_list)):
	# 	print len(combined_all_fields_result_list[i][1]);

	# print '**************************************************';
	# for item in Tranche_list:
	# 	print item;
	# print '**************************************************';

	# print ' ';
	# print ' ';

	# print '**************************************************';
	# for item in Cusip_list:
	# 	print item;
	# print '**************************************************';

	Tranche_ID_list = add_Tranche_Doc_Tranche(file_name, Tranche_list, Cusip_list);      #### here we return the tranche_id_list which is the list of all the newly added tranche ids
	Field_Name_ID_list = add_Doc_Field_Name(Tranche_ID_list, Calcrt_ID_Field_Name_list);



	intrate_modify_list_tranche = [];
	intrate_modify_list_intrate = [];
	for i in range(0, len(combined_all_fields_result_list)):
		if combined_all_fields_result_list[i][0] == 'Tranche':
			for item in combined_all_fields_result_list[i][1]:
				intrate_modify_list_tranche.append(item[0]);
		if combined_all_fields_result_list[i][0] == 'Class Coupon':
			for item in combined_all_fields_result_list[i][1]:
				intrate_modify_list_intrate.append(item[0]);

	intrate_modify_tranche_intrate = [];
	if len(intrate_modify_list_tranche) == len(intrate_modify_list_intrate):
		for i in range(0, len(intrate_modify_list_tranche)):
			intrate_modify_tranche_intrate.append([intrate_modify_list_tranche[i],intrate_modify_list_intrate[i]]);
	else:
		print 'NO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!';

	need_change_int_index_list = [];
	for i in range(0, len(intrate_modify_tranche_intrate)):
		temp_tranche = intrate_modify_tranche_intrate[i][0];
		temp_intrate = intrate_modify_tranche_intrate[i][1];
		print temp_tranche,temp_intrate;

		if bool(re.search(r'^\([0-9]{1}\)$', temp_intrate.replace(' ',''))):
			need_change_int_index_list.append([temp_tranche,temp_intrate,i,[]]);

	# add_Doc_Field_Value(Field_Name_ID_list, combined_all_fields_result_list);
	# for item in Tranche_ID_list:
	# 	print item;

	# for item in Field_Name_ID_list:
	# 	print item;


	####################################################################################
	####################################################################################
	####################################################################################
	####################################################################################
	####################################################################################
	####################################################################################

	page_num_list = range(0, len(initial_page_list_int));
	sorted_pl_component_list_int = page_level_process(initial_page_list_int);
	special_interest_rate_list, ts_start_page, ts_end_page = process_term_sheet(pdf_document, sorted_pl_component_list_int);
	for item in need_change_int_index_list:
		print item;
	print '';
	print '';
	print '-------------------------- Special Interest Rate List ---------------------------------';
	print 'Length of special interest rate items list: ', len(special_interest_rate_list);
	print '';
	print '';
	for item in special_interest_rate_list:
		print item;
	print '';

	# for i in range(0, len(combined_all_fields_result_list)):

	print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&';
	print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&';
	print '';
	print bool(len(need_change_int_index_list) == len(special_interest_rate_list)), '       ' ,len(need_change_int_index_list), '           ', len(special_interest_rate_list), '        ';
	
	for i in range(0, len(need_change_int_index_list)):
		for j in range(0, len(special_interest_rate_list)):
			if need_change_int_index_list[i][0] == special_interest_rate_list[j][0]:
				need_change_int_index_list[i][1] = special_interest_rate_list[j][1];
				need_change_int_index_list[i][3] = special_interest_rate_list[j][2];

	for item in need_change_int_index_list:
		print item;

	print '';
	print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&';	
	print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&';




	for i in range(0, len(combined_all_fields_result_list)):
		if combined_all_fields_result_list[i][0] == 'Class Coupon':
			for j in range(0, len(combined_all_fields_result_list[i][1])):
				# print j, '     ', combined_all_fields_result_list[i][1][j][0];
				for item in need_change_int_index_list:
					if j == item[2] and item[3]!=[]:
						combined_all_fields_result_list[i][1][j][0] = item[1];
						combined_all_fields_result_list[i][1][j][1:] = item[3];

	print '';
	print '';
	print '------------------------------------------------------------------------------';
	print '------------------------------------------------------------------------------';
	

	list_length = len(combined_all_fields_result_list[0][1]);
	
	print list_length;

	write_row(test_wb, test_ws, ['Number of Classes', str(list_length)]);

	combined_all_fields_result_list_table = [];
	combined_all_fields_result_list_table.append(['','','']);
	combined_all_fields_result_list_table.append(['----------------','The following is the result set generated by the scripts: ','----------------------'])
	for i in range(0, list_length):
		# print '**************************************************************************';
		combined_all_fields_result_list_table.append([i+1,'*************************************************************************************************************','']);
		disp_str = '';
		for j in range(0, len(combined_all_fields_result_list)):
			if len(combined_all_fields_result_list[j][1]) > 1:
				disp_str = disp_str + str(combined_all_fields_result_list[j][1][i][0]) + '          \n';
				combined_all_fields_result_list_table.append([combined_all_fields_result_list[j][0],str(combined_all_fields_result_list[j][1][i][0]),'']);
			if len(combined_all_fields_result_list[j][1]) == 1:
				disp_str = disp_str + str(combined_all_fields_result_list[j][1][0][0]) + '          \n';
				combined_all_fields_result_list_table.append([combined_all_fields_result_list[j][0],str(combined_all_fields_result_list[j][1][0][0]),'']);
		# print disp_str;
		# combined_all_fields_result_list_table.append(['',disp_str,'']);
		# print '**************************************************************************';
		combined_all_fields_result_list_table.append(['','*************************************************************************************************************','']);

	combined_all_fields_result_list_table.append(['','','']);
	combined_all_fields_result_list_table.append(['','','']);


	####################################################################################
	fields_list = [];
	for item in combined_all_fields_result_list:
		fields_list.append(item[0]);

	write_row_signal(test_wb, test_ws, fields_list);

	for i in range(0, list_length):
		disp_str = '';
		single_result_item_list = [];
		for j in range(0, len(combined_all_fields_result_list)):
			if len(combined_all_fields_result_list[j][1]) > 1:
				disp_str = disp_str + str(combined_all_fields_result_list[j][1][i][0]) + '    ';
				single_result_item_list.append(str(combined_all_fields_result_list[j][1][i][0]));
			if len(combined_all_fields_result_list[j][1]) == 1:
				if len(str(combined_all_fields_result_list[j][1][0][0])) < 30:
					disp_str = disp_str + str(combined_all_fields_result_list[j][1][0][0]) + '    ';
					single_result_item_list.append(str(combined_all_fields_result_list[j][1][0][0]));
				else:
					disp_str = disp_str + str(combined_all_fields_result_list[j][1][0][0])[:30] + '    ';
					single_result_item_list.append(str(combined_all_fields_result_list[j][1][0][0][:30]));
		print disp_str;
		# print single_result_item_list;
		write_row_signal(test_wb, test_ws, single_result_item_list);

	####################################################################################

	####################################################################################
	sample_testing_sql = "SELECT * FROM ([xtr].[Doc_Field_Name] dfn INNER JOIN [xtr].[Doc_Field_Value] dfv ON dfn.Field_Name_ID = dfv.Field_Name_ID) INNER JOIN [xtr].[Doc_Tranche] dt ON dfn.[Tranche_ID] = dt.[Tranche_ID] WHERE dt.Cusip = ";
	sample_cusip = Cusip_list[random_pick_index][0];
	sample_cusip = sample_cusip.replace(' ','');
	sample_testing_sql = sample_testing_sql + "'" + str(sample_cusip) + "';";
	write_row(test_wb, test_ws, ['Sample Cusip', str(sample_cusip), '']);
	write_row(test_wb, test_ws, ['Testing SQL Statement', sample_testing_sql, 'You can copy-paste this to the SQL Server and run it to double check the result']);
	write_row(test_wb, test_ws, ['Index of this Cusip', str(random_pick_index+1), 'You can use this number to quickly find out the item printed in the following result set.(This is a psyeudo random number)'])
	
	# print sample_testing_sql;
	

	write_table(test_wb, test_ws, combined_all_fields_result_list_table);

	print "Core logic--- %s seconds ---" % (time.time() - start_time);
	running_time_table.append(['Core Logic time: ',str(time.time() - start_time), 'seconds']);
	running_time_table.append(['Max Page Proc Time: ','10','seconds']);
	running_time_table.append(['------------------------------------','---------------------------------------------------------------------------------------------------------------','-----------------------------------']);
	write_table(test_wb, test_ws, running_time_table);
	start_time = time.time();
	print '------------------------------------------------------------------------------';
	print '------------------------------------------------------------------------------';


	####################################################################################################


	page_number_rotation_list = [];

	class_coupon_index = 0;

	print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&';
	for i in range(0,len(combined_all_fields_result_list)):
		# print combined_all_fields_result_list[i][0];
		if combined_all_fields_result_list[i][0] == 'Class Coupon':
			print 'Class COUPON!!!!!!!!!!!!!!!!!!!!!!!!!';
			class_coupon_index = i;
			print i;


		for j in range(0, len(combined_all_fields_result_list[i][1])):
			page_number_rotation_list.append([combined_all_fields_result_list[i][1][j][1], combined_all_fields_result_list[i][1][j][-1]]);
			print combined_all_fields_result_list[i][1][j];
	print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$';

	####################################################################################################

	for i in range(ts_start_page, ts_end_page):
		page_number_rotation_list.append([i,'Horizontal']);

	need_special_process_flag = 0;	
	print '';
	print 'Special!!!!!!!!!!!!!!!!!!!!!!!!!!!!';
	for i in range(0, len(combined_all_fields_result_list[class_coupon_index][1])):
		if '(' in combined_all_fields_result_list[class_coupon_index][1][i][0]:
			need_special_process_flag = 1;
			print combined_all_fields_result_list[class_coupon_index][1][i];
			combined_all_fields_result_list[class_coupon_index][1][i][1] = 0;
			print '*******************';
			print combined_all_fields_result_list[class_coupon_index][1][i];
	print '';

	# for item in page_number_rotation_list:
	# 	print item;

	
	####################################################################################################
	####################################################################################################
	if image_generation_swtich == 1:
		page_number_rotation_list = list(set(map(tuple,page_number_rotation_list)));
		for item in page_number_rotation_list:
			print item;
		global db_conn;
		pdf_page_crop(file_name_full,page_number_rotation_list, db_conn);


	


	merge_int_info_box = [];
	####################################################################################################
	if need_special_process_flag == 1:
		print '';
		print '';
		print 'Interest Rates !!!! WTF:::::::::::::: ', get_search_string_position(sorted_pl_component_list_int, 'Interest Rates:');
		merge_int_info_box.append(get_search_string_position(sorted_pl_component_list_int, 'Interest Rates:'));

		print 'Allocation Of Principals!!!!  WTF:::::::::::: ',get_search_string_position(sorted_pl_component_list_int, 'Allocation of Principal:');
		merge_int_info_box.append(get_search_string_position(sorted_pl_component_list_int, 'Allocation of Principal:'));
		print '';

	####################################################################################################

	if merge_int_info_box!=[]:
		print '';
		print 'Merge Info Box!!!!!!!!!!!!!!!!!!!!!';
		print merge_int_info_box;
	

	####################################################################################################
	if image_generation_swtich == 1:
		add_Doc_Field_Value_HLImage_Generation(Field_Name_ID_list, combined_all_fields_result_list, merge_int_info_box, db_conn);
	else:
		add_Doc_Field_Value(Field_Name_ID_list, combined_all_fields_result_list);


	####################################################################################################



	sample_db_result_df = execute_pure_query_to_pddf(sample_testing_sql);

	print 'length of sample db result: ', len(sample_db_result_df);

	write_row(test_wb, test_ws ,['******************************','------------------ The following is the DB result from the sample query sql statement  -------------------','******************************']);

	write_row(test_wb, test_ws, ['','************************************************************************************************************************','']);
	
	sample_db_result_obj_str = '';
	sample_db_result_obj_str = sample_db_result_obj_str + 'Tranche Name: ' + str(sample_db_result_df.iloc[0]['Tranche_Name']) + '\n';
	sample_db_result_obj_str = sample_db_result_obj_str + 'Cusip: ' + str(sample_db_result_df.iloc[0]['Cusip']) + '\n';
	sample_db_result_obj_str = sample_db_result_obj_str + '----------------------------------------------\n';
	for i in range(0, len(sample_db_result_df)):
		sample_db_result_obj_str = sample_db_result_obj_str + str(sample_db_result_df.iloc[i]['Field_Name']) + ' : ';
		sample_db_result_obj_str = sample_db_result_obj_str + str(sample_db_result_df.iloc[i]['Field_Value']) + '\n';

	write_row(test_wb, test_ws, ['', sample_db_result_obj_str, '']);

	####################################################################################
	####################################################################################
	####################################################################################
	write_row(test_wb, test_ws,['','************************************************************************************************************************','']);



	####################################################################################################

#####################################################################################



#####################################################################################
def test_special_interest_rate(file_name_full):
	pdf_document = opt_pdf_document(file_name_full);
	page_num_list= None;
	print '------------------- Int Rate Process start here: -----------------------';
	initial_page_list = pdfminer_configuration(pdf_document, page_num_list);
	page_num_list = range(0, len(initial_page_list));
	# print '(';
	# print page_num_list;
	# print ')';
	sorted_pl_component_list = page_level_process(initial_page_list);


	# sorted_detailed_component_list = [];
	###################################################
	###################################################
	###################################################
	# output_1 = open('pdf_document.pkl', 'wb');
	# pickle.dump(pdf_document, output_1);
	# output_1.close();

	# pkl_name = file_name_full.split('\\')[-1][:-4] + '.pkl';
	# print pkl_name;
	# output_2 = open(pkl_name, 'wb');
	# pickle.dump(sorted_pl_component_list, output_2);
	# output_2.close();


	# pkl_file = open(pkl_name, 'rb');
	# sorted_pl_component_list = pickle.load(pkl_file);
	####################################################
	####################################################
	####################################################


	process_term_sheet(pdf_document, sorted_pl_component_list);     # I personally don't recommend a design like this. This is not the perfect design. 
																	# Might potentially cause some problems. But it is very fast and efficient.
																	# the only thing is the parameters definition is not consistent
#####################################################################################


#####################################################################################
def test_cropping_methods(file_name_full):
	page_number_rotation_list = [[1, 'Horizontal'], [2, 'Vertical'], [3, 'Horizontal']];
	test_crop_pdf(file_name_full,page_number_rotation_list);



#####################################################################################
	

########################################################################################################
########################################################################################################
########################################################################################################
##     Here we start !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
########################################################################################################
########################################################################################################
########################################################################################################




test_log_file_name = test_log_generator_config();




disp_proj_info();

############### DB Info ######################
## DRIVER={ODBC Driver 11 for SQL Server};  ##
## SERVER=dydevsql03;                       ##
## DATABASE=Guest_Writer;                   ##
## UID=TechOps_Guest;                       ##
## PWD=GuestSimSim                          ##
##############################################	

test_log_file_name_cmd = test_log_file_name[:-5] + '.txt';
print '-----';
print test_log_file_name;
fd = open(test_log_file_name_cmd,'a');
old_stdout = sys.stdout;
sys.stdout = fd;

total_start_time = time.time();



db_conn = create_db_connection('ODBC Driver 11 for SQL Server', 'dydevsql03', 'Guest_Writer', 'TechOps_Guest','GuestSimSim');



# pdf_directory_path = 'F:\Desktop\PythonProject\PDF_Extractor\PDFDirectory\*.pdf';

pdf_directory_path = 'F:\Desktop\PythonProject\PDF_Extractor\V_1_2_0_dev\PDFDirectory\*.pdf';
file_name_list_full = get_file_list_on_given_directory(pdf_directory_path);

sys.stdout = old_stdout;
print 'Number of files in the folder: ',len(file_name_list_full);
sys.stdout = fd;
# global TEST_LOG_CONTENT_TABLE;
# TEST_LOG_CONTENT_TABLE = [];
TEST_LOG_CONTENT_TABLE.append(['Version Info', 'V 1.2.0']);
TEST_LOG_CONTENT_TABLE.append(['Number of Files', str(len(file_name_list_full))]);

test_wb = 0;
test_ws = 0;

file_index = 1;
test_wb = create_xlsx_workbook(test_log_file_name);







for file_name_full in file_name_list_full:
	
	print ' ';
	print '------------------ file name full ---------------------';
	print file_name_full;
	print '-------------------------------------------------------';
	print ' ';
	# global TEST_LOG_CONTENT_TABLE;
	file_name_simp = file_name_full.split('\\')[-1][10:25];
	test_ws = add_work_sheet(test_wb, str(file_index) + ' ' +file_name_simp)
	write_row(test_wb, test_ws, TEST_LOG_TITLE);
	TEST_LOG_CONTENT_TABLE.append([file_index,'-------------------------------------------------------------------------']);
	TEST_LOG_CONTENT_TABLE.append(['Agency Type','Ginnie Mae']);
	TEST_LOG_CONTENT_TABLE.append(['File Name', file_name_full.split('\\')[-1]]);
	write_table(test_wb, test_ws,TEST_LOG_CONTENT_TABLE);
	pdf_major_process_with_border_detection(file_name_full);
	
	TEST_LOG_CONTENT_TABLE = TEST_LOG_CONTENT_TABLE[0:4];
	file_index = file_index + 1;

total_end_time = time.time();


sys.stdout = old_stdout;
print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$';
print 'Total Running time is: ', (total_end_time - total_start_time) / 60, 'minutes.';
print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$';



fd.close();
disp_proj_endding();
# for item in TEST_LOG_CONTENT_TABLE:
# 	print item;


test_wb.close();


# test_linked();