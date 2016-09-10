from cStringIO import StringIO;
from pdfminer.pdfdocument import PDFDocument;
from pdfminer.pdfpage import PDFPage;
from pdfminer.pdfpage import PDFTextExtractionNotAllowed;
from pdfminer.pdfinterp import PDFResourceManager;
from pdfminer.pdfinterp import PDFPageInterpreter;
from pdfminer.pdfdevice import PDFDevice;
from pdfminer.pdfparser import PDFParser;
from cStringIO import StringIO;
from pdfminer.converter import TextConverter;
from pdfminer.converter import PDFPageAggregator;
######################################################
from pdfminer.pdfparser import PDFSyntaxError;
from pdfminer.layout import *;
from binascii import b2a_hex;
from operator import itemgetter;

import time;
import csv;
import os;
import sys;
import glob;
import re;
import stopit;
from TestLog_Generator import *;


reload(sys);
sys.setdefaultencoding('utf-8');




######################################################
######################################################
############ Potential Approach 1#####################
############ can extract all the text content ########
def disp_proj_info():
	print '========================================================================';
	print '                    PDF Information Extraction Project                  ';
	print '                           Version 1.2.0                                ';
	print '                      Author:  Chang Liu (cliu462)                      ';
	current_time = time.asctime(time.localtime(time.time()));
	print '                  Date Time: ', current_time;
	current_file_dir = str(os.path.dirname(os.path.realpath(__file__)));
	print '       File Directory: ' +current_file_dir;
	print '                  The commandline output begins here:                   ';
	print '------------------------------------------------------------------------';
	print ' ';
	print '                The script is currently running, please wait:           ';
	print ' ';


def disp_proj_endding():
	print ' ';
	print '------------------------------------------------------------------------';
	print '                  The commandline output ends here                      ';
	print '                         The process finished.                          ';
	print '========================================================================';



def test_allobjs_page(layout):
	obj_list = list(layout._objs);
	return obj_list;




#####################################################################
def sort_pl_component_by_pos(component_list, sort_option):     							# this method will sort the component_list based on the position.
	if sort_option == 1:    
		sorted_component_list = sorted(component_list, key = lambda x: (x[0],-(x[6]),(x[3])));										    
	if sort_option == 2:
		sorted_component_list = sorted(component_list, key = lambda x: (x[0],-(x[7]),(x[4])));
	if sort_option == 3:
		sorted_component_list = sorted(component_list, key = lambda x: (x[0],(x[3]),(x[4])));
	if sort_option == 4:
		sorted_component_list = sorted(component_list, key = lambda x: (x[0],(x[5]),(x[4])));

	return sorted_component_list;										# I found that the components in a page object are originally 
											   							# sorted based on the component type. 
											   							# But since we want to know the exact line number and row number of a certain text field,
											   							# maybe we need to reorganize the component list.
											   							# Make it in the order of the position and indicate the line numbers.
#####################################################################


#####################################################################
def calc_width_and_height(component, type):
	
	if type == 'page_level_component':
		return [component[5] - component[3], component[6] - component[4]];
	if type == 'detailed_component':
		return [component[6] - component[4], component[7] - component[5]];



#####################################################################


#####################################################################
def is_ignorable_points_or_pageborderline(detailed_component):
	border_threshold_X_min = 40;
	border_threshold_X_max = 570;
	border_threshold_Y_max = 750;
	border_threshold_Y_min = 40;

	point_width_threshold = 1;
	point_height_threshold = 1;

	border_line_width_threshold = 550;
	border_line_height_threshold = 730;	
	if (('Text' not in detailed_component[2]) \
		and (detailed_component[-1] < point_height_threshold) \
		and (detailed_component[-2] < point_width_threshold)) \
	or (('Text' not in detailed_component[2]) \
		and ((detailed_component[-1] > border_line_height_threshold \
			and detailed_component[-2] < point_width_threshold) \
		or (detailed_component[-2] > border_line_width_threshold \
			and detailed_component[-1] < point_height_threshold))):
		return True;

#####################################################################



#######################################################################################
#######################################################################################
#######################################################################################
####################### Architech Redesign Attempt 1 ##################################
####################### Objective: Do modulazation for those methods above ############
# For this redesign, i will try to pull the sharing part of each methods above 
# Encapsulate the repeated part into a separate method and other methods will call 
# this method.


#######################################################################################
############ For optimize purpose: we separate this method

def opt_pdf_document(pdf_file_n):
	pdf_file_name = pdf_file_n;   # make the name different 
	pdf_file = open(pdf_file_name,'rb');
	pdf_parser = PDFParser(pdf_file);   # this is a pdf parser object 

	pdf_document = PDFDocument(pdf_parser);           # this is a pdf document object
											  # can have a second parameter, as password
											  # if the document doesn't have password, then just ignore it

	if not pdf_document.is_extractable:
		raise PDFTextExtractionNotAllowed;    # test whether the pdf allows text extraction	

	return pdf_document;

#######################################################################################





