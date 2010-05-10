#! /usr/bin/python
#gpl v2 by dave b. (db AT (IGNORE THIS ) d1b (D-O-T) org )

import urllib
import urllib2
import re
import pycurl
import StringIO
import sys
import os
import getpass

def strip_tags(value):
	return re.sub(r'<[^>]*?>', '', value)

def get_credit_point(data):
	data = str(data)
	index_grade = data.find(" 3")
	if index_grade ==-1:
		index_grade = data.find(" 4")
	if index_grade ==-1:
		return
	assert index_grade+3 <=len(data)
	check = str(data[index_grade+2:index_grade+3])
	if check.isdigit():
		pass
	else:
		check = str ( data[index_grade+1:index_grade+2] )
		if check.isdigit():
			return int(data[index_grade+1:index_grade+2])

def print_units_in_grade(grade_list):
	print str(len(grade_list) -1 ),
	for i in grade_list:
		print i,
	print "\n"

def print_stats(hd_list, d_list, c_list, p_list, pc_list, f_list):
	print_units_in_grade(hd_list)
	print_units_in_grade(d_list)
	print_units_in_grade(c_list)
	print_units_in_grade(p_list)
	print_units_in_grade(pc_list)
	print_units_in_grade(f_list)


def check_assumption_format(counter,data_leng,temp):
	assert len(temp) >=27
	assert counter+1 < (data_leng)
	assert counter-3 >= 0

def calculate_gpa_and_print(data,unit_prefix_1,unit_prefix_2):
	rt = 0 #results total
	counter =0
	tc =0 #total credit points
	hd_list = ["HD"]
	d_list = ["D"]
	c_list = ["C"]
	p_list = ["P"]
	pc_list = ["PC"]
	f_list = ["F"]
	wc_total = 0
	wam_top = 0

	list_grades = ["HDHigh Distinction", "DDistinction", "CRCredit", "PPass", "PCConceded", "FFail"]
	dict_gpa_points = {}
	dict_gpa_points["HDHigh Distinction"] = 4
	dict_gpa_points["DDistinction"] = 4
	dict_gpa_points["CRCredit"] = 3
	dict_gpa_points["PPass"] = 2
	dict_gpa_points["PCConceded"] = 1
	dict_gpa_points["FFail"] = 0

	data_leng = len(data)
	for line in data:
		for i in list_grades:
			if i in line:
				temp = data[counter-3]
				check_assumption_format(counter,data_leng,temp)
				credit_point = int(get_credit_point(data[counter+1]))
				tc += credit_point
				rt +=  credit_point * dict_gpa_points[i]
				if i == "HDHigh Distinction":
					hd_list.append(temp[20:27])
				elif i == "DDistinction":
					d_list.append(temp[20:27])
				elif i == "CRCredit":
					c_list.append(temp[20:27])
				elif i == "PPass":
					p_list.append(temp[20:27])
				elif i == "PCConceded":
					pc_list.append(temp[20:27])
				elif i == "FFail":
					f_list.append(temp[20:27])

				else:
					assert True == False, "not a known performance band"

				if unit_prefix_1 in temp or unit_prefix_2 in temp:
					mark = data[counter-1][24:26]
					wc_weight = credit_point * int(temp[24:25])
					wc_total += wc_weight
					wam_top += ( int(mark) * wc_weight)
				break
		counter += 1
	assert tc != 0
	assert wc_total != 0
	print_stats(hd_list, d_list, c_list, p_list, pc_list, f_list)
	print "Your GPA is " +  str( float(rt)/float(tc) ) + "\n"

	if unit_prefix_1 != "" and unit_prefix_2 != "":
		print "Your "+ unit_prefix_1 + "/" +unit_prefix_2 + " WAM is "  + str (float(wam_top) / (wc_total) )  + "\n"

	elif unit_prefix_1 !="":
		print "Your "+ unit_prefix_1 + " WAM is "  + str (float(wam_top) / (wc_total) )  + "\n"
	else:
		print "Your WAM is "  + str (float(wam_top) / (wc_total) )  + "\n"

