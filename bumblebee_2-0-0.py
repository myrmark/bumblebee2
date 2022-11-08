from PyQt5 import QtWidgets, uic
import sys
import subprocess
import keyring
import time
import threading
import pymysql
import paramiko
import os
import mysql.connector
import csv
import io

from threading import Thread
from subprocess import Popen, PIPE, STDOUT, call
from paramiko.ssh_exception import *
from PyQt5 import QtCore
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from queue import Queue
from splinter import Browser
from selenium.webdriver.common.keys import Keys


dbpw = keyring.get_password("172.28.88.47", "simdbuploader")
imppw = keyring.get_password("imp","root")
ip='10.101.0.1'
port='22'
username='root'
red = "#ff0000"
green = "#008000"
black = "#000000"
bold = "font-weight: bold"
normal = "font-weight: normal"
newline = "white-space: pre-line"


def coloredtext(self, text, color, boldornot):
    self.textBrowser.append(f'<span style=\" color: {color}; {boldornot}; white-space: pre-line;\">{text}</span>')
    QApplication.processEvents()


def dbquery(select, from_DB, where, value):
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb")
    cursor = db.cursor()
    cursor.execute(f"SELECT {select} FROM simdb.{from_DB} WHERE {where}='{value}'")
    result = cursor.fetchall()
    for row in result:
        result = row[0]
    result = str(result)
    result = result.strip()
    cursor.close()
    db.close()
    return(result)


def dbupload(self, sap, projectid, mo, serial, mac, dbroutertype, imp, modems, firmwares, imeis, wifis, sims, simids):
    print(simids)
    coloredtext(self, "\nUploading information to database", black, bold)
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb")
    cursor = db.cursor()
    sql= "INSERT INTO simdb.configuredunits (serial,projectid,articlenumber,simid1,iccid1,simid2,iccid2,simid3,iccid3,simid4,iccid4,simid5,iccid5,simid6,iccid6,simid7,iccid7,simid8,iccid8,simid9,iccid9,simid10,iccid10,simid11,iccid11,simid12,iccid12,simid13,iccid13,simid14,iccid14,simid15,iccid15,simid16,iccid16,modemfirmware1,modemfirmware2,modemfirmware3,modemfirmware4,modemfirmware5,modemfirmware6,modemimei1,modemimei2,modemimei3,modemimei4,modemimei5,modemimei6,modemmodel1,modemmodel2,modemmodel3,modemmodel4,modemmodel5,modemmodel6,wifi0,wifi1,mac, impversion,manufacturingorder) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (serial, projectid, sap, simids['simid1'], sims['sim1'], simids['simid2'], sims['sim2'], simids['simid3'], sims['sim3'], simids['simid4'], sims['sim4'], simids['simid5'], sims['sim5'], simids['simid6'], sims['sim6'], simids['simid7'], sims['sim7'], simids['simid8'], sims['sim8'], simids['simid9'], sims['sim9'], simids['simid10'], sims['sim10'], simids['simid11'], sims['sim11'], simids['simid12'], sims['sim12'], simids['simid13'], sims['sim13'], simids['simid14'], sims['sim14'], simids['simid15'], sims['sim15'], simids['simid16'], sims['sim16'], firmwares['modemfirmware1'], firmwares['modemfirmware2'], firmwares['modemfirmware3'], firmwares['modemfirmware4'], firmwares['modemfirmware5'], firmwares['modemfirmware6'], imeis['imei1'], imeis['imei2'], imeis['imei3'], imeis['imei4'], imeis['imei5'], imeis['imei6'], modems['modem1'], modems['modem2'], modems['modem3'], modems['modem4'], modems['modem5'], modems['modem6'], wifis['wifi0'], wifis['wifi1'], mac, imp, mo)
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    unitid = str(dbquery("unitid", "configuredunits", "serial", serial)).strip()
    if unitid == "()":
        coloredtext(self, "\nDatabase upload verification FAIL", red, bold)
        return
    for i, key in enumerate(sims, start=1):
        if key != None:
            cursor = db.cursor()
            cursor.execute(f"UPDATE simdb.simcards SET dateused = now(), configuredunitid = '{unitid}' WHERE iccid = '{key}'")
            db.commit()
            cursor.close()
    moremaining = int(dbquery("moremaining", "manufacturingorder", "monumber", mo))
    moremaining = moremaining-1
    cursor = db.cursor()
    cursor.execute(f"UPDATE simdb.manufacturingorder SET moremaining ='{moremaining}' WHERE monumber ='{mo}'")
    db.commit()
    cursor.close()
    db.close()
    coloredtext(self, f"Configured unit ID is: {unitid}", black, normal)
    coloredtext(self, f"Remaining units on MO is: {moremaining}", black, normal)