#######################################################################################
def pdfminer_configuration(pdf_document, page_num_list=None):
	
	pdf_resmg = PDFResourceManager();		  # create a resource manager object

	pdf_laparams = LAParams();    # this is the default layout 
	pdf_device_la = PDFPageAggregator(pdf_resmg, laparams = pdf_laparams);
	pdf_interpreter_la = PDFPageInterpreter(pdf_resmg, pdf_device_la);
	
	interpret_result_list = [];


	number_of_complex_pages = 0;

	if page_num_list == None:       ### if no page number list specified, then we do for all pages
		# print '==============================================';
		for pageid, page in enumerate(PDFPage.create_pages(pdf_document)): 
			# print '                                     rotate: ',page.rotate;
			sstart_time = time.time();
			with stopit.ThreadingTimeout(5) as to_ctx_mrg:
				assert to_ctx_mrg.state == to_ctx_mrg.EXECUTING
				pdf_interpreter_la.process_page(page);             							 
				# Something potentially very long but which
				layout = pdf_device_la.get_result();
				interpret_result_list.append(test_allobjs_page(layout));
			# OK, let's check what happened
			if to_ctx_mrg.state == to_ctx_mrg.EXECUTED:
				# All's fine, everything was executed within 10 seconds
				eend_time = time.time();
				print 'Page number: ', (pageid+1),'The processing time is:', eend_time - sstart_time;
				sstart_time = time.time();
				'''do nothing''';
			elif to_ctx_mrg.state == to_ctx_mrg.EXECUTING:
				# Hmm, that's not possible outside the block
				'''do nothing''';
			elif to_ctx_mrg.state == to_ctx_mrg.TIMED_OUT:
				# eend_time = time.time();
				# Eeek the 10 seconds timeout occurred while executing the block
				print '---------------------------------------------------------------------';
				print 'Page ', pageid+1, ' is too complex to analyze. The interpreting time exceeds 5 seconds. We skip this page.'; 
				number_of_complex_pages = number_of_complex_pages + 1;
				print '---------------------------------------------------------------------';
				
			elif to_ctx_mrg.state == to_ctx_mrg.INTERRUPTED:
				# Oh you raised specifically the TimeoutException in the block
				'''do nothing''';
			elif to_ctx_mrg.state == to_ctx_mrg.CANCELED:
				'''do nothing''';
			else:
				'''do nothing''';
			# print pageid+1;    
			# print '----------------------------------------------------------------------------'; 	
			last_page_obj = test_allobjs_page(layout)[-1];
			# print '';
			# print (pageid+1) , '    -------    ',str(last_page_obj);
			# print '';
			if isinstance(last_page_obj, LTText):
				# print len(str(last_page_obj.get_text())), str(last_page_obj.get_text()), pageid + 1;
				# if 'S-1' in str(last_page_obj.get_text()):
				# 	print str(last_page_obj.get_text()), pageid + 1;				

				if str(last_page_obj.get_text())[0:3]=='B-1' or number_of_complex_pages > 2:    # this is very fragile
					print str(last_page_obj.get_text()), pageid + 1;
					return interpret_result_list;
		return interpret_result_list;

	for pageid, page in enumerate(PDFPage.create_pages(pdf_document)):   ################ here we might specify the page number if needed
		# print '*************', pageid+1;
		if (pageid+1) in page_num_list:									 ################ The page number in the database starts from 1 while the numerator starts from 0
			pstart_time = time.time();
			pdf_interpreter_la.process_page(page);
			layout = pdf_device_la.get_result();
			interpret_result_list.append(test_allobjs_page(layout));     ################ call different methods2 to test		
			pend_time = time.time();
			print 'Page ', pageid+1, ' |Process time: ', (pend_time - pstart_time)/60.0;
			if (pageid+1) == page_num_list[-1]:
				break; 
	# print 'WTF??????????????????????????????????????';
	return interpret_result_list;
######################################################################################




######################################################################################
def split_analyze_LTTextLineHorizontal(LTTextLineHorizontal_obj):
	detailed_info_list = LTTextLineHorizontal_obj._objs;
	split_detailed_info_list = [];
	for item in detailed_info_list:
		if ('Anno' not in str(item)):
			split_raw_list = str(item).split(' ',6);
			temp_split_detail_obj = [];
			temp_split_detail_obj.append(split_raw_list[0][1:]);
			temp_split_detail_obj.append(float(split_raw_list[1].split(',',3)[0]));
			temp_split_detail_obj.append(float(split_raw_list[1].split(',',3)[1]));
			temp_split_detail_obj.append(float(split_raw_list[1].split(',',3)[2]));
			temp_split_detail_obj.append(float(split_raw_list[1].split(',',3)[3]));
			
			temp_split_detail_obj.append((split_raw_list[2] + split_raw_list[3])[7:]);
			temp_split_detail_obj.append(split_raw_list[4][6:-1]);
			temp_split_detail_obj.append(float(split_raw_list[5][4:]));

			temp_split_detail_obj.append(split_raw_list[6][7:-2]);
			temp_split_detail_obj.append(item.size);
			temp_split_detail_obj.append(item.upright);
			if item.matrix[0]-0 > 0.1 and item.matrix[3]-0 > 0.1:
				temp_split_detail_obj.append('Horizontal');
			if item.matrix[1]-0 > 0.1 and item.matrix[2]-0 < -0.1 :
				temp_split_detail_obj.append('Vertical');	

			split_detailed_info_list.append(temp_split_detail_obj);
		else:
			split_detailed_info_list.append(item);
		# print type(item);
	return split_detailed_info_list;

######################################################################################



