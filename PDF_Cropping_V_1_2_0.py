from PyPDF2 import PdfFileWriter, PdfFileReader
import PythonMagick;
from DB_Controller_1_2_0 import *;
from PIL import Image;
from PIL import ImageDraw;
import PIL;
from PIL import ImageFont;
import os;

doc_id = 0;

img_density = 250;

resize_ratio = [1.0,1.0];

pdf_page_size = [612,792];

pdf_page_img_size = [0,0];

def cut_length(dictionary, key, factor):
    cut_factor = 1-factor;
    cut = float(dictionary[key])*cut_factor;
    cut = cut / 4;
    return cut;

def new_coords(dictionary, key, cut, margin, code = "tl"):
    if code == "tl":
        if key == "x":
            return abs(float(dictionary[key])+(cut+margin["l"]));
        else:
            return abs(float(dictionary[key])-(cut+margin["t"]));
    elif code == "tr":
        if key == "x":
            return abs(float(dictionary[key])-(cut+margin["r"]));
        else:
            return abs(float(dictionary[key])-(cut+margin["t"]));
    elif code == "bl":
        if key == "x":
            return abs(float(dictionary[key])+(cut+margin["l"]));
        else:
            return abs(float(dictionary[key])+(cut+margin["b"]));
    else:
        if key == "x":
            return abs(float(dictionary[key])-(cut+margin["r"]));
        else:
            return abs(float(dictionary[key])+(cut+margin["b"]));


def db_query_doc_id(file_name_full):
    file_name = file_name_full.split('\\')[-1];
    # print file_name;
    sql_query_doc_id = 'SELECT * FROM [xtr].[Doc_PDF] WHERE [PDF_File_Name] = \'' + file_name + '\';'; 
    # print sql_query_doc_id;
    doc_id_df = execute_pure_query_to_pddf(sql_query_doc_id);
    # print doc_id.iloc[0]['Doc_ID'];
    global doc_id;
    doc_id = doc_id_df.iloc[0]['Doc_ID'];
    return doc_id;