class ThreadWithResult(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)


def filiptest(self,serial):
    coloredtext(self, "Startar filiptest", black, normal)
    filipresultat = f"{serial}, test"
    for i in range(10):
        print(f"{i}")
        time.sleep(1)
        coloredtext(self, f"{i}", black, bold)
    return filipresultat


def simdb_Check(select):
    try:
        db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb")
        cursor = db.cursor()
        cursor.execute(f"SELECT {select} FROM simdb.manufacturingorder WHERE moremaining!='0'")
        vf = cursor.fetchall()
        vf = [i[0] for i in vf]
        return(vf)
        cursor.close()
        db.close()
    except Exception as e:
        print(e)
        return(False)


def get_systemid():
    try:
        ip='10.101.0.1'
        port='22'
        username='root'
        cmd="cat /sys/class/net/eth0/address"
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,port,username,imppw,allow_agent=False,look_for_keys=False, timeout=5)
        stdin,stdout,stderr=ssh.exec_command(cmd)
        outlines=stdout.readlines()
        mac=''.join(outlines)
        mac = str(mac)
        mac = mac.strip()
        mac = mac.replace(':', '')
        mac = mac[4:]
        systemid = int(mac, 16)
        return systemid
    except Exception:
        return None


def send_ssh_command(cmd):
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port,username,imppw,allow_agent=False,look_for_keys=False, timeout=5)
    stdin,stdout,stderr=ssh.exec_command(cmd)
    outlines=stdout.readlines()
    return outlines


results = simdb_Check("monumber")
orders = []
for i in results:
    remaining = dbquery("moremaining", "manufacturingorder", "monumber", i)
    test = i+" - "+remaining
    orders.append(test)


def simcheckx3x5(self, sap):#This function checks which SIM slots are equipped with SIM cards and matches it with the database. It also verifies that the intalled SIMs operator matches the operator in the database. It uses the IIN (first six number of the iccid to match this)
    fail = False
    coloredtext(self, "\nVerifying that SIM cards are installed in the correct slot", black, bold)
    sims = {
    "sim1": None,
    "sim2": None,
    "sim3": None,
    "sim4": None,
    "sim5": None,
    "sim6": None,
    "sim7": None,
    "sim8": None,
    "sim9": None,
    "sim10": None,
    "sim11": None,
    "sim12": None,
    "sim13": None,
    "sim14": None,
    "sim15": None,
    "sim16": None,
    }
    simids = {
    "simid1": None,
    "simid2": None,
    "simid3": None,
    "simid4": None,
    "simid5": None,
    "simid6": None,
    "simid7": None,
    "simid8": None,
    "simid9": None,
    "simid10": None,
    "simid11": None,
    "simid12": None,
    "simid13": None,
    "simid14": None,
    "simid15": None,
    "simid16": None,
    }
    print2 = "{print $2}"
    lengthofsimtofetch = "{18,22}"
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb")
    cursor = db.cursor()
    sim = {}
    a = send_ssh_command("sim_cli ls")
    sim = ''.join(a)
    for i, key in enumerate(sims, start=1):
        cmd = f"sim_cli ls | grep -wE '\w{lengthofsimtofetch}' | grep SC6:{i} | awk 'FNR == 1 {print2}'"
        outlines = send_ssh_command(cmd)
        sim = ''.join(outlines)
        simdbfetch = dbquery(f"operatoridsim{i}", "articles", "articlenumber", f"{sap}")
        simdb = simdbfetch
        if len(sim) > 10 and simdb == "None":
            coloredtext(self, f"Unexpected SIM card found in slot {i}", black, normal)
            coloredtext(self, f"SIM slot {i} verification FAIL", red, normal)
            fail = True
        elif len(sim) < 10 and simdb != "None":
            coloredtext(self, f"SIM card missing from slot {i}", black, normal)
            coloredtext(self, f"SIM slot {i} verification FAIL", red, normal)
            fail = True
        elif len(sim) > 10 and simdb != "None":
            simdbiin = dbquery("iin", "operators", "operatorid", f"{simdb}")
            sim = sim.strip()
            simiin = sim[:6]
            if simiin == simdbiin:
                simdbcheck = str(dbquery("iccid", "simcards", "iccid", f"{sim}")).strip("("")"",")
                if simdbcheck != None and simdbcheck == sim:
                    coloredtext(self, f"SIM slot {i} verification PASS", green, normal)
                elif len(simdbcheck) <= 3:
                    coloredtext(self, f"SIM{i} missing from database!", black, normal)
                    coloredtext(self, f"SIM slot {i} verification FAIL", red, normal)
                    fail = True
                simid = dbquery("simid", "simcards", "iccid", f"{sim}")
                cursor.execute(f"SELECT simid FROM simdb.simcards WHERE iccid='{sim}'")
                simid = cursor.fetchall()
                for row in simid:
                    simid = row[0]
                simid = str(simid)
                sims.update({key: sim})
                simids.update({key: simid})
            else:
                coloredtext(self, f"IIN of SIM card in slot {i} and database does not match. This probably means that the SIM is not from the correct operator", black, normal)
                coloredtext(self, f"IIN of the installed SIM card is {simiin} and the IIN specified in the database is {simdbiin}", black, normal)
                coloredtext(self, f"SIM slot {i} verification FAIL", red, normal)
                fail = True
        elif len(sim) < 10 and simdb == "None":
            coloredtext(self, f"SIM slot {i} is unused", black, normal)
    return fail, sims, simids