######################################################################################
#### method that returns all the detailed components in a LTTextBoxHorizontal
def analyze_LTTextBoxHorizontal(LTTextBoxHorizontal_obj, option):
	detailed_info_list = [];
	temp_info_list = LTTextBoxHorizontal_obj._objs;
	if option == 'raw':
		for item in temp_info_list:
			detailed_info_list = detailed_info_list + raw_analyze_LTTextLineHorizontal(item);
	if option == 'split':
		for item in temp_info_list:
			detailed_info_list = detailed_info_list + split_analyze_LTTextLineHorizontal(item);		

	return detailed_info_list;
######################################################################################

#####################################################################
#####################################################################
##	Method: page_level_process									   ##
##  Now we want to combine the detailed information and the page   ## 
##  level components. Because it is obivously too redundant if we  ## 
##  use one entry for one character. For those characters in same  ##
##  text box, they all share same font same size. 				   ##
##  They might be different, but we don't care. We aren't copying  ##
##  an exact same pdf. We only care about the text content. The    ##
##  reason we want to know the font is only taking it as 		   ##
##  an attribute.                                                  ##
#####################################################################
#####################################################################



#####################################################################
##### this is another key method                                #####
#####################################################################
def decode_a_page_level_component(pl_component,page_num, component_index):
	component_detail_list = [];
	component_detail_list.append(page_num+1);
	component_detail_list.append(component_index+1);
	info_component = str(pl_component);
	info_component_list = info_component.split(' ',2);
	if '(' in info_component_list[0]:
		parenthesis_index = info_component_list[0].index('(');
		component_detail_list.append(info_component_list[0][1:parenthesis_index ]);
	else:
		component_detail_list.append(info_component_list[0][1:]);
	coordinates_info_list = info_component_list[1].split(',',3);
	component_detail_list.append(float(coordinates_info_list[0]));
	component_detail_list.append(float(coordinates_info_list[1]));
	component_detail_list.append(float(coordinates_info_list[2]));
	component_detail_list.append(float(coordinates_info_list[3][:-1]));
	if isinstance(pl_component, LTTextBoxHorizontal): 
		component_detail_list.append(info_component_list[2][2:-2]);
	else:
		component_detail_list.append('');

	if isinstance(pl_component,LTTextBoxHorizontal):
		textbox_obj_list = pl_component._objs;    # all textlines
		textline_obj_list = [];
		if len(textbox_obj_list) > 0:
			textline_obj_list = textbox_obj_list[0];  # all chars and annos
		
		textline_obj_list = [item for item in textline_obj_list if isinstance(item, LTChar)];    # all chars
		# print len(textline_obj_list);
		if len(textline_obj_list) > 0 :
			char_obj_list = str(textline_obj_list[0]).split(' ',6);			
			component_detail_list.append((char_obj_list[2] + char_obj_list[3])[7:]);
			component_detail_list.append(char_obj_list[4][6:-1]);
			component_detail_list.append(float(char_obj_list[5][4:]));
			component_detail_list.append(textline_obj_list[0].size);
			component_detail_list.append(textline_obj_list[0].upright);
			if textline_obj_list[0].matrix[0]-0 > 0.1 and textline_obj_list[0].matrix[3]-0 > 0.1:
				component_detail_list.append('Horizontal');
			if textline_obj_list[0].matrix[1]-0 > 0.1 and textline_obj_list[0].matrix[2]-0 < -0.1:
				component_detail_list.append('Vertical');				
	return component_detail_list;			

#######################################################################################
def get_search_string_position(pl_component_list, search_string):
	# print '*********************************************************';
	# print search_string;
	center_point_coordinates = [];
	newline_flag = 0;

	if '\\n' in search_string:
		for item in pl_component_list:
				item_str = item[7];
				item_str = item_str.replace(' ','');
				if search_string in item_str:
					center_point_coordinates.append((item[3] + item[5])/2);
					center_point_coordinates.append(item[6]);
					newline_flag = 1;
					break;

	if newline_flag == 1:
		return center_point_coordinates;


	
	for item in pl_component_list:
		item_str = item[7];
		item_str = item_str.replace('\r\n','');
		item_str = item_str.replace("\\n",' ');
		item_str = re.sub(' +',' ',item_str);      ### this is very important!
		if search_string in item_str:
			center_point_coordinates.append((item[3] + item[5])/2);
			center_point_coordinates.append(item[6]);
			center_point_coordinates.append(item[0]);
			break;
	return center_point_coordinates;

#######################################################################################

#######################################################################################
def decide_process_option(table_signal, direction_signal, row_signal, result_type):
	if table_signal and direction_signal and row_signal and result_type == 'list':
		return 'hor_tab_row_list';



#######################################################################################



