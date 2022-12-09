#!/bin/python3

import smtplib, email, sys, pymysql, keyring, getpass
from email import encoders
from email.message import EmailMessage
from prompt_toolkit import prompt

def getemails(projectid): 										#Get emails that are assigned to the project in the database
    dbpw = keyring.get_password("172.28.88.47", "simdbuploader") 					#Get password for the database
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb") 	#Connect to the database
    cursor = db.cursor() 
    cursor.execute("SELECT email FROM simdb.projects WHERE projectid='{}'".format(projectid)) 	#Execute the query
    emails = cursor.fetchall() 									#Save emails to a variable
    db.close() 											#Close the connection
    cursor.close() 											#Close the connection
    for row in emails:
        emails = row[0] 										#Remove unwanted characters from the variable with emails
    return emails
    
def getprojectname(projectid): 										#Get the name of the project
    dbpw = keyring.get_password("172.28.88.47", "simdbuploader") 					#Get password for the database
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb") 	#Connect to the database
    cursor = db.cursor() 
    cursor.execute("SELECT projectname FROM simdb.projects WHERE projectid='{}'".format(projectid)) #Execute the query
    projectname = cursor.fetchall() 									#Save emails to a variable
    db.close() 											#Close the connection
    cursor.close() 											#Close the connection
    for row in projectname:
        projectname = row[0] 										#Remove unwanted characters from the variable with emails
    return projectname

def send(emails,projectname):
    filename = "SIM-list.csv" 									#Location of the SIM-list on the system
    subject = "SIM-list" 										#Subject of the email
    body = "Please find the SIM-list attached in this email." 					#Message in the email
    sender_email = "production.se@icomera.com" 							#Where the email is sent from
    receiver_email = "{}".format(emails) 								#Where the email is sent to
    msg = EmailMessage() 										#Build the email
    msg["From"] = "production.se@icomera.com"
    msg["Subject"] = "SIM-list {}".format(projectname)
    msg["To"] = "{}".format(emails)
    msg["Bcc"] = "filip.malmberg@icomera.com"
    msg.set_content("Please find the SIM-list attached in this email.")
    msg.add_attachment(open(filename, "r").read(), filename="SIM-list-{}.csv".format(projectname))
    try: 												#Attempt to send the mail
        s = smtplib.SMTP('smtp.icomera.com')
        s.send_message(msg)
        return True
    except smtplib.SMTPException: 									#If unsuccessful, return False
        return False

def main(projectid):
    emails = getemails(projectid)
    projectname = getprojectname(projectid)
    send(emails,projectname)
    
if __name__ == "__main__":
    projectid = prompt('What is the project ID?:')
    main(projectid)