def modemcheck(self, sap):
    coloredtext(self, "\nVerifying modem type and installation slot", black, bold)
    fail = False
    modems = {
    "modem1": None,
    "modem2": None,
    "modem3": None,
    "modem4": None,
    "modem5": None,
    "modem6": None
    }
    for i, key in enumerate(modems, start=1):
        dbmodemmodel = str(dbquery(f"modemmodel{i}", "articles", "articlenumber", f"{sap}")).strip()
        if dbmodemmodel == "None":
            coloredtext(self, f"Slot {i} is unused", black, normal)
        elif dbmodemmodel != "None":
            #self.textBrowser.append(f"Verifying slot {i}")
            #QApplication.processEvents()
            while True:
                impmodem = send_ssh_command(f"/lib/api/connectivity.umts.hwinfo 10{i}")[0].strip()
                if impmodem == "-1":
                    coloredtext(self, f"Unable to read modem type from slot {i}. Restarting modem and waiting for 30 seconds", black, normal)
                    send_ssh_command(f"wan_cli -i 10{i} softwarereset")
                    time.sleep(30)
                elif impmodem != "-1" and impmodem != dbmodemmodel:
                    coloredtext(self, "Modem slot does not seem to be empty, but it does not match the database. Trying again...", black, normal)
                    coloredtext(self, "Restarting modem and waiting for 30 seconds", black, normal)
                    send_ssh_command(f"wan_cli -i 10{i} softwarereset")
                    time.sleep(30)
                    impmodem = send_ssh_command(f"/lib/api/connectivity.umts.hwinfo 10{i}")
                    impmodem=''.join(outlines)
                    impmodem = str(impmodem).strip()
                    if impmodem != "-1" and impmodem != dbmodemmodel:
                        fail = True
                        coloredtext(self, "Unable to match modem in slot {i} with database in the given time", black, normal)
                        coloredtext(self, f"Modem 10{i} verification FAIL", red, normal)
                elif impmodem != "-1" and impmodem == dbmodemmodel:
                    coloredtext(self, f"Modem slot {i} verification PASS", green, normal)
                    modems.update({key: impmodem})
                    break
    return fail, modems

