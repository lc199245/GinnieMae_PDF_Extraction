import re;


test_string_1 = 'AB.LIBOR101.8900%';
test_string_2 = 'ABC.LIBOR1.8900%';
test_string_3 = 'ABCD.LIBOR1.890%';
test_string_4 = 'A.LIBOR1.89%';
test_string_5 = '.LIBOR1.00089%HI';



test_string_6 = 'ME.3.00000';
test_string_7 = 'QS.6.05%LIBOR5.575%0.00%6.05%06.05%';
test_string_8 = '.1.84343%HI';
test_string_9 = 'ABC%AB.%123.321'

test_string_10 = '24.93333333%-(LIBOR×3.66666667)23.3750%0.00%24.93333333%196.80%';


test_string_list = [test_string_1,test_string_2,test_string_3,test_string_4,test_string_5];
test_string_list.append(test_string_6);
test_string_list.append(test_string_7);
test_string_list.append(test_string_8);
test_string_list.append(test_string_9);



regex_str = r'[^0-9][1-9]{0,1}[0-9]{1,}\.[0-9]{3,}%|[^0-9][1-9]{0,1}[0-9]{1,}\.[0-9]{3,}$';

print '----------------------------------------------';	
i = 1;
for item in test_string_list:
	print i;
	print bool(re.search(regex_str,item));
	if bool(re.search(regex_str,item)):
		print 'Start pos: ',re.search(regex_str,item).start();
		print 'End pos: ',re.search(regex_str,item).end();
		start = re.search(regex_str,item).start();
		end = re.search(regex_str,item).end();
		print re.sub(r'[^0-9.]','',item[start+1:end]);
	else:
		print bool(re.search(regex_str,item));
	print '----------------------------------------------';	
	i = i + 1;



# regex_str = r'^[A-Z]{1,2}\.|[^A-Z][A-Z]{1,2}[^A-Z]|[A-Z]{1,2}$';
# print '----------------------------------------------';	
# i = 1;
# for item in test_string_list:
# 	print i;
# 	print bool(re.search(regex_str,item));
# 	if bool(re.search(regex_str,item)):
# 		print 'Start pos: ',re.search(regex_str,item).start();
# 		print 'End pos: ',re.search(regex_str,item).end();
# 		start = re.search(regex_str,item).start();
# 		end = re.search(regex_str,item).end();
# 		print re.sub(r'[^A-Z]','',item[start:end]);
# 	else:
# 		print bool(re.search(regex_str,item));
# 	print '----------------------------------------------';	
# 	i = i + 1;
