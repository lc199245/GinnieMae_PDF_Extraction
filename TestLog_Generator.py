import xlsxwriter as xlw;
import time;

TEST_LOG_TITLE = ['TITLE', 'VALUE', 'DESCRIPTION'];
CURSOR_ROW = 0;
CURSOR_COLUMN = 0;
CURSOR_ROW_E = 10;
TEST_LOG_CONTENT_TABLE = [];
# format;


def create_xlsx_workbook(file_name):

	workbook = xlw.Workbook(file_name);
	# format = workbook.add_format();
	# format.set_text_wrap();
	return workbook;

def add_work_sheet(workbook, sheet_name):
	global CURSOR_COLUMN;
	global CURSOR_ROW;
	CURSOR_COLUMN = 0;
	CURSOR_ROW = 0;
	worksheet = workbook.add_worksheet(sheet_name);
	worksheet.set_column('A:A',30);
	worksheet.set_column('B:B',120);
	worksheet.set_column('C:C',60);
	worksheet.set_column('D:D',15);
	worksheet.set_column('E:E',20);
	worksheet.set_column('F:F',10);
	worksheet.set_column('G:G',20);
	worksheet.set_column('H:H',15);
	worksheet.set_column('I:I',20);
	worksheet.set_column('J:J',10);
	worksheet.set_column('K:K',30);
	worksheet.set_column('L:L',30);
	worksheet.set_column('M:M',30);
	worksheet.set_column('N:N',30);
	
	return worksheet;


def write_row_signal(workbook, worksheet, signal_string):
	global CURSOR_COLUMN;
	global CURSOR_ROW_E;
	CURSOR_COLUMN = 3;
	format = workbook.add_format();
	format.set_text_wrap();
	for item in signal_string:
		worksheet.write(CURSOR_ROW_E, CURSOR_COLUMN, item, format);
		CURSOR_COLUMN = CURSOR_COLUMN + 1;
	CURSOR_COLUMN = 0;	
	CURSOR_ROW_E = CURSOR_ROW_E + 1;
	return worksheet;	





def write_row(workbook, worksheet, row_list):
	global CURSOR_COLUMN;
	global CURSOR_ROW;
	format = workbook.add_format();
	format.set_text_wrap();
	for item in row_list:
		worksheet.write(CURSOR_ROW, CURSOR_COLUMN, item, format);
		CURSOR_COLUMN = CURSOR_COLUMN + 1;
	CURSOR_ROW = CURSOR_ROW + 1;
	CURSOR_COLUMN = 0;	
	return worksheet;


def write_column(workbook, worksheet, column_list):
	global CURSOR_COLUMN;
	global CURSOR_ROW;
	format = workbook.add_format();
	format.set_text_wrap();
	for item in column_list:
		worksheet.write(CURSOR_ROW, CURSOR_COLUMN, item, format);
		CURSOR_ROW = CURSOR_ROW + 1;
	CURSOR_ROW = CURSOR_ROW + 1;	
	return worksheet;

def write_table(workbook, worksheet, table_content_list):
	global CURSOR_COLUMN;
	global CURSOR_ROW;
	start_col = CURSOR_COLUMN;
	start_row = CURSOR_ROW;
	format = workbook.add_format();
	format.set_text_wrap();
	for row_item in table_content_list:
		for column_item in row_item: 
			worksheet.write(CURSOR_ROW, CURSOR_COLUMN, column_item, format);
			CURSOR_COLUMN = CURSOR_COLUMN + 1;
		CURSOR_ROW = CURSOR_ROW + 1;
		CURSOR_COLUMN = start_col;	
	return worksheet;	


def ask_user_info():
	user_name = raw_input('Please enter your name: ');
	print '';
	global TEST_LOG_CONTENT_TABLE;
	TEST_LOG_CONTENT_TABLE.append(['Tester Name',user_name]);
	time_tag = time.strftime("%Y_%m_%d_%H%M%S");
	time_tag_log = time.strftime("%Y/%m/%d %H:%M");
	TEST_LOG_CONTENT_TABLE.append(['Test Time Tag', time_tag_log]);
	file_name = '.\TestLogs\GinnieMae_TestLog_' + user_name + '_' + str(time_tag) + '.xlsx';
	file_name = file_name.replace(' ','');
	return file_name;

def disp_bbox_header():	
	print '=========================================================================================';
	print '-----------------------------------------------------------------------------------------';
	print '-------------------------------------- Welcome! -----------------------------------------';
	print '-------------------------------- PDF Extraction Program ---------------------------------';
	print '';
	test_log_file_name = ask_user_info();
	print '---------------------------------Your Test Log\'s Name: ---------------------------------';
	print '';
	print test_log_file_name;
	print '';
	print '-----------------------------------------------------------------------------------------';
	print '=========================================================================================';
	print '';
	print '';
	print '';
	print '';
	return test_log_file_name;

def test_log_generator_config():
	test_log_file_name = disp_bbox_header();
	return test_log_file_name;