def pdf_page_crop(file_name_full, page_number_rotation_list, db_connection=None):
    input_file = file_name_full;
    margin = {"l": 0, "t": 0, "r": 0, "b": 0};    
    input1 = PdfFileReader(file(input_file,'rb'));
    factor = 1;
    print 'file_name for query:';
    db_query_doc_id(file_name_full);
    print '-------------------------';

    pages = input1.getNumPages();
    print pages;
    top_right = {'x': input1.getPage(1).mediaBox.getUpperRight_x(), 'y': input1.getPage(1).mediaBox.getUpperRight_y()};
    top_left = {'x': input1.getPage(1).mediaBox.getUpperLeft_x(), 'y': input1.getPage(1).mediaBox.getUpperLeft_y()};
    bottom_right = {'x': input1.getPage(1).mediaBox.getLowerRight_x(), 'y': input1.getPage(1).mediaBox.getLowerRight_y()};
    bottom_left = {'x': input1.getPage(1).mediaBox.getLowerLeft_x(), 'y': input1.getPage(1).mediaBox.getLowerLeft_y()};
    print 'Page dim.\t%f by %f' %(top_right['x'], top_right['y']); 
    
    pdf_page_size[0] = top_right['x'];
    pdf_page_size[1] = top_right['y'];

    cut = cut_length(top_right, 'x', factor);
    print cut;
    new_tr = (new_coords(top_right, 'x', cut, margin, code = "tr"), new_coords(top_right, 'y', cut, margin, code = "tr"));
    new_br = (new_coords(bottom_right, 'x', cut, margin, code = "br"), new_coords(bottom_right, 'y', cut, margin, code = "br" ));
    new_tl = (new_coords(top_left, 'x', cut, margin, code = "tl"), new_coords(top_left, 'y', cut, margin, code = "tl"));
    new_bl = (new_coords(bottom_left, 'x', cut, margin, code = "bl"), new_coords(bottom_left, 'y', cut, margin, code = "bl"));

    print new_tr,new_br,new_tl,new_bl;


    page_number_list = [];
    for item in page_number_rotation_list:
        page_number_list.append(item[0]);

    print page_number_list;
    page_number_list = list(sorted(set(page_number_list)));
    for i in range(0, pages):
        if (i+1) in page_number_list:
            crop_file_name_str = input_file[:-4] + '_' + str(i+1) + '.pdf';
            output_file = crop_file_name_str;
            output = PdfFileWriter();
            outputstream = file(output_file,'wb');
            page = input1.getPage(i);
            page.mediaBox.upperLeft = new_tl;
            page.mediaBox.upperRight = new_tr;
            page.mediaBox.lowerLeft = new_bl;
            page.mediaBox.lowerRight = new_br;
            # page.rotateClockwise(90);
            output.addPage(page);                
            output.write(outputstream);
            outputstream.close();
            pdf_name = crop_file_name_str;
            img_name = crop_file_name_str[:-4] + '.jpg';
            p = PythonMagick.Image();
            p.density(str(img_density));
            p.read(pdf_name);
            p.write(img_name);
            os.remove(crop_file_name_str);

            doc_id = db_query_doc_id(file_name_full);
            ###########################################
            # consider about the conditions, seems like not a very good design 
            # update_column_list = ['Doc_Page_Pic_Bin'];
            # update_value_list = [];
            
            # where_column_list = ['Doc_ID', 'Doc_Page_Pic_PageNum'];
            # where_value_list = [];

            # table_name = '[xtr].[Doc_Page_Pic]';
            ###########################################
            vertical_flag = 0;
            for item in page_number_rotation_list:
                if item[0] == i+1 and item[1]=='Vertical':
                    # print item[1];
                    vertical_flag = 1;


            add_page_pic_sql_str = 'UPDATE [xtr].[Doc_Page_Pic] SET [Doc_Page_Pic_Bin] = ? WHERE [Doc_ID] = ' +  str(doc_id) + ' AND [Doc_Page_Pic_PageNum] = ' + \
                                    str(i+1) + ' IF @@ROWCOUNT = 0 INSERT INTO [xtr].[Doc_Page_Pic] ( [Doc_ID], [Doc_Page_Pic_PageNum], [Is_Vertical], [Doc_Page_Pic_Bin] ) VALUES ( ' + \
                                    str(doc_id) + ', ' + str(i+1) + ' , ' + str(vertical_flag)  + ', ?);'
            # insert = 'insert into [xtr].[Doc_Page_Pic] ([Doc_Img_Pic_Bin]) Values (?)'
            # print '**************************************************************';
            # print add_page_pic_sql_str;
            # print '**************************************************************';

            bindata = open(img_name, 'rb').read();
            binparams = pyodbc.Binary(bindata);
            binparams_dup = pyodbc.Binary(bindata);
            db_connection.cursor().execute(add_page_pic_sql_str, binparams, binparams_dup);
            db_connection.commit();
            os.remove(img_name);

def show_all_pics(option_string, field_id=None, temp_name = None):
    if field_id == None:
        print doc_id;
        query_all_pics_sql_str = 'SELECT * FROM [xtr].[Doc_' + option_string + '_Pic];';
        all_pics_df = execute_pure_query_to_pddf(query_all_pics_sql_str);
        for i in range(0, len(all_pics_df)):
            ablob = all_pics_df.iloc[i]['Doc_' + option_string + '_Pic_Bin'];
            temp_file_name = str(i+1);  #all_pics_df.iloc[i]['Field_Value_ID'];
            jpg_file_name = 'Temp\\' + str(temp_file_name) + '.jpg';
            with open(jpg_file_name,'wb') as output_file:
                output_file.write(ablob);
            os.startfile(jpg_file_name);
    if field_id != None:
        print doc_id;
        query_all_pics_sql_str = 'SELECT * FROM [xtr].[Doc_' + option_string + '_Pic] WHERE [Field_Value_ID] = ' + str(field_id) + ' ;';
        all_pics_df = execute_pure_query_to_pddf(query_all_pics_sql_str);
        if len(all_pics_df) > 0:
            for i in range(0, len(all_pics_df)):
                ablob = all_pics_df.iloc[i]['Doc_' + option_string + '_Pic_Bin'];
                temp_file_name = str(i+1);  #all_pics_df.iloc[i]['Field_Value_ID'];
                jpg_file_name = 'Temp\\' + str(temp_file_name) + '_' + temp_name + '.jpg';
                with open(jpg_file_name,'wb') as output_file:
                    output_file.write(ablob);
                os.startfile(jpg_file_name);
        else:
            print 'No Image found!';