def get_value_of_it(item,data):
	counter = 0
	for line in data:
		if item in line:
			line_str = str(line)
			index = line_str.find("value=")
			assert (index +7) < len(line_str)
			return line_str[index+7:-5]
		counter = counter +1

def get_input():
	return str (raw_input() )

def get_details_for_connection(url, conn_details):
	conn = urllib2.urlopen(url)
	the_page =  conn.read()
	#close the connection
	conn.close()
	data = the_page.split("\n")
	conn_details["view_state"] = get_value_of_it("__VIEWSTATE",data)
	conn_details["event_validation"] = get_value_of_it("__EVENTVALIDATION",data)
	return conn_details

def get_user_credentials_from_user_input(conn_details):
	#get username / password
	print "enter your username "
	conn_details["username"] = get_input()
	conn_details["password"] = getpass.getpass("enter your password\n")
	return conn_details

def get_waiver_info(data):
	at_waiver_pos = False
	counter = 0
	first_hit = True
	print "Approved waivers:"
	for line in data:
		if "UnitTitleEffective DateExpiry Date" in line:
			at_waiver_pos = True
			counter = counter +1
		if at_waiver_pos and not first_hit:
			print line[3:]
			counter = counter +1
		if counter >=10:
			at_waiver_pos = False
		if counter >=1:
			first_hit = False

def get_estudent_info(url_login,url_target,conn_details):
	submit_data_t = [ ('__VIEWSTATE', conn_details["view_state"] ), ('ctl00$Content$txtUserName$txtText', str(conn_details["username"]) ), ('ctl00$Content$txtPassword$txtText', conn_details["password"]), ('ctl00$Content$cmdLogin', 'Login In'), ('__EVENTVALIDATION',conn_details["event_validation"]) ]

	submit_data_t = urllib.urlencode(submit_data_t)

	string_s = StringIO.StringIO()
	connection = pycurl.Curl()
	connection.setopt(pycurl.FOLLOWLOCATION, True)
	connection.setopt(pycurl.SSL_VERIFYPEER, 1)
	connection.setopt(pycurl.SSL_VERIFYHOST, 2)
	connection.setopt(pycurl.WRITEFUNCTION, string_s.write)
	connection.setopt(pycurl.COOKIEFILE, os.path.expanduser("~/.mq/cookie") )
	connection.setopt(pycurl.COOKIEJAR, os.path.expanduser("~/.mq/cookie") )
	connection.setopt(pycurl.POSTFIELDS, submit_data_t)
	connection.setopt(pycurl.URL, url_login)
	connection.perform()

	connection.setopt(pycurl.WRITEFUNCTION, string_s.write)
	connection.setopt(pycurl.URL, url_target)
	connection.perform()
	the_page = str(string_s.getvalue())
	the_page = strip_tags(the_page)

	#close the connection
	connection.close()

	return the_page

def delete_cookie():
	try:
		os.remove(os.path.expanduser("~/.mq/cookie") )
	except:
		print "failed to remove the cookie file " + str (os.path.expanduser("~/.mq/cookie") )

def create_mq_directory(mq_dir):
	#if the paths don't exist already, create them.
	state = "done"
	if mq_dir == None:
		mq_dir = os.path.expanduser("~/.mq")
	if not os.path.exists(mq_dir):
		state = "init"
		os.mkdir(mq_dir)
		os.chmod(os.path.expanduser("~/.mq"),16832)
	return state

def write_to_a_file(data,full_file_loc):
	the_file = open(full_file_loc, 'w')
	the_file.write(data)
	the_file.close()

def read_from_a_file(full_file_loc,return_type ):
	the_file = open(full_file_loc, 'r')
	if return_type == "read":
		return_type = the_file.read()
	if return_type =="readlines":
		return_type = the_file.readlines()
	the_file.close()
	return return_type

