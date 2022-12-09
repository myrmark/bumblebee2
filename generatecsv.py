#!/bin/python3

import sys, pymysql, keyring, getpass, mysql.connector, csv
from prompt_toolkit import prompt

def export(monumber): 											#Export a MO from the database to a .csv file
    dbpw = keyring.get_password("172.28.88.47", "simdbuploader") 					#Get password for the database
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb") 	#Connect to the database
    cursor = db.cursor() 
    cursor.execute("SELECT articlenumber FROM simdb.configuredunits WHERE manufacturingorder='{}'".format(monumber))
    articlenumber = cursor.fetchall()
    for row in articlenumber:
        articlenumber = row[0]
    cursor.execute("SELECT routertype FROM simdb.articles WHERE articlenumber='{}'".format(articlenumber))
    routertype = cursor.fetchall()
    for row in routertype:
        routertype = row[0]
    if routertype == "R01" or routertype == "X3":
        cursor.execute("SELECT serial,impversion,mac,iccid1,iccid2,iccid3,iccid4,iccid5,iccid6,iccid7,iccid8,wifi0,wifi1,modemimei3,modemimei4,modemimei5,modemmodel3,modemmodel4,modemmodel5,modemfirmware3,modemfirmware4,modemfirmware5 FROM simdb.configuredunits WHERE manufacturingorder='{}'".format(monumber)) 								#Execute the query
    elif routertype == "R02" or routertype == "R02/R04" or routertype == "R04":
        cursor.execute("SELECT serial,impvertsion,mac,iccid1,iccid2,iccid3,iccid4,iccid5,iccid6,iccid7,iccid8,iccid9,iccid10,iccid11,iccid12,iccid13,iccid14,iccid15,iccid16,wifi0,modemimei2,modemimei3,modemimei4,modemimei5,modemmodel2,modemmodel3,modemmodel4,modemmodel5,modemfirmware2,modemfirmware3,modemfirmware4,modemfirmware5 FROM simdb.configuredunits WHERE manufacturingorder='{}'".format(monumber)) 				#Execute the query
    output = cursor.fetchall()
    db.close() 											#Close the connection
    cursor.close() 											#Close the connection
    fp = open('SIM-list.csv', 'w')
    myFile = csv.writer(fp)
    myFile.writerows(output)
    fp.close()

def main(monumber):
    export(monumber)
    
if __name__ == "__main__":
    monumber = prompt('What is the MO number?:')
    main(monumber)
