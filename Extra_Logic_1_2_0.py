from PDF_Extractor_1_2_0 import *;
from TestLog_Generator import *;



reload(sys);
sys.setdefaultencoding('utf-8');
def reorganize_vertical_line_item(vertical_line_item):
	organized_vertical_line_item = [];
	pass_flag = 0;
	# print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~';
	# for item in vertical_line_item:
	# 	print item;
	# print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~';
	for i in range(0, len(vertical_line_item)):
		process_flag = 0;
		# print '----------------------';
		# print vertical_line_item[i];
		# print '----------------------';
		if (process_flag == 0) and (len(vertical_line_item[i]) == 0):
			process_flag = 1;

		if (process_flag == 0) and ('(' == vertical_line_item[i][0]) and ( len(vertical_line_item[i]) > 1) and (not bool(re.search(r'\([0-9]\)', vertical_line_item[i]))):
			organized_vertical_line_item[-1] = ''.join([organized_vertical_line_item[-1], vertical_line_item[i]]);
			process_flag = 1;

		if (process_flag == 0) and (pass_flag != 0) and (i == pass_flag):
			process_flag = 1;

		if (process_flag == 0) and (i == 0):
			organized_vertical_line_item.append(vertical_line_item[i]);
			process_flag = 1;
		if (process_flag == 0) and (i == 1):
			if bool(re.search(r'[A-Za-z]',vertical_line_item[i])):
				organized_vertical_line_item[0] = ''.join([organized_vertical_line_item[0], vertical_line_item[i]]);
				process_flag = 1;
		if (process_flag == 0) and (bool(re.search(r'^\([A-Za-z]+\)$', vertical_line_item[i]))):
			organized_vertical_line_item[-1] = ''.join([vertical_line_item[i-1],vertical_line_item[i]]);
			process_flag = 1;		
		if (process_flag == 0) and (bool(re.search(r'^[A-HJ-Za-z]$', vertical_line_item[i]))):
			organized_vertical_line_item.append(vertical_line_item[i]);
			organized_vertical_line_item[-1] = ''.join([vertical_line_item[i], vertical_line_item[i+1]]);
			process_flag = 1;
			pass_flag = i + 1;
		if (process_flag == 0) and (vertical_line_item[i].replace(' ','') == 'I') and ('PAC' in organized_vertical_line_item[-1]):
			organized_vertical_line_item[-1] = ''.join([organized_vertical_line_item[-1],' I']);
			process_flag = 1;

		if (process_flag == 0) and (vertical_line_item[i].replace(' ','') == 'I') and ('NV' in vertical_line_item[i+1]):
			organized_vertical_line_item.append(vertical_line_item[i]);
			organized_vertical_line_item[-1] = ''.join([vertical_line_item[i], vertical_line_item[i+1]]);
			process_flag = 1;
			pass_flag = i + 1;

		if (process_flag == 0) and (')' == vertical_line_item[i]):
			# print vertical_line_item[i];
			organized_vertical_line_item[-1] = ''.join([organized_vertical_line_item[-1], vertical_line_item[i]]);
			process_flag = 1;
		if (process_flag == 0) and ('I)' == vertical_line_item[i]):
			organized_vertical_line_item[-1] = ''.join([organized_vertical_line_item[-1], vertical_line_item[i]]);
			process_flag = 1;	
		if (process_flag == 0) and (bool(re.search(r'I[0-9]{1,}',vertical_line_item[i]))):
			# print 'a?';
			organized_vertical_line_item[-1] = ''.join([organized_vertical_line_item[-1], ' ', vertical_line_item[i].replace(' ','')[0]]);
			organized_vertical_line_item.append(vertical_line_item[i].replace(' ','')[1:]);
			process_flag = 1;	
		if (process_flag == 0) and ('(' == vertical_line_item[i]):
			# print vertical_line_item[i];
			organized_vertical_line_item[-1] = ''.join([organized_vertical_line_item[-1], vertical_line_item[i], vertical_line_item[i+1]]);
			process_flag = 1;
			pass_flag = i+1;
		if (process_flag == 0) and (i != len(vertical_line_item) - 1):
			organized_vertical_line_item.append(vertical_line_item[i]);
			process_flag = 1;
		if (process_flag == 0) and (i == len(vertical_line_item) - 1) and (bool(re.search(r'^\d{4}$', vertical_line_item[i]))):
			organized_vertical_line_item[-1] = ''.join([organized_vertical_line_item[-1],' ',vertical_line_item[i]]);
			process_flag = 1;


	for i in range(0, len(organized_vertical_line_item)):
		# print organized_vertical_line_item[i];
		# print '-------------------------';
		if 'PACI' in organized_vertical_line_item[i]:
			# print organized_vertical_line_item[i];
			end_pos = re.search(r'PAC', organized_vertical_line_item[i]).end();
			organized_vertical_line_item[i] = organized_vertical_line_item[i][:(end_pos)] + ' ' + organized_vertical_line_item[i][(end_pos):];

		if ('(' in organized_vertical_line_item[i]) and (i == 0):
			end_index = organized_vertical_line_item[i].index('(');
			organized_vertical_line_item[i] = organized_vertical_line_item[i][:end_index];						

	if len(organized_vertical_line_item) != 7:
		print '-------------------------------------------------------';
		print 'Something wrong on interpreting vertical tables.'
		print 'Program stops here.';
		print 'Detailed row information: ', organized_vertical_line_item; 
		print 'Number of items in this row list (should be 7): ', len(organized_vertical_line_item);
		print '-------------------------------------------------------';
		return [];
	else:
		print organized_vertical_line_item;

	return organized_vertical_line_item;