#######################################################################################
def border_detect_move_top(component_list, pl_component_list, start_center_point_coordinates, distance_moving_offset, page_num):
	start_pos_X = start_center_point_coordinates[0];
	start_pos_Y = start_center_point_coordinates[1];
	border_range_max_Y = 0.0;	
	border_range_min_Y = 0.0;
	border_range_max_X = 0.0;
	border_range_min_X = 0.0;



	print start_pos_X;
	print start_pos_Y;
	print len(component_list);


	axis_X = start_pos_X;
	axis_Y = start_pos_Y;

	##############################################################################
	######## Figure out the top border
	##############################################################################
	print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~';
	while axis_Y > 0:
		break_flag = 0;
		for i in range(0, len(pl_component_list)):
			temp_component_type = pl_component_list[i][2] ;
			# print temp_component_type;
			temp_min_X = pl_component_list[i][3];
			temp_min_Y = pl_component_list[i][4];
			temp_max_X = pl_component_list[i][5];
			temp_max_Y = pl_component_list[i][6];
			pl_page_num = pl_component_list[i][0];
			if (temp_min_X <= start_pos_X) and (temp_max_X >= start_pos_X) and (temp_max_Y < start_pos_Y) and ('LTLine' in temp_component_type or 'LTRect' in temp_component_type) and (pl_page_num == page_num):
				# print pl_component_list[i];
				break_flag = 1;
				border_range_max_Y = temp_min_Y;
				break;
		if break_flag != 0:
			break;
		axis_Y = axis_Y - distance_moving_offset; 
		print axis_Y;
	print '====================== border range max Y: ' + str(border_range_max_Y) ;

	axis_Y = border_range_max_Y;                 # now starts from the top border of the box




	##############################################################################
	######## Figure out the bottom border
	##############################################################################
	potential_row_item_list = [];
	for i in range(0, len(pl_component_list)):
		temp_component_type = pl_component_list[i][2] ;
		# print temp_component_type;
		temp_min_X = pl_component_list[i][3];
		temp_min_Y = pl_component_list[i][4];
		temp_max_X = pl_component_list[i][5];
		temp_max_Y = pl_component_list[i][6];
		pl_page_num = pl_component_list[i][0];
		if (temp_min_X <= start_pos_X) and (temp_max_X >= start_pos_X) and (temp_min_Y < border_range_max_Y) and ('Text' in temp_component_type) and (pl_page_num == page_num):
			potential_row_item_list.append(pl_component_list[i]);
	

	# potential_row_item_list = sorted(potential_row_item_list, key = lambda x:(-x[6]));

	axis_Y = axis_Y - distance_moving_offset; 
	last_width = potential_row_item_list[0][-2];
	bottom_border_detect_flag = 0;

	# print start_pos_Y;
	# print 'Lower Border Detection --------------------------------------------------------------';
	for i in  range(0, len(potential_row_item_list)):
		item = potential_row_item_list[i];
		# print 'FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCK!';
		# print item[7];
		if (item[-2] - last_width) > 200:
			border_range_min_Y = item[6];
			bottom_border_detect_flag = 1;
			break;
		else:
			last_width = item[-2];
	if bottom_border_detect_flag == 0:
		border_range_min_Y = potential_row_item_list[-1][4];

	print '====================== border range min Y: ' + str(border_range_min_Y) ;



	##############################################################################
	######## Figure out the left border
	##############################################################################
	while axis_X > 0:
		character_number = 0;
		for i in range(0, len(pl_component_list)):
			temp_component_type = pl_component_list[i][2];
			# print temp_component_type;
			temp_min_X = pl_component_list[i][3];
			temp_min_Y = pl_component_list[i][4];
			temp_max_X = pl_component_list[i][5];
			temp_max_Y = pl_component_list[i][6];
			pl_page_num = pl_component_list[i][0];
			if (temp_min_X <= axis_X) and (temp_max_X >= axis_X) and (temp_min_Y < border_range_max_Y) and (temp_min_Y > border_range_min_Y) and ('Text' in temp_component_type) and (pl_page_num == page_num):
				character_number = character_number + 1;
				# print pl_component_list[i][7];

		# print '-------------------------------- ' + str(character_number);
		


		if character_number == 0:
			border_range_min_X = axis_X;
			break;


		vertical_line_flag = 0;
		for item in pl_component_list:
			if (('Line' in item[2]) or ('Rect' in item[2])) and (item[-1] > item[-2])  and ( (item[3] >= axis_X) and (item[3] <= axis_X+distance_moving_offset)):
				vertical_line_flag = 1;

		if vertical_line_flag == 1:
			border_range_min_X = axis_X + distance_moving_offset;
			break;	



		axis_X = axis_X - distance_moving_offset; 

	print '====================== border range min X: ' + str(border_range_min_X) ;	







	##############################################################################
	######## Figure out the right border
	##############################################################################
	axis_X = start_pos_X;
	while axis_X < 842:
		character_number = 0;
		for i in range(0, len(pl_component_list)):
			temp_component_type = pl_component_list[i][2];
			# print temp_component_type;
			temp_min_X = pl_component_list[i][3];
			temp_min_Y = pl_component_list[i][4];
			temp_max_X = pl_component_list[i][5];
			temp_max_Y = pl_component_list[i][6];
			pl_page_num = pl_component_list[i][0];
			if (temp_min_X <= axis_X) and (temp_max_X >= axis_X) and (temp_min_Y < border_range_max_Y) and (temp_min_Y > border_range_min_Y) and ('Text' in temp_component_type) and (pl_page_num == page_num):
				character_number = character_number + 1;
		# print '-------------------------------- ' + str(character_number);
		if character_number == 0:
			border_range_max_X = axis_X;
			break;

		vertical_line_flag = 0;
		for item in pl_component_list:
			if (('Line' in item[2])  or ('Rect' in item[2])) and (item[-1] > item[-2])  and ( (item[5] <= axis_X) and (item[5] >= axis_X - distance_moving_offset)):
				vertical_line_flag = 1;

		if vertical_line_flag == 1:
			border_range_max_X = axis_X - distance_moving_offset;
			break;	

	
		axis_X = axis_X + distance_moving_offset; 

	print '====================== border range max X: ' + str(border_range_max_X) ;	
	return [border_range_min_X, border_range_min_Y, border_range_max_X, border_range_max_Y];

