import unittest
from selenium import webdriver
import time
import csv
import os
from datetime import datetime
from datetime import timezone
from influxdb import InfluxDBClient
from pyvirtualdisplay import Display

def write_csv(content, filepath):
	with open(filepath, 'w', newline='') as file:
		writer=csv.writer(file,quoting=csv.QUOTE_ALL)
		writer.writerows(content)

def clean_string(text,dic):
	for i, j in dic.items():
		text=text.replace(i,j)
	return text

def send_influx(data):
	dbClient = InfluxDBClient('10.11.12.131', 8086, 'root', 'root', 'SunSuper')
	dbClient.create_database('SunSuper')
	dbClient.write_points(data,time_precision='s')


d={ "%": "", ",": "","$":""}
my_list=[]
user=""
password=""
default_directory="/home/ekul/Documents/Coates"
filename="ssinvest.csv"

display=Display(visible=0)
display.start()

driver = webdriver.Chrome()
driver.get('https://secure.sunsuper.com.au/memberonline')
time.sleep(10)

driver.find_element_by_id('idToken1').send_keys(user)
time.sleep(5)

driver.find_element_by_id('idToken2').send_keys(password)
time.sleep(5)

driver.find_element_by_id('loginButton_0').click()
time.sleep(10)

driver.get('https://secure.sunsuper.com.au/MemberOnline/Investment/Options')
time.sleep(10)

sdate=driver.find_element_by_xpath('//*[@id="tab-content"]/h2[1]').text
sdate=sdate.replace("How your money was invested as at ","")
ddate=datetime.strptime(sdate, "%d %B %Y")
ts = int(ddate.replace(tzinfo=timezone.utc).timestamp())

sdate=ddate.strftime("%Y-%m-%d")

table = driver.find_element_by_xpath('//*[@id="tab-content"]/table[1]')
for row in table.find_elements_by_css_selector('tr'):
	output=[]
	measurement=""
	balance=0
	units=0
	unitprice=0
	allocation=0
	i=0

	for cell in row.find_elements_by_tag_name('td'):
		output.append(clean_string(cell.text,d))
		i=i+1
		if i==1:
			measurement=clean_string(cell.text,d)
		if i==2:
			balance=clean_string(cell.text,d)
		if i==3:
			units=clean_string(cell.text,d)
		if i==4:
			unitprice=clean_string(cell.text,d)
		if i==5:
			allocation=clean_string(cell.text,d)
	if output:
		print("measurement: "+measurement+", balance: "+str(balance)+", units: "+str(units)+", unitprice: "+str(unitprice)+", allocation: "+str(allocation)+", ts: "+str(ts))

		data={}
		data["measurement"]="Super"
		data["tags"]={"type":measurement}
		data["fields"]={"balance":float(balance), "units":float(units), "unitprice":float(unitprice), "allocation":float(allocation)}
		data["time"]=ts


		print(data)
		send_influx([data])
display.stop()