def modemfirmwarecheck(self, sap):
    coloredtext(self, "\nVerifying modem firmware", black, bold)
    fail = False
    modemfirmwares = {
    "modemfirmware1": None,
    "modemfirmware2": None,
    "modemfirmware3": None,
    "modemfirmware4": None,
    "modemfirmware5": None,
    "modemfirmware6": None
    }
    for i, key in enumerate(modemfirmwares, start=1):
        dbmodemmodel = str(dbquery(f"modemmodel{i}", "articles", "articlenumber", f"{sap}")).strip()
        if dbmodemmodel == "None":
            coloredtext(self, f"Slot {i} is unused", black, normal)
        else:
            dbmodemfirmware = str(dbquery(f"{key}", "articles", "articlenumber", f"{sap}")).strip()
            dbfirmwares = []
            for x in dbmodemfirmware.split(","):
                dbfirmwares.append(x)
            #coloredtext(self, f"Verifying slot {i}", "black")
            for x in range(10):
                test = """\',\'"""
                try:
                    impfirmware = send_ssh_command(f"""sqlite3 /tmp/wanmanager2.sqlite3 .d | grep "10{i}" | grep 'firmware_revision'""")[0].strip().split("','")[2]
                except Exception:
                    impfirmware = "None"
                    pass
                if impfirmware in dbfirmwares:
                    coloredtext(self, f"Modem{i} firmware verification PASS", green, normal)
                    modemfirmwares.update({key: impfirmware})
                    break
                elif len(impfirmware) >= 3 and impfirmware not in dbfirmwares:
                    coloredtext(self, "Firmware reported by modem does not match the database. The modem probably needs a new firmware", black, normal)
                    coloredtext(self, f"The firmware reports the following firmware: {impfirmware}", black, normal)
                    coloredtext(self, f"Modem{i} firmware verification FAIL", red, normal)
                    if x == 10:
                        fail = True
                else:
                    coloredtext(self, f"Unable to read modem firmware from slot {i}. Restarting modem and waiting for 30 seconds", black, normal)
                    send_ssh_command(f"wan_cli -i 10{i} softwarereset")
                    time.sleep(30)
    return fail, modemfirmwares


def modemimeicheck(self, sap):
    coloredtext(self, "\nVerifying modem IMEI", black, bold)
    fail = False
    imeis = {
    "imei1": None,
    "imei2": None,
    "imei3": None,
    "imei4": None,
    "imei5": None,
    "imei6": None
    }
    for i, key in enumerate(imeis, start=1):
        dbmodemmodel = str(dbquery(f"modemmodel{i}", "articles", "articlenumber", f"{sap}")).strip()
        if dbmodemmodel == "None":
            coloredtext(self, f"Slot {i} is unused", black, normal)
        else:
            for x in range(10):
                imei = send_ssh_command(f"""sqlite3 /tmp/wanmanager2.sqlite3 .d |grep -w "10{i}"|grep imei | awk -F"','" '{{print $3}}'""")[0].strip()
                if len(imei) >= 10:
                    coloredtext(self, f"Modem{i} IMEI verification PASS", green, normal)
                    imeis.update({key: imei})
                    break
                elif len(imei) <= 10:
                    coloredtext(self, f"Unable to read modem IMEI from slot {i}. Restarting modem and waiting for 30 seconds", black, normal)
                    send_ssh_command(f"wan_cli -i 10{i} softwarereset")
                    time.sleep(30)
                    if x == 10:
                        fail = True
    return fail, imeis


def wificheck(self, sap):
    coloredtext(self, "\nVerifying Wi-Fi slots", black, bold)
    fail = False
    wifis = {
    "wifi0": None,
    "wifi1": None,
    }
    for i, key in enumerate(wifis):
        wifislot = str(dbquery(f"wifi{i}", "articles", "articlenumber", f"{sap}")).strip()
        if wifislot != "yes":
            coloredtext(self, f"Slot {i} is unused", black, normal)

        else:
            mac = send_ssh_command(f"cat /sys/class/net/wlan{i}/address")[0].strip()
            if len(mac) == 17:
                coloredtext(self, f"Wi-Fi{i} verification PASS", green, normal)
                wifis.update({key: mac})
            elif len(mac) <= 16:
                coloredtext(self, f"Unable to read Wi-Fi from slot {i}", black, normal)
                coloredtext(self, f"Wi-Fi slot {i} verification FAIL", red, normal)
                fail = True
    return fail, wifis



def impinstallercheck(self):
    def stop(self):
        return
    self.pushButton_2.clicked.connect(stop(self))
    try:
        test = ""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("10.101.0.1", "22", "root", "imp", timeout=5)
        stdin, stdout, stderr = ssh.exec_command("/icomera/www/cgi-bin/status")
        lines = stdout.readlines()
        test = str(lines)
        ssh.close()
    except Exception:
        coloredtext(self, "Waiting for host to boot..", black, normal)
    if "Installation complete" in test:
        coloredtext(self, "Installation complete", green, normal)
        return
    impinstallercheck(self)
    

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('emptywindow.ui', self)
        self.show()
        self.actionBumblebee.triggered.connect(self.bumblebeegui)
        self.actionUpdate_Peak.triggered.connect(self.updatepeakgui)
