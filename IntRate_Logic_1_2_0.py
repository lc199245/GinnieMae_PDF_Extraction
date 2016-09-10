from PDF_Extractor_1_2_0 import *;
from TestLog_Generator import *;
import pandas as pd;



def search_intial_interest(centerpoint_coordinates_initial, terms_sheet_pl_component_list):
	if len(centerpoint_coordinates_initial) == 3:
		bottom_Y = 0;
		top_Y = 0;
		for i in range(0, len(terms_sheet_pl_component_list)):
			terms_sheet_pl_component_obj = terms_sheet_pl_component_list[i];
			if terms_sheet_pl_component_obj[0] == centerpoint_coordinates_initial[2]:
				if (terms_sheet_pl_component_obj[6] < centerpoint_coordinates_initial[1]) and ('Text' not in terms_sheet_pl_component_obj[2])\
					and (terms_sheet_pl_component_obj[-2] > terms_sheet_pl_component_obj[-1]) and (terms_sheet_pl_component_obj[3] <= centerpoint_coordinates_initial[0]) \
					and (terms_sheet_pl_component_obj[5] >= centerpoint_coordinates_initial[0]) and (abs(centerpoint_coordinates_initial[1] - terms_sheet_pl_component_obj[6]) < 30):
					# print terms_sheet_pl_component_obj;
					top_Y = terms_sheet_pl_component_obj[6];


				if (terms_sheet_pl_component_obj[6] < centerpoint_coordinates_initial[1]) and ('Text' not in terms_sheet_pl_component_obj[2])\
					and (terms_sheet_pl_component_obj[-2] > terms_sheet_pl_component_obj[-1]) and (terms_sheet_pl_component_obj[3] < 100) \
					and (abs(centerpoint_coordinates_initial[1] - terms_sheet_pl_component_obj[6]) > 30):
					# print terms_sheet_pl_component_obj;
					bottom_Y = terms_sheet_pl_component_obj[6];
					break;
		if top_Y == 0:
			top_Y = centerpoint_coordinates_initial[1]-20;
		print '';
		print 'The top border\'s Y value for the table is: ', top_Y;
		print '';
		print '';
		print 'The bottom border\'s Y value for the table is: ', bottom_Y;
		print '';

		max_X = 0;
		min_X = 1000;

		for i in range(0, len(terms_sheet_pl_component_list)):
			terms_sheet_pl_component_obj = terms_sheet_pl_component_list[i];
			if terms_sheet_pl_component_obj[0] == centerpoint_coordinates_initial[2]:
				if (terms_sheet_pl_component_obj[6] <= centerpoint_coordinates_initial[1]) and (terms_sheet_pl_component_obj[6] <= top_Y) and (terms_sheet_pl_component_obj[6] >= bottom_Y) and ('Text' in terms_sheet_pl_component_obj[2]):
					# print terms_sheet_pl_component_obj[7];
					if terms_sheet_pl_component_obj[3] < min_X:
						min_X = terms_sheet_pl_component_obj[3];
					if terms_sheet_pl_component_obj[5] > max_X:
						max_X = terms_sheet_pl_component_obj[5];

		max_X = max_X + 1;
		min_X = min_X - 1;


		max_X = 700;                                  ### extremly fragile
		min_X = 70;                                   ### heheda

		print '';
		print 'The left border\'s X value for the table is: ', min_X;
		print '';
		print '';
		print 'The right border\'s X value for the table is: ', max_X;
		print '';



		int_rate_initial_condition_list = [[0,0,'V2016','Terms Sheet','',centerpoint_coordinates_initial[2], min_X, bottom_Y, max_X, top_Y, True,True,True,'list',0,1,1,0,'','Top']];

		int_rate_initial_condition_set = pd.DataFrame(int_rate_initial_condition_list, columns = ['Doc_Pre_ID', 'Doc_Type_ID', 'Doc_Version', 'Field_Name', 'Search_String', 'Page_Num',\
						  'Minpoint_X','Minpoint_Y','Maxpoint_X','Maxpoint_Y',\
						  'Is_From_Table', 'Is_Horizontal', 'Is_Organized_In_Row', 'Result_Type', 'Minimum_Length', \
						  'Column_Number', 'Max_Column', 'Max_Row', 'Calcrt_ID', 'Relative_Pos']);
		return int_rate_initial_condition_set;
	return [];	

