#! /usr/bin/python
#gpl v2 by dave b. (db AT (IGNORE THIS ) d1b (D-O-T) org )

import urllib
import urllib2
import re

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

def calculate_gpa_and_print(data):
	rt = 0 #results total
	counter =0
	tc =0 #total credit points
	for line in data:
		if "HDHigh Distinction" in line:
			assert counter+1 < len(data)
			tc =tc + int (get_credit_point(data[counter+1]) )
			rt  = rt + ( int (get_credit_point(data[counter+1]) ) *(4) )
		elif "DDistinction" in line:
			assert counter+1 < len(data)
			tc =tc + int (get_credit_point(data[counter+1]) )
			rt  = rt + ( int (get_credit_point(data[counter+1]) ) *(4) )
		elif "CRCredit" in line:
			assert counter+1 < len(data)
			tc =tc + int (get_credit_point(data[counter+1]) )
			rt  = rt + ( int (get_credit_point(data[counter+1]) ) *(3) )
		elif "PPass" in line:
			assert counter+1 < len(data)
			tc =tc + int (get_credit_point(data[counter+1]) )
			rt  = rt + ( int (get_credit_point(data[counter+1]) ) *(2) )
		elif "PCConceded" in line:
			assert counter+1 < len(data)
			tc =tc + int (get_credit_point(data[counter+1]) )
			rt  = rt + ( int (get_credit_point(data[counter+1]) ) *(1) )
		elif "FFail" in line:
			assert counter+1 < len(data)
			tc =tc + int (get_credit_point(data[counter+1]) )
		counter =counter +1
	assert tc !=0
	print "\n" +"Your gpa is " +  str( float(rt)/float(tc) ) + "\n"

def get_value_of_it(item,data):
	counter =0
	for line in data:
		if item in line:
			line_str = str(line)
			index = line_str.find("value=")
			assert (index +7) < len(line_str)
			return line_str[index+7:-5]
		counter = counter +1

def get_input():
	return str (raw_input() )

def main():
	url_login = "https://student1.mq.edu.au/login.aspx"
	url_results = "https://student1.mq.edu.au/S1/ResultsDtls10.aspx?r=MQ.ESTU.UGSTUDNT&f=MQ.ESW.RSLTDTLS.WEB"

	conn = urllib2.urlopen(url_login)
	the_page =  conn.read()
	#close the connection
	conn.close()
	
	data =the_page.split("\n")
	view_state = get_value_of_it("__VIEWSTATE",data)
	event_validation= get_value_of_it("__EVENTVALIDATION",data)

	#prompt for a username and a password
	print "enter your username "
	username = get_input()
	print "enter your password "
	password = get_input()

	#set the submit values
	submit_data= {'__VIEWSTATE' :view_state,'ctl00$Content$txtUserName$txtText' : username,'ctl00$Content$txtPassword$txtText' : password, "ctl00$Content$cmdLogin" : "Login In", '__EVENTVALIDATION': event_validation }

	#url encode the submit data
	submit_data = urllib.urlencode(submit_data)
	the_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor() )
	urllib2.install_opener(the_opener)
	#open a connection, login + get a cookie
	conn = the_opener.open(url_login, submit_data)
	response =  conn.read()
	#close the connection
	conn.close()
	
	#get the page with the results on it
	conn = the_opener.open(url_results)
	the_page = conn.read()
	#close the connection
	conn.close()
	
	#now process the data to get the gpa and print it 
	striped_data =  strip_tags(the_page)
	striped_data = striped_data.split("\n")
	calculate_gpa_and_print(striped_data)

if __name__=='__main__':
	main()