def extra_classes_final_process(result_component_list):
	Extra_Trenche_list = [];
	Extra_Class_Balance_list = [];
	Extra_Descriptor_list = [];
	Extra_Class_Coupon_list = [];
	Extra_Descriptor_Int_list = [];
	Extra_Cusip_list = [];
	Extra_Maturity_Date_list = [];
	for i in range(0, len(result_component_list)):
		for j in range(0, len(result_component_list[i][0])):
			if j==0:
				temp_extra_obj = [];
				temp_extra_obj.append(result_component_list[i][0][j]);
				temp_extra_obj = temp_extra_obj + result_component_list[i][1:];
				Extra_Trenche_list.append(temp_extra_obj);
			if j==1:
				temp_extra_obj = [];
				temp_extra_obj.append(result_component_list[i][0][j]);
				temp_extra_obj = temp_extra_obj + result_component_list[i][1:];
				Extra_Class_Balance_list.append(temp_extra_obj);
			if j==2:
				temp_extra_obj = [];
				temp_extra_obj.append(result_component_list[i][0][j]);
				temp_extra_obj = temp_extra_obj + result_component_list[i][1:];
				Extra_Descriptor_list.append(temp_extra_obj);
			if j==3:
				temp_extra_obj = [];
				temp_extra_obj.append(result_component_list[i][0][j]);
				temp_extra_obj = temp_extra_obj + result_component_list[i][1:];
				Extra_Class_Coupon_list.append(temp_extra_obj);
			if j==4:
				temp_extra_obj = [];
				temp_extra_obj.append(result_component_list[i][0][j]);
				temp_extra_obj = temp_extra_obj + result_component_list[i][1:];
				Extra_Descriptor_Int_list.append(temp_extra_obj);
			if j==5:
				temp_extra_obj = [];
				temp_extra_obj.append(result_component_list[i][0][j]);
				temp_extra_obj = temp_extra_obj + result_component_list[i][1:];
				Extra_Cusip_list.append(temp_extra_obj);
			if j==6:
				temp_extra_obj = [];
				temp_extra_obj.append(result_component_list[i][0][j]);
				temp_extra_obj = temp_extra_obj + result_component_list[i][1:];
				Extra_Maturity_Date_list.append(temp_extra_obj);

	final_extra_class_info_list = [Extra_Trenche_list, Extra_Class_Balance_list, Extra_Descriptor_list, Extra_Class_Coupon_list, Extra_Descriptor_Int_list, Extra_Cusip_list, Extra_Maturity_Date_list];

	return final_extra_class_info_list;