#        self.actionIMP_installer_check.triggered.connect(self.impinstallergui)
        self.actionIMP_installer_check.triggered.connect(self.filipstartgui)

    def filipstartgui(self, serial):
        uic.loadUi('impinstallercheck.ui', self)
        self.pushButton.clicked.connect(self.filipteststart)

    def filipteststart(self, serial):
        mo = 1000000
        que = Queue()
        t1 = ThreadWithResult(target=filiptest, args=(self, serial,))
        t1.start()
        t1.join()
        test = t1.result
        coloredtext(self, f"{test}", black, normal)

    def bumblebeegui(self):
        uic.loadUi('mainwindow.ui', self)
        self.comboBox.addItems(orders)
        self.lineEdit.setFocus()
        self.actionUpdate_Peak.triggered.connect(self.updatepeakgui)
        self.lineEdit.returnPressed.connect(self.bumblebeestart)
        self.pushButton.clicked.connect(self.populate_systemid)
        self.pushButton_2.clicked.connect(self.copy_systemid)

    def updatepeakgui(self):
        uic.loadUi('updatepeak.ui', self)
        self.actionBumblebee.triggered.connect(self.bumblebeegui)
        customers = []
        with open ("customers.csv") as f:
            for row in f:
                customers.append(row.strip())
        self.comboBox.addItems(customers)
        self.lineEdit.setFocus()
        self.pushButton.clicked.connect(self.updatepeakstart)
        self.lineEdit.returnPressed.connect(self.updatepeakstart)

    #@pyqtSlot
    def impinstallergui(self):
        uic.loadUi('impinstallercheck.ui', self)
        self.pushButton.clicked.connect(coloredtext(self, "Starting", black, normal), impinstallercheck(self))


    def updatepeakstart(self):
        self.textBrowser.clear()
        coloredtext(self, "Starting..", black, normal)
        try:
            customer = str(self.comboBox.currentText()).strip()
            serial = str(self.lineEdit.text())
            browser = Browser(headless=True)
            browser.visit("https://peak.icomera.com/devices")
            browser.find_by_css('#user_email').fill('filip.malmberg@icomera.com')
            browser.find_by_css('#user_password').fill('abcd1234')
            coloredtext(self, "Signing in", black, normal)
            browser.is_element_visible_by_xpath("/html/body/div/div[4]/div[2]/div[3]/form/div/div/div/div[3]/div[2]/input", wait_time=10)
            browser.find_by_xpath("/html/body/div/div[4]/div[2]/div[3]/form/div/div/div/div[3]/div[2]/input").click()
            browser.reload()
            browser.find_by_css('#search').fill(f'{serial}')
            searchfield = browser.find_by_css('#search')
            searchfield.type(Keys.RETURN)
            coloredtext(self, "Updating information for device in Peak", black, normal)
            browser.find_by_xpath("/html/body/div/div[5]/div[1]/div[2]/form/p/input[2]").click()
            certificate_link = browser.find_by_xpath("//td[. = '{}']/following-sibling::td/a".format(serial)).first.click()
            browser.is_text_present('Edit:', wait_time=10)
            browser.find_by_css('#device_system_name').fill('{}'.format(serial))
            mac = browser.find_by_css('#device_mac')
            mac = mac.value
            mac = mac[4:]
            systemid = int(mac, 16)
            browser.find_by_css('#device_system_id').fill('{}'.format(systemid))
            browser.find_option_by_text(f'{customer}').first.click()
            browser.find_by_xpath("/html/body/div/div[5]/div[1]/div[2]/form/div[2]/input").click()
            coloredtext(self, "Saving..", black, normal)
            browser.is_text_present('Edit | Back', wait_time=10)
            coloredtext(self, "Verifying information..", black, normal)
            browser.reload()
            systemidcheck = browser.find_by_xpath("/html/body/div/div[5]/div[1]/div[2]/div[2]/div/div/div[1]/table/tbody/tr[6]").first.value
            customercheck = browser.find_by_xpath("/html/body/div/div[5]/div[1]/div[2]/div[2]/div/div/div[1]/table/tbody/tr[10]").first.value
            fail = False
            if str(systemid) not in systemidcheck:
                fail = True
            if customer not in customercheck:
                fail = True
            if fail == True:
                coloredtext(self, "Failed to update device. Please try again", red, bold)
            else:
                coloredtext(self, "Successfully updated device in Peak", green, bold)
            coloredtext(self, f"{customercheck}", black, normal)
            coloredtext(self, f"{systemidcheck}", black, normal)
        except Exception as e:
            heavyloadcheck = browser.is_text_present('heavy load', wait_time=10)
            if heavyloadcheck == True:
                coloredtext(self, "Peak is weak and can't handle the pressure.. Please try again.", black, bold)
            else:
                coloredtext(self, "Something went wrong...", red, bold)
                coloredtext(self, f"{e}", black, normal)

    def bumblebeestart(self):
        fail = False
        self.textBrowser.clear()
        mo = str(self.comboBox.currentText())
        mo = mo.split(" ")
        mo = mo[0]
        sap = dbquery("moarticle", "manufacturingorder", "monumber", mo)
        dbimp = dbquery("impversion", "articles", "articlenumber", sap).replace("\n", "").strip()
        dbroutertype = dbquery("routertype", "articles", "articlenumber", sap)
        projectid = dbquery("projectid", "articles", "articlenumber", sap)
        serial = str(self.lineEdit.text())
        coloredtext(self, f"Given serial from operator is: {serial}", black, normal)
        coloredtext(self, f"SAP number is: {sap}", black, normal)
        unitid = str(dbquery("unitid", "configuredunits", "serial", serial)).strip()
        if unitid != "()":
            coloredtext(self, "\nThis unit has already been configured. Duplicates are not allowed in the database", red, bold)
            return
        imp = send_ssh_command("/lib/api/system.imageversion")[0].replace("\n", "").strip()
        coloredtext(self, f"Installed IMP is: {imp}\n", black, normal)
        if imp != dbimp:
            print(imp)
            print(dbimp)
            coloredtext(self, "Installed IMP does not match specified IMP in database", black, normal)
            fail = True
        else:
            coloredtext(self, "IMP verification PASS", green, normal)
        mac = send_ssh_command("cat /sys/class/net/eth0/address")[0].replace("\n", "").strip()
        if len(mac) == 17:
            coloredtext(self, "MAC verification PASS", green, normal)
        else:
            coloredtext(self, "Unable to fetch MAC from IMP", black, normal)
            coloredtext(self, "MAC verification FAIL", red, normal)
            fail = True
        impserial = send_ssh_command("cat /var/log/persistent/serial_nr")[0].replace("\n", "").strip()
        if len(impserial) < 6:
            coloredtext(self, "Unable to fetch serial from IMP", black, normal)
            fail = True
        if impserial == serial:
            coloredtext(self, "Serial verification PASS", green, normal)
        else:
            coloredtext(self, "Serial verification FAIL", red, normal)
            fail = True
        improutertype = send_ssh_command("/lib/api/system.hardwareversion")[0].replace("\n", "").strip().split(" ")[0]
        if dbroutertype == improutertype:
            coloredtext(self, "Router hardware verification PASS", green, normal)
        else:
            coloredtext(self, f"Router hardware verification FAIL {improutertype}", red, normal)
            fail = True
        if dbroutertype == "X3" or dbroutertype == "R01" or dbroutertype == "R02" or dbroutertype == "R02/R04":
            simcheck, sims, simids = simcheckx3x5(self, sap)
            if simcheck == True:
                fail = True
        modemverification, modems = modemcheck(self, sap)
        if modemverification == True:
            fail = True
        modemfirmwareverification, firmwares = modemfirmwarecheck(self, sap)
        if modemfirmwareverification == True:
            fail = True
        imeistaus, imeis = modemimeicheck(self, sap)
        if imeistaus == True:
            fail = True
        wifistatus, wifis = wificheck(self, sap)
        if wifistatus == True:
            fail = True
        if fail == False:
            dbupload(self, sap, projectid, mo, serial, mac, dbroutertype, imp, modems, firmwares, imeis, wifis, sims, simids)
        else:
            coloredtext(self, "Overall status FAIL", red, normal)

    def populate_systemid(self):
        try:
            systemid = get_systemid()
            self.lineEdit_2.setText(str(systemid))
        except Exception:
            pass

    def copy_systemid(self):
        clipboard = QApplication.clipboard()
        systemid = self.lineEdit_2.text()
        clipboard.setText(systemid)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()