#######################################################################################



#######################################################################################
def border_detect_move(component_list, pl_component_list, detection_option, relative_pos, distance_moving_offset, start_center_point_coordinates, page_num):
	move_flag = 0;
	if move_flag == 0 and detection_option == 'hor_tab_row_list' and relative_pos == 'Top':
		return border_detect_move_top(component_list,pl_component_list, start_center_point_coordinates, distance_moving_offset, page_num);

#######################################################################################



#######################################################################################
def border_detect_by_search_string(start_center_point_coordinates, condition_set, component_list, pl_component_list):
	distance_moving_offset = 1;
	table_signal = condition_set['Is_From_Table'];
	direction_signal = condition_set['Is_Horizontal'];
	row_signal = condition_set['Is_Organized_In_Row'];
	result_type = condition_set['Result_Type'];
	page_num = condition_set['Page_Num'];
	detection_option = decide_process_option(table_signal, direction_signal, row_signal, result_type);
	# print detection_option;
	print '===================== Decide Border Here ========================'; 
	return border_detect_move(component_list, pl_component_list, detection_option, condition_set['Relative_Pos'], distance_moving_offset, start_center_point_coordinates, page_num);







#######################################################################################

#####################################################################
#####################################################################
##	Method: page_level_process									   ##
##  Now we want to combine the detailed information and the page   ## 
##  level components. Because it is obivously too redundant if we  ## 
##  use one entry for one character. For those characters in same  ##
##  text box, they all share same font same size. 				   ##
##  They might be different, but we don't care. We aren't copying  ##
##  an exact same pdf. We only care about the text content. The    ##
##  reason we want to know the font is only taking it as 		   ##
##  an attribute.                                                  ##
#####################################################################
#####################################################################



#######################################################################################
def page_level_process(initial_page_list):
	pl_component_list = [];
	for i in range(0, len(initial_page_list)):
		for j in range(0,len(initial_page_list[i])):
			component_detail_list = decode_a_page_level_component(initial_page_list[i][j],i,j);
			component_detail_list = component_detail_list;
			pl_component_list.append(component_detail_list);

	sorted_pl_component_list = sort_pl_component_by_pos(pl_component_list,1);
	# print '================================================================';
	# for item in sorted_pl_component_list:
	# 	print item;

	for i in range(0,len(sorted_pl_component_list)):
		if 'Text' not in sorted_pl_component_list[i][2]:    											# indicating it is not a LTChar
			sorted_pl_component_list[i] = sorted_pl_component_list[i]  + ['','','','','',''];
			sorted_pl_component_list[i]  = sorted_pl_component_list[i]  + calc_width_and_height(sorted_pl_component_list[i] ,'page_level_component');
		else:
			sorted_pl_component_list[i]  = sorted_pl_component_list[i]  + calc_width_and_height(sorted_pl_component_list[i] ,'page_level_component');

		# pl_csv_writer.writerow(sorted_pl_component_list[i]);

	return sorted_pl_component_list;	
#######################################################################################

#######################################################################################
def split_string_detail_process(initial_page_list, page_num_list):
	# initial_page_list = pdfminer_configuration(pdf_file_name, page_num_list);
	split_component_list = [];
	for i in range(0, len(initial_page_list)): 
		# print '-----------------------   ',i;
		for j in range(0,len(initial_page_list[i])):
			# print j; 
			process_flag = 0;
			

			if (process_flag == 0) and ('LTTextBoxHorizontal' in str(type(initial_page_list[i][j]))):
				process_flag = 1;
				temp_detailed_component_list = analyze_LTTextBoxHorizontal(initial_page_list[i][j],'split');
				for item in temp_detailed_component_list:
					detailed_object = [];
					detailed_object.append(page_num_list[i]);
					detailed_object.append(j+1);
					detailed_object.append(str(initial_page_list[i][j]).split(' ',1)[0][1:]);
					if not isinstance(item,LTAnno):
						detailed_object = detailed_object + item;
					else:
						detailed_object.append(str(item).split(' ',1)[0][1:]);
						detailed_object = detailed_object + [split_component_list[-1][4],split_component_list[-1][5],split_component_list[-1][6],split_component_list[-1][7],'','',''];
						detailed_object.append(str(item).split(' ',1)[1][:-1]);
					split_component_list.append(detailed_object);
					# split_csv_writer.writerow(detailed_object);
			if process_flag == 0:
				detailed_object = [];
				detailed_object.append(i+1);
				detailed_object.append(j+1);
				temp_raw_info_list = str(initial_page_list[i][j]).split(' ',2);
				detailed_object.append(temp_raw_info_list[0][1:]);
				detailed_object.append('');
				detailed_object.append(float(temp_raw_info_list[1].split(',',3)[0]));
				detailed_object.append(float(temp_raw_info_list[1].split(',',3)[1]));
				detailed_object.append(float(temp_raw_info_list[1].split(',',3)[2]));
				detailed_object.append(float(temp_raw_info_list[1].split(',',3)[3][:-1]));	
				split_component_list.append(detailed_object);											
	sorted_split_component_list = sort_pl_component_by_pos(split_component_list,2);



	for i in range(0,len(sorted_split_component_list)):
		if sorted_split_component_list[i][3] == 'LTAnno':    											# indicating it is not a LTChar
			sorted_split_component_list[i] = sorted_split_component_list[i] + ['','',''];
			sorted_split_component_list[i] = sorted_split_component_list[i] + calc_width_and_height(sorted_split_component_list[i],'detailed_component');
		elif sorted_split_component_list[i][3] == 'LTChar':
			sorted_split_component_list[i] = sorted_split_component_list[i] + calc_width_and_height(sorted_split_component_list[i],'detailed_component');
		else:
			sorted_split_component_list[i] = sorted_split_component_list[i] + ['','','','','','',''];
			sorted_split_component_list[i] = sorted_split_component_list[i] + calc_width_and_height(sorted_split_component_list[i],'detailed_component');
		# split_csv_writer.writerow(sorted_split_component_list[i]);

	# test_method_1_detect_table(sorted_split_component_list);

	return sorted_split_component_list;