def search_approximate_interest(centerpoint_coordinates_approximate, terms_sheet_pl_component_list):
	if len(centerpoint_coordinates_approximate) == 3:
		bottom_Y = 0;
		top_Y = 0;
		for i in range(0, len(terms_sheet_pl_component_list)):
			terms_sheet_pl_component_obj = terms_sheet_pl_component_list[i];
			if terms_sheet_pl_component_obj[0] == centerpoint_coordinates_approximate[2]:
				if (terms_sheet_pl_component_obj[6] < centerpoint_coordinates_approximate[1]) and ('Text' not in terms_sheet_pl_component_obj[2])\
					and (terms_sheet_pl_component_obj[-2] > terms_sheet_pl_component_obj[-1]) and (terms_sheet_pl_component_obj[3] <= centerpoint_coordinates_approximate[0]) \
					and (terms_sheet_pl_component_obj[5] >= centerpoint_coordinates_approximate[0]) and (abs(centerpoint_coordinates_approximate[1] - terms_sheet_pl_component_obj[6]) < 30):
					# print terms_sheet_pl_component_obj;
					top_Y = terms_sheet_pl_component_obj[6];


				if (terms_sheet_pl_component_obj[6] < centerpoint_coordinates_approximate[1]) and ('Text' not in terms_sheet_pl_component_obj[2])\
					and (terms_sheet_pl_component_obj[-2] > terms_sheet_pl_component_obj[-1]) and (terms_sheet_pl_component_obj[3] < 100) \
					and (abs(centerpoint_coordinates_approximate[1] - terms_sheet_pl_component_obj[6]) > 30):
					# print terms_sheet_pl_component_obj;
					bottom_Y = terms_sheet_pl_component_obj[6];
					break;

		print '';
		print 'The top border\'s Y value for the table is: ', top_Y;
		print '';
		print '';
		print 'The bottom border\'s Y value for the table is: ', bottom_Y;
		print '';

		max_X = 0;
		min_X = 1000;

		print '-----------------------------     ', len(terms_sheet_pl_component_list);

		for i in range(0, len(terms_sheet_pl_component_list)):
			terms_sheet_pl_component_obj = terms_sheet_pl_component_list[i];
			# print '';
			# print terms_sheet_pl_component_obj[7];
			# print '';
			if terms_sheet_pl_component_obj[0] == centerpoint_coordinates_approximate[2]:
				if (terms_sheet_pl_component_obj[6] <= top_Y) and (terms_sheet_pl_component_obj[6] >= bottom_Y) and ('Text' in terms_sheet_pl_component_obj[2]):
					
					# print '------------------------------------------------';
					# print terms_sheet_pl_component_obj[7];
					if terms_sheet_pl_component_obj[3] < min_X:
						min_X = terms_sheet_pl_component_obj[3];
					if terms_sheet_pl_component_obj[5] > max_X:
						max_X = terms_sheet_pl_component_obj[5];

		max_X = max_X + 1;
		min_X = min_X - 1;

		if min_X == 999:
			min_X = 70;

		if max_X == 1:
			max_X = 700;											             ### Caution: this is very fragile, this is obviously not robust
																		   		 ### But I just don't know how to do it in other ways	

		min_X = 70;
		max_X = 700;
		print '';
		print 'The left border\'s X value for the table is: ', min_X;
		print '';
		print '';
		print 'The right border\'s X value for the table is: ', max_X;
		print '';

		int_rate_approximate_condition_list = [[0,0,'V2016','Terms Sheet','',centerpoint_coordinates_approximate[2], min_X, bottom_Y, max_X, top_Y, True,True,True,'list',0,1,1,0,'','Top']];

		int_rate_approximate_condition_set = pd.DataFrame(int_rate_approximate_condition_list, columns = ['Doc_Pre_ID', 'Doc_Type_ID', 'Doc_Version', 'Field_Name', 'Search_String', 'Page_Num',\
						  'Minpoint_X','Minpoint_Y','Maxpoint_X','Maxpoint_Y',\
						  'Is_From_Table', 'Is_Horizontal', 'Is_Organized_In_Row', 'Result_Type', 'Minimum_Length', \
						  'Column_Number', 'Max_Column', 'Max_Row', 'Calcrt_ID', 'Relative_Pos']);
		return int_rate_approximate_condition_set;	
	return [];