def process_vertical_content(file_name_full, pdf_document):
	# print len(initial_content_list);
	initial_content_list = pdfminer_configuration(pdf_document);
	result_component_list = [];
	string_component_list = [];
	for i in range(0, len(initial_content_list)):
		# print '                                                                              ----- Page Number: ', i+1;
		for j in range(0, len(initial_content_list[i])):
			temp_content_obj = initial_content_list[i][j];
			component_detail_list = decode_a_page_level_component(initial_content_list[i][j],i,j);
			if 'Text' not in component_detail_list[2]:
				component_detail_list = component_detail_list + ['','','','','',''];

			component_detail_list.append(component_detail_list[5] - component_detail_list[3]);
			component_detail_list.append(component_detail_list[6] - component_detail_list[4]);
			string_component_list.append(component_detail_list);


	column_title_list = ['Page_Num','Component_Index','Detail_Component_Type','Coor_Min_X','Coor_Min_Y','Coor_Max_X',\
	'Coor_Max_Y','Text','Matrix', 'Font', 'Adv(wid*fsize*scal)','FontSize(pt)','Upright(Bool)','Text_Direction','Box_Width','Box_Height'];
	sorted_string_component_list = 	sort_pl_component_by_pos(string_component_list,3);

	for i in range(0,len(sorted_string_component_list)):
		if sorted_string_component_list[i][-3] == 'Vertical':
			temp_str = sorted_string_component_list[i][7];
			temp_str = temp_str.replace('\\n','');
			temp_str = temp_str[::-1];
			sorted_string_component_list[i][7] = temp_str; 

	sorted_string_component_list = sort_pl_component_by_pos(sorted_string_component_list,4);
	# generate_mid_csv(file_name_full,sorted_string_component_list,column_title_list);


	string_info_list = [];
	for i in range(0, len(sorted_string_component_list)):
		# print sorted_string_component_list[i][7][0:8];
		if ('MXClass' in sorted_string_component_list[i][7] and sorted_string_component_list[i][-3] == 'Vertical') \
			or ('MX Class' in sorted_string_component_list[i][7] and sorted_string_component_list[i][-3] == 'Vertical'):
			# print '=================================================';
			# print sorted_string_component_list[i][0];
			# print sorted_string_component_list[i][5];
			# print sorted_string_component_list[i][4];
			start_pos_X = sorted_string_component_list[i][5];
			start_pos_Y = sorted_string_component_list[i][4];
			start_pos_Y = start_pos_Y - 5;
			detect_page_num = sorted_string_component_list[i][0];
			for j in range(0, len(sorted_string_component_list)):
				temp_vertical_pl_component = sorted_string_component_list[j];
				if ('LTLine' in temp_vertical_pl_component[2]) and (temp_vertical_pl_component[-2] < 0.5) and ( abs(temp_vertical_pl_component[-1]) >= 59) \
									and ( abs(temp_vertical_pl_component[-1]) <= 61) and (detect_page_num == temp_vertical_pl_component[0]) and (len(string_info_list) != 0) and (temp_vertical_pl_component[4] < 200):
					print temp_vertical_pl_component;
					break;

				if ( temp_vertical_pl_component[3] > start_pos_X ) and ( temp_vertical_pl_component[4] > start_pos_Y ) \
						and ('Text' in temp_vertical_pl_component[2]) and (detect_page_num == temp_vertical_pl_component[0]):
					if (len(temp_vertical_pl_component[7]) > 0) and (temp_vertical_pl_component[7].replace(' ','') != ''):
						string_info_list.append(temp_vertical_pl_component);


	print '-----------------------------------------------------------------------------------------------';
	print '-----------------------------------------------------------------------------------------------';
	print '-----------------------------------------------------------------------------------------------';
	# print len(string_info_list);
	# for item in string_info_list:
	# 	print item[3],item[4],item[5],item[6],item[7];
	if len(string_info_list) == 0:
		print 'No \'Available Combinations\' Information on this PDF and no extra classes returned.';
		return [[], initial_content_list];

	string_info_list = sort_pl_component_by_pos(string_info_list, 4);

	last_X = string_info_list[0][5];

	reorganized_vertical_content_list = [];
	reorganized_vertical_line = [];
	for i in range(0, len(string_info_list)):
		temp_vertical_pl_component = string_info_list[i];
		if (temp_vertical_pl_component[5] == last_X):
			reorganized_vertical_line.append(temp_vertical_pl_component);

		if (temp_vertical_pl_component[5] != last_X):
			reorganized_vertical_content_list.append(reorganized_vertical_line);
			last_X = temp_vertical_pl_component[5];
			reorganized_vertical_line = [];
			reorganized_vertical_line.append(temp_vertical_pl_component);

		if (i == len(string_info_list)-1):
			reorganized_vertical_content_list.append(reorganized_vertical_line);



	concatenate_string_list = [];

	for i in range(0, len(reorganized_vertical_content_list)):
		concatenate_string_line = [];
		temp_vertical_line = reorganized_vertical_content_list[i];
		concatenate_string = '';
		component_type = temp_vertical_line[0][2];
		minpoint_X = temp_vertical_line[0][3];
		minpoint_Y = temp_vertical_line[0][4];
		maxpoint_X = temp_vertical_line[-1][5];
		maxpoint_Y = temp_vertical_line[-1][6];
		matrix = temp_vertical_line[0][8];
		font = temp_vertical_line[0][9];
		adv = temp_vertical_line[0][10];
		fontsize = temp_vertical_line[0][11];
		upright = temp_vertical_line[0][12];
		test_direction = temp_vertical_line[0][13];
		box_width = maxpoint_X - minpoint_X;
		box_height = maxpoint_Y - minpoint_Y;

		for j in range(0, len(reorganized_vertical_content_list[i])):
			concatenate_string = concatenate_string + '   ' + reorganized_vertical_content_list[i][j][7];

		concatenate_string_line.append(temp_vertical_line[0][0]);
		concatenate_string_line.append(i+1);
		concatenate_string_line = concatenate_string_line + [component_type, minpoint_X, minpoint_Y, maxpoint_X, maxpoint_Y];
		concatenate_string_line.append(concatenate_string);
		concatenate_string_line = concatenate_string_line + [matrix,  font, adv, fontsize, upright, test_direction, box_width, box_height];
		concatenate_string_list.append(concatenate_string_line);

	# print '__________________________________________________________________';
	for item in concatenate_string_list:
		# print item[0:7], item[8:];
		temp_str  = item[7][3:];
		temp_str = temp_str.replace('$','');
		temp_str = temp_str.replace('%','');
		temp_str = temp_str.replace(',','');
		temp_str = re.sub(' +',' ',temp_str);
		line_number_percentage = 0.0;
		line_number_percentage = round(((842.0 - (item[4] + item[6])/2.0) / 842.0), 3) * 100;
		line_number_percentage = str(line_number_percentage) + '%';
		temp_str_list = temp_str.split(' ');
		if len(reorganize_vertical_line_item(temp_str_list)) != 0:
			# print reorganize_vertical_line_item(temp_str_list);
			result_component_list.append([reorganize_vertical_line_item(temp_str_list),item[0], line_number_percentage,item[3],item[4],item[5],item[6],item[9],item[10],item[11], item[12], item[13]]);

	# print '__________________________________________________________________';
	if len(result_component_list) != 0:
		final_extra_classes_info_list = extra_classes_final_process(result_component_list);	
	else:
		final_extra_classes_info_list = [];
	return [final_extra_classes_info_list, initial_content_list];