######################################################################################


######################################################################################
###  method detailed_str_modify()												   ###
###  this method is used for mofifying a detailed string of a field                ###
###  e.g. we have ',' in the class balance fields' values, we need to eliminate it ###
###  		we have '(1)' in the Tranche list, we need to eliminate it             ###
###       we need to deal with '(5)' in the interest rate column, so we need       ###
### 				more logic to get the real value for it.                       ###
###  all those extra logics will be here and get processed by the option name      ###
###  the option name is the Field_Name in the predefined table Doc_Pre             ###
######################################################################################
######################################################################################
def detailed_str_modify(original_list, option):

	modified_list = [];
	if option == 'Tranche':
		for item in original_list:
			flag = 0;
			# print item[0];
			item[0] = item[0].replace('\r\n','');
			item[0] = item[0].replace("'",'');
			item[0] = item[0].replace("\\n",' ');
			item[0] = item[0].replace('$ ','');
			item[0] = item[0].replace(' ','');

			# print item[0];

			if '...' in item[0]:
				'''do nothing'''
				flag = 1;

			if '(' in item[0]:
				index_parenthsis = item[0].index('(');
				item[0] = item[0][0:index_parenthsis];
			
			item[0] = item[0].replace(' ','');
			if len(item[0]) > 3 or len(item[0]) == 0:
				'''do nothing'''
				flag = 1;
			item[0] = re.sub(' +',' ', item[0]);
			if(flag == 0):
				modified_list.append(item);
		return modified_list;

	if option == 'Class Balance' or option == 'Descriptors' or option == 'Descriptors_IntType':
		for item in original_list:
			item[0] = item[0].replace(',','');
			item[0] = item[0].replace('\\n','');
			item[0] = item[0].replace("'",'');
			item[0] = item[0].replace('$','');
			item[0] = item[0].replace(' ','');
			item[0] = re.sub(' +',' ', item[0]);
			if len(item[0]) > 0 and item[0]!=' ':
				modified_list.append(item);
		return modified_list;		
	

	if option == 'Cusip':
		for item in original_list:
			item[0] = item[0].replace("'",'');
			item[0] = item[0].replace("\\n",'');
			item[0] = item[0].replace('\r\n', '');
			# print item[0];
			item[0] = re.sub(' +',' ', item[0]);
			if len(item[0]) > 0 and item[0]!=' ':
				modified_list.append(item);
		return modified_list;	


	if option == 'Maturity':
		for item in original_list:
			item[0] = item[0].replace(',','');
			item[0] = item[0].replace('\\n','');
			item[0] = item[0].replace("'",'');
			item[0] = item[0].replace('$','');
			item[0] = re.sub(' +',' ', item[0]);
			if len(item[0]) > 0 and item[0]!=' ':
				modified_list.append(item);
		return modified_list;		
	
	if option == 'Class Coupon':
		for item in original_list:
			item[0] = item[0].replace(',','');
			item[0] = item[0].replace('\\n','');
			item[0] = item[0].replace("'",'');
			item[0] = item[0].replace('$','');
			item[0] = item[0].replace('%','');
			item[0] = re.sub(' +',' ', item[0]);
			if len(item[0]) > 0 and item[0]!=' ':
				modified_list.append(item);
		return modified_list;		
	
	if option == 'Terms Sheet':
		# print 'Term Shit!!!!!!!!!!!!!!!!!!!!!!!';
		for item in original_list:
			# print '---------------';
			# print item[0];
			# print '---------------';
			item[0] = item[0].replace("'",'');
			item[0] = item[0].replace(' ','');
			item[0] = item[0].replace('\\n','');
			if len(item[0]) > 0 and item[0]!=' ':
				# print item[0];
				modified_list.append(item);
		return modified_list;		



	for item in original_list:
		item[0] = item[0].replace(',','');
		item[0] = item[0].replace('\\n','');
		item[0] = item[0].replace("'",'');
		item[0] = item[0].replace('$','');
		
		item[0] = re.sub(' +',' ', item[0]);
		if len(item[0]) > 0 and item[0]!=' ':
			modified_list.append(item);
	return modified_list;		






######################################################################################






#####################################################################
#####################################################################
##	Core Method: search_field_by_condition(condition_set)		   ##
##  We read in the xtr.Doc_pre table 							   ##
## 	Each data entry in that table will represent a detailed 	   ##
##  condition that required to search a certain  field's 		   ##
##  Information   												   ##
#####################################################################
#####################################################################