x_modify_factor_1 = -15;
y_modify_factor_1 = 15;
x_modify_factor_2 = 20;
y_modify_factor_2 = -10;



def modify_highlight_matrix(original_matrix):
    modified_highlight_matrix = original_matrix;
    modified_highlight_matrix[1] = -modified_highlight_matrix[1];
    modified_highlight_matrix[3] = -modified_highlight_matrix[3];

    modified_highlight_matrix[0] = ( modified_highlight_matrix[0] ) * resize_ratio[0] * 1.15 + x_modify_factor_1;
    modified_highlight_matrix[1] = ( modified_highlight_matrix[1] + pdf_page_size[1] ) * resize_ratio[1] * 1.15 + y_modify_factor_1;
    modified_highlight_matrix[2] = ( modified_highlight_matrix[2] ) * resize_ratio[0] * 1.15 + x_modify_factor_2;
    modified_highlight_matrix[3] = ( modified_highlight_matrix[3] + pdf_page_size[1] ) * resize_ratio[1] * 1.15 + y_modify_factor_2;

    return modified_highlight_matrix;


def get_pic_size(doc_id, page_number):
    query_page_img_str = 'SELECT * FROM [xtr].[Doc_Page_Pic] WHERE [Doc_ID] = ' + str(doc_id) + \
                            ' AND [Doc_Page_Pic_PageNum] = ' + str(page_number) + ';';
    page_img_df = execute_pure_query_to_pddf(query_page_img_str);
    if len(page_img_df) > 0:
        print '-----------------------------';
        ablob = page_img_df.iloc[0]['Doc_Page_Pic_Bin'];
        temp_jpg_file = 'temp.jpg';
        with open(temp_jpg_file,'wb') as output_file:
            output_file.write(ablob);
        im = Image.open(temp_jpg_file);
        x, y =  im.size;
        print im.size;
        global pdf_page_img_size;
        pdf_page_img_size[0] = im.size[0];
        pdf_page_img_size[1] = im.size[1];
        im.close(); 

size_flag = 0;