def save_credentials_to_accounts_file(username,password,file_loc):
	assert username !=""
	assert password !=""
	write_to_a_file("username="+username +"\n" +"password="+password+"\n", file_loc)

def get_credentials_from_accounts_file(conn_details):
	account_file_loc = os.path.expanduser("~/.mq/account")
	credentials =[]
	username = ""
	password = ""

	the_file = read_from_a_file(account_file_loc, "readlines")
	for line in the_file:
		if "username=" in line:
			index = line.find("=")
			assert index +1 < len(line)
			username = line[index+1:-1]
		if "password=" in line:
			index = line.find("=")
			assert index +1 < len(line)
			password = line[index+1:-1]
	#url encoding is handled in the connection part. dont' worry about it here.
	conn_details["username"] = username
	conn_details["password"] = password
	return conn_details

def main():
	url_login = "https://student1.mq.edu.au/login.aspx"
	url_results = "https://student1.mq.edu.au/S1/ResultsDtls10.aspx?r=MQ.ESTU.UGSTUDNT&f=MQ.ESW.RSLTDTLS.WEB"
	url_waiver="https://student1.mq.edu.au/S1/StuWvrDtls10.aspx?r=MQ.ESTU.UGSTUDNT&f=MQ.ESW.WVRDTLS.WEB"

	mode = "gpa"
	conn_details = {}
	data = ""
	error_flag = False
	test  = False #test

	unit_prefix_1 = ""  #e.g. ISYS
	unit_prefix_2 = ""  #e.g. COMP

	print "enter gpa to get gpa information, enter waiver to get waiver information or enter wam to get wam information."
	mode = get_input()

	if "gpa" in mode:
		mode = "gpa"
		url_target = url_results
	elif "wam" in mode:
		mode = "wam"
		url_target = url_results
		print "Optional: enter a unit prefix to calculate selective WAM"
		unit_prefix_1 = get_input()
		unit_prefix_1 = unit_prefix_1.upper()
		print "Optional: enter another unit prefix"
		unit_prefix_2 = get_input()
		unit_prefix_2 = unit_prefix_2.upper()
	elif "waiver" in mode:
		mode = "waiver"
		url_target = url_waiver
	else:
		print "invalid mode choice"
		sys.exit(1)

	state = create_mq_directory(None)
	os.chmod(os.path.expanduser("~/.mq"),16832)
	if state == "init":
		get_user_credentials_from_user_input(conn_details)
		save_credentials_to_accounts_file(conn_details["username"], conn_details["password"], os.path.expanduser("~/.mq/account") )

	if test:
		try:
			data = read_from_a_file(os.path.expanduser("~/.mq/" + mode + "-page"),"read")
		except Exception, e:
			print e
	else:
		try:
			conn_details = get_details_for_connection(url_login,conn_details)
		except Exception, e:
			print e
			print "\nAn error occured during receiving the required information from the estudent website."
			error_flag = True

		if error_flag:
			sys.exit(3)

		#get credentials
		conn_details = get_credentials_from_accounts_file(conn_details)
		try:
			data = get_estudent_info(url_login, url_target, conn_details)
		except Exception:
			error_flag = True
			traceback.print_exc(file=sys.stderr)
			sys.stderr.flush()
		if error_flag:
			print "An error occured while trying to get information from estudent."
			sys.exit(3)

	striped_data = data.split("\n")
	if mode == "gpa" or mode == "wam":
		calculate_gpa_and_print(striped_data,unit_prefix_1,unit_prefix_2)
		write_to_a_file(data,os.path.expanduser("~/.mq/gpa-page"))

	elif mode == "waiver":
		get_waiver_info(striped_data)
		write_to_a_file(data,os.path.expanduser("~/.mq/waiver-page"))

	delete_cookie()

if __name__=='__main__':
	main()