def search_field_by_condition(condition_set, pl_component_list, component_list, page_num_list, level_option='detailed'):
	temp_condition_set = condition_set;	
	# print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^';
	# print tem
	# print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^';
	page_num = temp_condition_set['Page_Num'];
	minpoint_X = temp_condition_set['Minpoint_X'];
	minpoint_Y = temp_condition_set['Minpoint_Y'];
	maxpoint_X = temp_condition_set['Maxpoint_X'];
	maxpoint_Y = temp_condition_set['Maxpoint_Y'];

	ranged_component_list = [];                   									# we will return all these four lists
	table_content_list = [];														# but what is the exact list we want?
	col_or_row_content_list = [];													# that's the reason I predefined a column in the database called 'Result_Type'
	string_content_list = [];														# for example, if the 'Result_Type' is a 'list', I should know the result is in col_or_row_content_list
																					# which is the 3rd return variable
																					# if the 'Result_Type' is a 'string', I should know the result is in string_content_list
																					# which is the 4th return variable
																					# the example of using 'drawer'

	if level_option == 'detailed':
		for i in range(0, len(component_list)):
			item = component_list[i];
			# print '----------------------';
			# print item[0] == page_num; #'* *', item[4] >= minpoint_X,'* *', item[5] >= minpoint_Y,'* *', item[6] <= maxpoint_X, '* *',item[7] <= maxpoint_Y;
			# print '----------------------';
			if (item[0] == page_num) and (item[4] >= minpoint_X) and (item[5] >= minpoint_Y) and (item[6] <= maxpoint_X) and (item[7] <= maxpoint_Y):
				ranged_component_list.append(item);

			#####################################################################
			############# Here we can improve the efficiency 
			# if (item[0] == page_num) and (component_list[i+1][0] != page_num):                           
			# 	break;
			#####################################################################

	if condition_set['Is_From_Table'] and condition_set['Is_Horizontal'] and condition_set['Is_Organized_In_Row']:		         # judge the conditions	
		# print 'HEHEHEHEHEHEH';
		org_row_list = organize_by_row(ranged_component_list, condition_set['Minimum_Length'], condition_set['Max_Column'], condition_set['Page_Num']);
		column_value_list = fetch_column(org_row_list, condition_set['Column_Number']-1);
		col_or_row_content_list = column_value_list;	


	if (condition_set['Minpoint_X'] == 0.0) and (condition_set['Minpoint_Y'] == 0.0) and (condition_set['Maxpoint_X'] == 0.0) and (condition_set['Maxpoint_Y'] == 0.0) and (not condition_set['Is_From_Table']) and (condition_set['Result_Type'] == 'string') :
		for i in range(0, len(pl_component_list)):
			item = pl_component_list[i];
			# print '---------------------------';
			# print item[7];
			item[7] = re.sub(' +',' ',item[7]);
			# print item[7];
			# print item[7], len(item[7]), condition_set['Search_String'], len(condition_set['Search_String']);
			# print (condition_set['Search_String'] in item[7]), int(condition_set['Page_Num']) == page_num_list[int(item[0])-1];
			if (condition_set['Search_String'] in item[7]) and int(condition_set['Page_Num']) == page_num_list[int(item[0])-1]:
				search_string_start_pos = item[7].index(condition_set['Search_String']);
				item[7] = item[7].replace('\\n','|');
				search_content = item[7][search_string_start_pos+len(condition_set['Search_String'])-1:];
				# print item[7][search_string_start_pos : search_string_start_pos+len(condition_set['Search_String'])-1];
				search_content = search_content.replace(':','');

				# print '-----';
				# print search_content;
				if search_content.replace('|','') == ' ' or search_content.replace('|','') == '' or bool(re.search(r'^ +$', search_content.replace('|',''))):
					# print '                                WOCAO!';
					# print search_content;
					search_content = pl_component_list[i+1][7];
					# print '----------------------';
					# print search_content;
					search_content = re.sub(' +',' ',search_content).replace('\\n',' ');


				# print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&';
				# print len(search_content);
				# print search_content;
				# print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&';
				print search_content;
				if condition_set['Search_String'] == 'Distribution Date':
					search_content = search_content[2:];
					search_content = search_content.replace('|', ' ');
					print '$$$@#@#@#@#@#@#@';
					print search_content;

				if search_content[0] == ' ':
					search_content = search_content[1:];

				line_number_percentage = 0.0;
				line_number_percentage = round(((842.0 - (item[3] + item[5])/2.0) / 842.0), 3) * 100;
				line_number_percentage = str(line_number_percentage) + '%';
				
				string_content_obj = [];
				search_content = search_content.split('|')[0];
				string_content_obj.append(search_content);
				string_content_obj.append(int(condition_set['Page_Num']));
				string_content_obj.append(line_number_percentage);
				string_content_obj.append(item[3]);
				string_content_obj.append(item[4]);
				string_content_obj.append(item[5]);
				string_content_obj.append(item[6]);
				string_content_obj.append(item[8]);
				string_content_obj.append(item[9]);
				string_content_obj.append(item[10]);
				string_content_obj.append(item[11]);
				string_content_obj.append(item[12]);
				string_content_obj.append(item[13]);
				string_content_list.append(string_content_obj);
				break;



			# row_org_list.append([temp_row_str, temp_row_item[index_start][0], temp_row_item[index_start][4], temp_row_item[index_start][5], temp_row_item[index_end][6], temp_row_item[index_end][7], temp_row_item[index_start][9]\
			# 	, temp_row_item[index_start][10], temp_row_item[index_start][12], temp_row_item[index_start][13], temp_row_item[index_start][14]]);        
			# 																																  # I take the first component's minpoint as the minpoint
			# 																																  # the last component's maxpoint as the maxpoint															
						
	####################################
	## Process further modification here
	####################################	
	col_or_row_content_list = detailed_str_modify(col_or_row_content_list, temp_condition_set['Field_Name']);
	return ranged_component_list, table_content_list, col_or_row_content_list, string_content_list;      # here we have 4 return variable (4 drawers)