def highlight_pdf_page_info(doc_id, page_number, coordinates_list, field_value_id, db_connection=None):
    query_page_img_str = 'SELECT * FROM [xtr].[Doc_Page_Pic] WHERE [Doc_ID] = ' + str(doc_id) + \
                            ' AND [Doc_Page_Pic_PageNum] = ' + str(page_number) + ';';

    global size_flag;
    if size_flag == 0:
        get_pic_size(doc_id, 1);
        size_flag = 1;


    page_img_df = execute_pure_query_to_pddf(query_page_img_str);
    if len(page_img_df) > 0:
        for i in range(0, len(page_img_df)):
            global pdf_page_img_size;
            resize_ratio[0] = pdf_page_img_size[0] / pdf_page_size[0];
            resize_ratio[1] = pdf_page_img_size[1] / pdf_page_size[1];
    

            coordinates_list = modify_highlight_matrix(coordinates_list);
            minpoint_X = coordinates_list[0] ;
            minpoint_Y = coordinates_list[1] ;
            maxpoint_X = coordinates_list[2] ;
            maxpoint_Y = coordinates_list[3] ;

            rotation_degree = 0;
            if page_img_df.iloc[i]['Is_Vertical'] == 1:
                rotation_degree = 270;

            # os.startfile(temp_jpg_file);
            add_field_pic_sql_str = 'UPDATE [xtr].[Doc_Field_Pic_Info] SET [Doc_Page_Pic_ID] = ' + str(page_img_df.iloc[i]['Doc_Page_Pic_ID']) + ' , [Doc_Pic_Rotation_Degree] = ' + str(rotation_degree) + \
                                    ' , [Pos_Minpoint_X] = ' + str(minpoint_X) + ' , [Pos_Minpoint_Y] = ' + str(minpoint_Y) + ' , [Pos_Maxpoint_X] = ' + str(maxpoint_X) + ' , [Pos_Maxpoint_Y] = ' +\
                                    str(maxpoint_Y) + ' WHERE [Doc_Field_Value_ID] = ' +  str(field_value_id) + \
                                    ' IF @@ROWCOUNT = 0 INSERT INTO [xtr].[Doc_Field_Pic_Info] ( [Doc_Page_Pic_ID], [Doc_Field_Value_ID], [Doc_Pic_Rotation_Degree], [Pos_Minpoint_X], [Pos_Minpoint_Y], [Pos_Maxpoint_X], [Pos_Maxpoint_Y] ) VALUES ( ' + \
                                    str(page_img_df.iloc[i]['Doc_Page_Pic_ID']) + ' , ' + str(field_value_id) + ' , ' + str(rotation_degree) + ' , ' + str(minpoint_X) + ' , ' + str(minpoint_Y) + ' , ' \
                                    + str(maxpoint_X) + ' , ' + str(maxpoint_Y) + ' );'
            
            # print '**************************************************************';
            # print add_field_pic_sql_str;
            # print '**************************************************************';
            db_connection.cursor().execute(add_field_pic_sql_str);
            db_connection.commit();
    else:
        rotation_degree = 0;
        minpoint_X = minpoint_Y = maxpoint_X = maxpoint_Y = 0;
        print query_page_img_str;
        add_field_pic_sql_str = 'UPDATE [xtr].[Doc_Field_Pic_Info] SET [Doc_Page_Pic_ID] = NULL , [Doc_Pic_Rotation_Degree] = ' + str(rotation_degree) + \
                                    ' , [Pos_Minpoint_X] = ' + str(minpoint_X) + ' , [Pos_Minpoint_Y] = ' + str(minpoint_Y) + ' , [Pos_Maxpoint_X] = ' + str(maxpoint_X) + ' , [Pos_Maxpoint_Y] = ' +\
                                    str(maxpoint_Y) + ' WHERE [Doc_Field_Value_ID] = ' +  str(field_value_id) + \
                                    ' IF @@ROWCOUNT = 0 INSERT INTO [xtr].[Doc_Field_Pic_Info] ( [Doc_Page_Pic_ID], [Doc_Field_Value_ID], [Doc_Pic_Rotation_Degree], [Pos_Minpoint_X], [Pos_Minpoint_Y], [Pos_Maxpoint_X], [Pos_Maxpoint_Y] ) VALUES ( NULL , '\
                                     + str(field_value_id) + ' , ' + str(rotation_degree) + ' , ' + str(minpoint_X) + ' , ' + str(minpoint_Y) + ' , ' \
                                    + str(maxpoint_X) + ' , ' + str(maxpoint_Y) + ' );'
            
        # print '**************************************************************';
        # print add_field_pic_sql_str;
        # print '**************************************************************';
        db_connection.cursor().execute(add_field_pic_sql_str);
        db_connection.commit();

        print 'nothing';




        
