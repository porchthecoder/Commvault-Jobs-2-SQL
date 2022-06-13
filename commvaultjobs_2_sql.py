#!/usr/bin/python2
import requests
import sys
import xml.etree.ElementTree as ET
import base64
import time
import re
import mysql.connector

##Commvault jobs to SQL database for Grafana
##Version 0.1 - 2/25/2022




#Commvault creds
user = 'DOMAIN\\user'
pwd = b'<password>'
service = 'http://<commvaultwebserver>:81/SearchSvc/CVWebService.svc/'


#SQL database creds
mydb = mysql.connector.connect(
	host="<sqlhost>",
	user="<user>",
	password="<password>",
	database="Commvault"
)





###########################################
##Login and get the token
loginReq = '<DM2ContentIndexing_CheckCredentialReq mode="Webconsole" username="<<username>>" password="<<password>>" />'

loginReq = loginReq.replace("<<username>>", user)
#encode password in base64
loginReq = loginReq.replace("<<password>>", str(base64.b64encode(pwd)))

#Login request built. Send the request now:
r = requests.post(service + 'Login', data=loginReq,verify=False)
token = None

#Check response code and check if the response has an attribute "token" set
if r.status_code == 200:
	root = ET.fromstring(r.text)
	if 'token' in root.attrib:
		token = root.attrib['token']
		#print "Login Successful"
	else:
		print("Login Failed")
		sys.exit(0)
else:
	print('there was an error logging in. Code HTML:' + str(r.status_code))
	

#print 'Login sucessful'
####################################


####################
#Based on the clientId, get the details of the backup jobs. All last data is inserted into the SQL database. 

def jobStatus(clientId):

	jobsPropsReq = service + "Job?ClientiD=" + clientId + "&limit=10000"
	headers = {'Cookie2': token, "limit": str(1000)} #Limit to 1,000 last backup jobs
	jobs = requests.get(jobsPropsReq, headers=headers,verify=False)
	jobsResp = jobs.text

	#Stop here if the client is found, but does not have any backup jobs. 
	#print jobsResp
	if not "job" in jobsResp:
		##print ("Server found setup in Commvault (iData type), but no backups exist. Not set to backup? Powered off?")
		return

        #print (jobsResp)
        #Get Job data.
	jobsclient = ET.fromstring(jobsResp)
	maxJobUpdateTime = 0
	for jobsSummary in jobsclient.iter('jobSummary'):

		sizeOfMediaOnDisk = int(jobsSummary.get('sizeOfMediaOnDisk'))
		sizeOfApplication = int(jobsSummary.get('sizeOfApplication'))

		
		if jobsSummary.get('status') != "Completed": #Only get completed jobs. 
			continue

		if jobsSummary.get('localizedOperationName') == "Backup Copy": #Skip Backup Copy jobs
			continue
			
		if sizeOfMediaOnDisk == 0: #No data? Skip
			continue

		if re.search("IndexServer", jobsSummary.get('destClientName')): #Skip IndexServer jobs
			continue
	
		jobTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(jobsSummary.get('jobStartTime')))) #Parse the job start time into SQL format. 
		mycursor = mydb.cursor()
		sql = "INSERT IGNORE INTO backup_jobs (timestamp, host, subclient, sizeOfMediaOnDisk, appTypeName, sizeOfApplication) VALUES (%s, %s, %s, %s, %s, %s)"
		val = (jobTime, str(jobsSummary.get('destClientName')), str(jobsSummary.get('subclientName')), sizeOfMediaOnDisk, str(jobsSummary.get('appTypeName')), sizeOfApplication)
		mycursor.execute(sql, val) #Insert the data
		mydb.commit()
#####################


########################
#Loop over all clients in Commvault
def getNonVM():
    ##########Non-VMs
	headers = {'Cookie2': token}
	clientPropsReq = service + "Client"
	r = requests.get(clientPropsReq, headers=headers,verify=False)
	clientResp = r.text
	client = ET.fromstring(clientResp)

	for clientEntity in client.iter('clientEntity'):
	    jobStatus(clientEntity.get('clientId'))

##########################

######Program starts here
getNonVM()



exit()