######################################################################################


######################################################################################
def organize_by_row(component_list, minlength, max_col, page_num):
	# print minlength;
	row_org_list = [];
	temp_row_item = [];
	for i in range(0, len(component_list)):
		item = component_list[i];
		item_flag = 0;

		if (item_flag == 0) and (len(temp_row_item) == 0):
			temp_row_item.append(item);
			item_flag = 1;
		if (item_flag == 0) and (abs(item[5] - temp_row_item[-1][5]) < 0.01 and abs(item[7] - temp_row_item[-1][7]) < 0.01):
			temp_row_item.append(item);                                                        # since they are organized in row, so I will detect the X coordinates for minpoint and maxpoint
			item_flag = 1;																	   # if those characters share same X values for minpoint and maxpoint, i know they are in the same
																							   # line and should represent one data row entry		


		if ((item_flag == 0) and ((abs(item[5] - temp_row_item[-1][5]) > 0.01 or abs(item[7] - temp_row_item[-1][7]) > 0.01))) or\
		 ((abs(item[5] - temp_row_item[-1][5]) > 0.01 or abs(item[7] - temp_row_item[-1][7]) > 0.01) or (i == (len(component_list) - 1))):
			# print '=======================',i;
			# if i == (len(component_list) - 1):
			# 	print 'we are herererererereer!!!!!!';
			temp_row_str = '';
			for temp_str in temp_row_item:
				temp_row_str = temp_row_str + temp_str[11];

			index_start = 0;
			index_end = len(temp_row_item) - 1;
			for i in range(0, len(temp_row_item)):
				if temp_row_item[i][3] == 'LTChar':
					index_start = i;
					break;

			for i in range(len(temp_row_item)-1,-1,-1):
				if temp_row_item[i][3] == 'LTChar':
					index_end = i;
					break;

  			
			row_org_list.append([temp_row_str, temp_row_item[index_start][0], temp_row_item[index_start][4], temp_row_item[index_start][5], temp_row_item[index_end][6], temp_row_item[index_end][7], temp_row_item[index_start][9]\
				, temp_row_item[index_start][10], temp_row_item[index_start][12], temp_row_item[index_start][13], temp_row_item[index_start][14]]);        
																																			  # I take the first component's minpoint as the minpoint
																																			  # the last component's maxpoint as the maxpoint															
																																			  # very absolute
			temp_row_item = [];
			temp_row_item.append(item);
			item_flag = 1;

	# print 'row_org_list ' + str(len(row_org_list));
	row_org_list = [item for item in row_org_list if len(item[0]) > minlength];

	# print 'row_org_list ' + str(len(row_org_list));
	result_list = [];
	for item in row_org_list:
		# print '  ';
		temp_list = item[0].split(' ',max_col-1);
		temp_list.append(int(item[1]));

		line_number_percentage = 0.0;
		line_number_percentage = round(((842.0 - (item[3] + item[5])/2.0) / 842.0), 3) * 100;
		line_number_percentage = str(line_number_percentage) + '%';

		temp_list.append(page_num);
		temp_list.append(line_number_percentage);
		temp_list.append(item[2]);
		temp_list.append(item[3]);
		temp_list.append(item[4]);
		temp_list.append(item[5]);
		temp_list.append(item[6]);
		temp_list.append(item[7]);
		temp_list.append(item[8]);
		temp_list.append(item[9]);
		temp_list.append(item[10]);
		result_list.append(temp_list);
	return result_list;
######################################################################################

######################################################################################
def fetch_column(table_content_list, column_num):
	column_value_list = [];
	for item in table_content_list:
		column_value_list.append([item[column_num],int(item[-11]), item[-10], item[-9],item[-8], item[-7], item[-6], item[-5], item[-4], item[-3], item[-2], item[-1]]);

	return column_value_list;
######################################################################################


######################################################################################
def get_file_list_on_given_directory(directory_path):
	file_path = directory_path;
	file_list = glob.glob(directory_path);
	# print len(file_list);
	file_name_list = [];
	for item in file_list:
		file_name_list.append(item);
		# item.split('\\')[-1]
	return file_name_list;
######################################################################################



######################################################################################
def generate_mid_csv(pdf_file_name,component_list,column_title_list):

	csv_file_name = '';
	path_split_list = pdf_file_name.split('\\');
	for i in range(0, len(path_split_list)-1):
		csv_file_name = csv_file_name + path_split_list[i] + '\\';

	csv_file_name = csv_file_name + 'Mid_Csvs\\';
	csv_file_name = csv_file_name + path_split_list[-1][:-4] + '.csv';
	# print csv_file_name;
	output_result_csv = open(csv_file_name,'wb');
	csv_writer = csv.writer(output_result_csv);

	csv_writer.writerow(column_title_list);
	for item in component_list:
		csv_writer.writerow(item);




######################################################################################