####################################################################################################
def add_Doc_Field_Value_HLImage_Generation(field_name_id_list, combined_all_field_value , merge_int_info_box, db_connection=None):
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
    field_name_list['Page_Number'] = '';
    field_name_list['Minpoint_X'] = '';
    field_name_list['Minpoint_Y'] = '';
    field_name_list['Maxpoint_X'] = '';
    field_name_list['Maxpoint_Y'] = '';
    for i in range(0, len(field_name_list)):
        for j in range(0, len(combined_all_field_value)):
            if (field_name_list.iloc[i]['Field_Name'] == combined_all_field_value[j][0]) and (len(combined_all_field_value[j][1]) > 1):
                field_index = j;
                field_name_list.set_value(i,'Field_Value', combined_all_field_value[j][1][value_pointer][0]);
                field_name_list.set_value(i,'Page_Number', combined_all_field_value[j][1][value_pointer][1]);
                field_name_list.set_value(i,'Minpoint_X', combined_all_field_value[j][1][value_pointer][3]);
                field_name_list.set_value(i,'Minpoint_Y', combined_all_field_value[j][1][value_pointer][4]);
                field_name_list.set_value(i,'Maxpoint_X', combined_all_field_value[j][1][value_pointer][5]);
                field_name_list.set_value(i,'Maxpoint_Y', combined_all_field_value[j][1][value_pointer][6]);
                value_pointer = value_pointer + 1;      
        
            if (field_name_list.iloc[i]['Field_Name'] == combined_all_field_value[j][0]) and (len(combined_all_field_value[j][1]) == 1):
                # print len(combined_all_field_value[j][1]);
                # print 'We reach here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!';
                field_name_list.set_value(i,'Field_Value', combined_all_field_value[j][1][0][0]);
                field_name_list.set_value(i,'Page_Number', combined_all_field_value[j][1][0][1]);
                field_name_list.set_value(i,'Minpoint_X', combined_all_field_value[j][1][0][3]);
                field_name_list.set_value(i,'Minpoint_Y', combined_all_field_value[j][1][0][4]);
                field_name_list.set_value(i,'Maxpoint_X', combined_all_field_value[j][1][0][5]);
                field_name_list.set_value(i,'Maxpoint_Y', combined_all_field_value[j][1][0][6]);

        if value_pointer == len(combined_all_field_value[field_index][1]):
            value_pointer = 0;
            field_index = 0;


            
         
    print 'Strong signal here!!!!!!!!!!!!!!!!!!!!!!!!'

    for i in range(0, len(field_name_list)):

        add_Doc_Field_Value_sqlstr = 'SET NOCOUNT ON; UPDATE [xtr].[Doc_Field_Value] SET ' ;
        add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Field_Value] = \'' + str(field_name_list.iloc[i]['Field_Value']) + '\' ,';
        add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Calcrt_ID] = \'' + str(field_name_list.iloc[i]['Calcrt_ID']) + '\',';
        add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Field_Value_Is_Numeric] = ISNUMERIC( \'' + str(field_name_list.iloc[i]['Field_Value']) + '\') WHERE ';
        add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + '[Field_Name_ID] = ' + str(field_name_list.iloc[i]['Field_Name_ID']);
        add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + ' IF @@ROWCOUNT=0 ' + 'INSERT INTO [xtr].[Doc_Field_Value] (Field_Name_ID, Field_Value, Calcrt_ID, Field_Value_Is_Numeric) OUTPUT Inserted.[Field_Value_ID] VALUES (';
        add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + str(field_name_list.iloc[i]['Field_Name_ID']) + ', \'' \
                                    + str(field_name_list.iloc[i]['Field_Value']) + '\', \'' + str(field_name_list.iloc[i]['Calcrt_ID']) + '\', ISNUMERIC(\'' + str(field_name_list.iloc[i]['Field_Value']) + '\'))';
        add_Doc_Field_Value_sqlstr = add_Doc_Field_Value_sqlstr + ' ELSE SELECT [Field_Value_ID] FROM [xtr].[Doc_Field_Value] WHERE [Field_Name_ID] = ' + str(field_name_list.iloc[i]['Field_Name_ID']) + ' ;';
        

        # print add_Doc_Field_Value_sqlstr;
        # doc_field_value_id_df = execute_pure_query_to_pddf(add_Doc_Field_Value_sqlstr);
        # print '???';
        result_cursor  = db_connection.cursor().execute(add_Doc_Field_Value_sqlstr);
        row = result_cursor.fetchone();
        if row:
            print row[0];
            coordinates_list = [field_name_list.iloc[i]['Minpoint_X'], field_name_list.iloc[i]['Minpoint_Y'], field_name_list.iloc[i]['Maxpoint_X'], field_name_list.iloc[i]['Maxpoint_Y']];
            page_number = field_name_list.iloc[i]['Page_Number'];
            global doc_id;
            highlight_pdf_page_info(doc_id, page_number, coordinates_list, int(row[0]), db_connection);    
            if field_name_list.iloc[i]['Page_Number'] == 0:
                highlight_special_merge_pic(doc_id, int(row[0]), merge_int_info_box, db_connection);

    db_connection.commit();
        # print len(doc_field_value_id_df);
        # print doc_field_value_id_df.iloc[0]['Field_Value_ID'];




####################################################################################################




####################################################################################################
def highlight_pdf_page(doc_id, page_number, coordinates_list, field_value_id, db_connection=None):
    

    query_page_img_str = 'SELECT [Doc_Page_Pic_Bin],[Is_Vertical] FROM [xtr].[Doc_Page_Pic] WHERE [Doc_ID] = ' + str(doc_id) + \
                            ' AND [Doc_Page_Pic_PageNum] = ' + str(page_number) + ';';

    page_img_df = execute_pure_query_to_pddf(query_page_img_str);
    if len(page_img_df) > 0:
        for i in range(0, len(page_img_df)):
            print '-----------------------------';
            ablob = page_img_df.iloc[i]['Doc_Page_Pic_Bin'];
            temp_jpg_file = 'temp.jpg';
            with open(temp_jpg_file,'wb') as output_file:
                output_file.write(ablob);
            im = Image.open(temp_jpg_file);
            print im.mode;
            im = im.convert('RGB');
            print im.mode;
            x, y =  im.size;
            print im.size;

            resize_ratio[0] = im.size[0] / pdf_page_size[0];
            resize_ratio[1] = im.size[1] / pdf_page_size[1];
    

            coordinates_list = modify_highlight_matrix(coordinates_list);
            minpoint_X = coordinates_list[0] ;
            minpoint_Y = coordinates_list[1] ;
            maxpoint_X = coordinates_list[2] ;
            maxpoint_Y = coordinates_list[3] ;


            draw = ImageDraw.Draw(im);
            draw.line(((minpoint_X,minpoint_Y),(minpoint_X,maxpoint_Y)),width = 4,fill='red');
            draw.line(((minpoint_X,maxpoint_Y),(maxpoint_X,maxpoint_Y)),width = 4,fill='red');
            draw.line(((maxpoint_X,maxpoint_Y),(maxpoint_X,minpoint_Y)),width = 4,fill='red');
            draw.line(((maxpoint_X,minpoint_Y),(minpoint_X,minpoint_Y)),width = 4,fill='red');  

            if page_img_df.iloc[i]['Is_Vertical'] == 1:
                im = im.rotate(270,expand=1);


            im.save(temp_jpg_file);
            # os.startfile(temp_jpg_file);
            add_field_pic_sql_str = 'UPDATE [xtr].[Doc_Field_Pic] SET [Doc_Field_Pic_Bin] = ? WHERE [Field_Value_ID] = ' +  str(field_value_id) + \
                                ' IF @@ROWCOUNT = 0 INSERT INTO [xtr].[Doc_Field_Pic] ( [Field_Value_ID], [Doc_Field_Pic_Bin] ) VALUES ( ' + \
                                    str(field_value_id) + ', ?);'
            # insert = 'insert into [xtr].[Doc_Page_Pic] ([Doc_Img_Pic_Bin]) Values (?)'
            # print '**************************************************************';
            # print add_field_pic_sql_str;
            # print '**************************************************************';

            bindata = open(temp_jpg_file, 'rb').read();
            binparams = pyodbc.Binary(bindata);
            binparams_dup = pyodbc.Binary(bindata);
            db_connection.cursor().execute(add_field_pic_sql_str, binparams, binparams_dup);
            db_connection.commit();

            os.remove(temp_jpg_file);
            output_file.close();






    else:
        print 'nothing';

####################################################################################################



####################################################################################################
def draw_and_show_pic(field_value_id):
    highlighted_pic_info_sqlstr = 'SELECT * FROM [xtr].[Doc_Field_Pic_Info] WHERE [Doc_Field_Value_ID] = ' + str(field_value_id) + ';';
    highlighed_pic_info_df = execute_pure_query_to_pddf(highlighted_pic_info_sqlstr);
    if len(highlighed_pic_info_df) > 0 :
        doc_page_pic_id = highlighed_pic_info_df.iloc[0]['Doc_Page_Pic_ID'];
        doc_field_value_id = highlighed_pic_info_df.iloc[0]['Doc_Field_Value_ID'];
        rotation_degree = highlighed_pic_info_df.iloc[0]['Doc_Pic_Rotation_Degree'];
        minpoint_X = highlighed_pic_info_df.iloc[0]['Pos_Minpoint_X'];
        minpoint_Y = highlighed_pic_info_df.iloc[0]['Pos_Minpoint_Y'];
        maxpoint_X = highlighed_pic_info_df.iloc[0]['Pos_Maxpoint_X'];
        maxpoint_Y = highlighed_pic_info_df.iloc[0]['Pos_Maxpoint_Y'];

        if doc_page_pic_id == None:
            doc_page_pic_id = 0;

        page_pic_sqlstr = 'SELECT * FROM [xtr].[Doc_Page_Pic] WHERE [Doc_Page_Pic_ID] = ' + str(doc_page_pic_id) + ';';
        page_pic_df = execute_pure_query_to_pddf(page_pic_sqlstr);
        
        if len(page_pic_df) > 0:
            ablob = page_pic_df.iloc[0]['Doc_Page_Pic_Bin'];
            temp_jpg_file = 'Temp\\' + str(field_value_id) +'_temp.jpg';
            with open(temp_jpg_file,'wb') as output_file:
                output_file.write(ablob);
            im = Image.open(temp_jpg_file);
            print im.mode;
            im = im.convert('RGB');
            print im.mode;
            x, y =  im.size;
            print im.size;
            draw = ImageDraw.Draw(im);
            draw.line(((minpoint_X,minpoint_Y),(minpoint_X,maxpoint_Y)),width = 4,fill='red');
            draw.line(((minpoint_X,maxpoint_Y),(maxpoint_X,maxpoint_Y)),width = 4,fill='red');
            draw.line(((maxpoint_X,maxpoint_Y),(maxpoint_X,minpoint_Y)),width = 4,fill='red');
            draw.line(((maxpoint_X,minpoint_Y),(minpoint_X,minpoint_Y)),width = 4,fill='red');  
            im = im.rotate(rotation_degree,expand=1);
            im.save(temp_jpg_file);           
            os.startfile(temp_jpg_file);
            output_file.close();

        else:
            print 'Nothing returned for this doc page id.';
            special_pic_sqlstr = 'SELECT * FROM [xtr].[Doc_Special_Pic] WHERE [Field_Value_ID] = ' + str(doc_field_value_id) + ' ;';
            special_pic_df = execute_pure_query_to_pddf(special_pic_sqlstr);
            if len(special_pic_sqlstr) > 0:
                ablob = special_pic_df.iloc[0]['Doc_Special_Pic_Bin'];
                temp_jpg_file = 'Temp\\' + str(field_value_id) +'.jpg';
                with open(temp_jpg_file,'wb') as output_file:
                    output_file.write(ablob);
                os.startfile(temp_jpg_file);
            else:
                print special_pic_sqlstr;
    else:
        print 'Nothing returned for this field value id.';        

####################################################################################################



#############################################
#  The following is an exciting method
#  that will deal with the remaining 
#  special interest rate issues
#  YOHO!
#############################################

####################################################################################################

def highlight_special_merge_pic(doc_id, field_value_id, merge_int_info_box, db_connection=None):
    print '===============================================================';
    print doc_id, field_value_id, merge_int_info_box;
    if len(merge_int_info_box) != 2:
        print 'Merge info is wrong.';
        return;
    if merge_int_info_box[0][2] == merge_int_info_box[1][2]:
        page_number = merge_int_info_box[0][2];
        page_query_sqlstr = 'SELECT * FROM [xtr].[Doc_Page_Pic] WHERE [Doc_ID] = ' + str(doc_id) + ' and [Doc_Page_Pic_PageNum] = ' + str(page_number) + '; ';
        page_img_df = execute_pure_query_to_pddf(page_query_sqlstr);
        
        global size_flag;
        if size_flag == 0:
            get_pic_size(doc_id, 1);
            size_flag = 1;

        coordinates_list = [75, merge_int_info_box[1][1], 540, merge_int_info_box[0][1]];    
        if len(page_img_df) > 0:
            for i in range(0, len(page_img_df)):
                print '-----------------------------';
                ablob = page_img_df.iloc[i]['Doc_Page_Pic_Bin'];
                temp_jpg_file = str(field_value_id) + '_temp.jpg';
                with open(temp_jpg_file,'wb') as output_file:
                    output_file.write(ablob);
                im = Image.open(temp_jpg_file);
                print im.mode;
                im = im.convert('RGB');
                print im.mode;
                x, y =  im.size;
                print im.size;

                global pdf_page_img_size;
                resize_ratio[0] = pdf_page_img_size[0] / pdf_page_size[0];
                resize_ratio[1] = pdf_page_img_size[1] / pdf_page_size[1];
        

                coordinates_list = modify_highlight_matrix(coordinates_list);
                minpoint_X = coordinates_list[0] ;
                minpoint_Y = coordinates_list[1] ;
                maxpoint_X = coordinates_list[2] ;
                maxpoint_Y = coordinates_list[3] ;

                draw = ImageDraw.Draw(im);
                draw.line(((minpoint_X,minpoint_Y),(minpoint_X,maxpoint_Y)),width = 4,fill='red');
                draw.line(((minpoint_X,maxpoint_Y),(maxpoint_X,maxpoint_Y)),width = 4,fill='red');
                draw.line(((maxpoint_X,maxpoint_Y),(maxpoint_X,minpoint_Y)),width = 4,fill='red');
                draw.line(((maxpoint_X,minpoint_Y),(minpoint_X,minpoint_Y)),width = 4,fill='red');  

                if page_img_df.iloc[i]['Is_Vertical'] == 1:
                    im = im.rotate(270,expand=1);


                im.save(temp_jpg_file);
                # os.startfile(temp_jpg_file);
                add_field_pic_sql_str = 'UPDATE [xtr].[Doc_Special_Pic] SET [Doc_Special_Pic_Bin] = ? WHERE [Field_Value_ID] = ' +  str(field_value_id) + \
                                ' IF @@ROWCOUNT = 0 INSERT INTO [xtr].[Doc_Special_Pic] ( [Field_Value_ID], [Doc_Special_Pic_Bin] ) VALUES ( ' + \
                                    str(field_value_id) + ', ?);'
                # insert = 'insert into [xtr].[Doc_Page_Pic] ([Doc_Img_Pic_Bin]) Values (?)'
                # print '**************************************************************';
                # print add_field_pic_sql_str;
                # print '**************************************************************';

                bindata = open(temp_jpg_file, 'rb').read();
                binparams = pyodbc.Binary(bindata);
                binparams_dup = pyodbc.Binary(bindata);
                db_connection.cursor().execute(add_field_pic_sql_str, binparams, binparams_dup);
                db_connection.commit();

                os.remove(temp_jpg_file);
                output_file.close();
        else:
            print 'Nothing 2!';    
    else:
        print 'To be implemented';
        for i in range(merge_int_info_box[0][2], merge_int_info_box[1][2]+1):
            print i;









####################################################################################################