def process_term_sheet(pdf_document, pl_component_list):


	# print '_____________________________________________________________WHIOA!!!!';
	# print len(detailed_component_list);

	sorted_pl_component_list = pl_component_list;
	start_page_number = 0;
	end_page_number = 0;

	for item in sorted_pl_component_list:
		# print item[7][0:10];
		if 'TERMS SHEET' == item[7][0:11]:
			# print item[0], item;
			start_page_number = item[0];

		if 'RISK FACTORS' == item[7][0:12]:
			# print item[0], item;
			end_page_number = item[0];

	print '';
	print '';
	print '  ------The start page number for the TERMS SHEET is: ', start_page_number;
	print '  ------The end page number for the TERMS SHEET is: ', end_page_number;
	print '';
	print '';

	terms_sheet_page_num_list = range(start_page_number,end_page_number);
	terms_sheet_pl_component_list = [];
	for i in range(0, len(sorted_pl_component_list)):
		if sorted_pl_component_list[i][0] in terms_sheet_page_num_list:
			terms_sheet_pl_component_list.append(sorted_pl_component_list[i]);
	print '';






	centerpoint_coordinates_initial = get_search_string_position(terms_sheet_pl_component_list, 'Initial Interest');
	centerpoint_coordinates_approximate = get_search_string_position(terms_sheet_pl_component_list, 'Approximate ');
	print '';
	print '------------------------';
	print centerpoint_coordinates_initial;
	print '';
	print centerpoint_coordinates_approximate;
	print '------------------------';
	print '';


	

	#######################################################################################################################
	#######################################################################################################################
	page_num_list_for_detail_component = [];
	if len(centerpoint_coordinates_initial) == 3:
		page_num_list_for_detail_component.append(centerpoint_coordinates_initial[2]);
	if len(centerpoint_coordinates_approximate) == 3:
		page_num_list_for_detail_component.append(centerpoint_coordinates_approximate[2]);
	
	page_num_list_for_detail_component = list(sorted(set(page_num_list_for_detail_component)));
	print '';
	
	des_int_rate_list = [];
	int_rate_initial_condition_set = search_intial_interest(centerpoint_coordinates_initial, terms_sheet_pl_component_list);
	initial_page_list_for_detailed = pdfminer_configuration(pdf_document, page_num_list_for_detail_component);
	detailed_component_list = split_string_detail_process(initial_page_list_for_detailed, page_num_list_for_detail_component);
		
	if len(int_rate_initial_condition_set) != 0:
	
		print '';
		print 'Initial Detailed List length: ', len(detailed_component_list);
		print '';


		[ranged_component_list, table_content_list, col_or_row_content_list, string_content_list] = search_field_by_condition(int_rate_initial_condition_set.iloc[0], sorted_pl_component_list, detailed_component_list, page_num_list_for_detail_component);
		

		print '';
		print 'Bordered Detailed List length: ', len(col_or_row_content_list);
		print '';



	
		for item in col_or_row_content_list:
			# print item[0];
			if len(item[0]) > 10 and ('..' in item[0].replace(' ','')):
				des_int_rate_list.append(item);


	#######################################################################################################################
	#######################################################################################################################
	int_rate_approximate_condition_set = search_approximate_interest(centerpoint_coordinates_approximate, terms_sheet_pl_component_list);

	if len(int_rate_approximate_condition_set) != 0:
		[ranged_component_list, table_content_list, col_or_row_content_list, string_content_list] = search_field_by_condition(int_rate_approximate_condition_set.iloc[0], sorted_pl_component_list, detailed_component_list, page_num_list_for_detail_component);		
		for item in col_or_row_content_list:
			# print item[0];
			if len(item[0]) > 6 and ('..' in item[0].replace(' ','')):
				des_int_rate_list.append(item);

	#######################################################################################################################
	#######################################################################################################################
	print '-------------------------------';
	regex_str_class = r'^[A-Z]{1,2}\.|[^A-Z][A-Z]{1,2}[^A-Z]|[A-Z]{1,2}$';
	regex_str_intrate = r'[^0-9][1-9]{0,1}[0-9]{1,}\.[0-9]{3,}[%]{1}|[^0-9][1-9]{0,1}[0-9]{1,}\.[0-9]{3,}$';
	regexed_des_int_rate_list = [];
	for item_obj in des_int_rate_list:
		intrate_start = 0;
		intrate_end = 0;
		item = item_obj[0];
		if 'or' not in item and (bool(re.search(regex_str_class,item))) and (bool(re.search(regex_str_intrate,item))):
			item = re.sub('\.+','.',item);
			# print item;
			class_start = re.search(regex_str_class,item).start();
			class_end = re.search(regex_str_class,item).end();
			intrate_start = re.search(regex_str_intrate,item).start();
			intrate_end = re.search(regex_str_intrate,item).end();

			if 'LIBOR' in item:
				if item.index('LIBOR') > intrate_start:
					# print '???????????????????????????????????';
					libor_start_pos = item.index('LIBOR');
					# print libor_start_pos;
					intrate_start = libor_start_pos + re.search(regex_str_intrate,item[libor_start_pos:]).start();
					intrate_end = libor_start_pos + re.search(regex_str_intrate,item[libor_start_pos:]).end();
				# print intrate_start, intrate_end;

			item_class = item[class_start:class_end];
			item_class = re.sub(r'[^A-Z]','',item_class);
			
			item_intrate = item[intrate_start:intrate_end];
			# print item_intrate;
			item_intrate = re.sub(r'[^0-9.]','',item_intrate);
		
			if item_intrate[0] == '.':
				item_intrate = item_intrate[1:];
			# print [item_class, item_intrate];
			regexed_des_int_rate_list.append([item_class, item_intrate, item_obj[1:]]);
			# print '-------------------------------';


	# for item in regexed_des_int_rate_list:
	# 	print item;

	return regexed_des_int_rate_list, start_page_number, end_page_number;