# coding=utf-8


import serial
import time
import json
import os
import sys
import traceback
import datetime
import io


def ddmm2dd(ddmm):
    #print("dentro ddmm2dd")
    ddmmstr = str(ddmm)

    if not ddmm:
        raise Exception("\n Errore: coordinate non rilevate. \n")

    ddSplitted = ddmmstr.split('.')
    dd = ddSplitted[0]
   # print("ancora dentro ddmm2dd")    
    mmm = ddSplitted[1]
    if len(mmm) == 1:
        mmm += '0'
    mm1 = mmm[0] + mmm[1]
    mm2 = ''
  #  print("ancora dentro ddmm2dd") 
    for i in range(2, len(mmm)):
        mm2 += mmm[i]
    a = float(mm1 + '.' + mm2) / 60
  #  print("a: " + str(a))
    dd = float(dd) + a
   # print("dd: " + str(dd))
    return float(dd)


class GPS_Exception(Exception):
    pass


class GPS():

    def __init__(self, port="/dev/ttyUSB1", baudrate=115200):
        self.ser = serial.Serial(port, baudrate)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        self.time = ""
        self.latitude = ""
        self.longitude = ""

    def get_data_test(self):
        condition = True
        data = None
        latitude = None
        longitude = None
        data_to_ret = []
        self.sio.flush()
        #self.ser.flushInput()
        while condition:
            line = self.sio.readline()
	    #line = self.ser.readline()
            #print(type(line))
            if "GPRMC" in str(line):
                #print("Sono dentro if GPRMC")
                data = str(line)
                condition = False

        # print(data)
        vet_errore = []
        if data != None:
            try:
                #print(data)
                data = data.split(',')
               # print("data[3]: "+str(data[3]))

                latitude = ddmm2dd((float(data[3])) / 100)
                #print("data[5]: "+str(data[5]))
                longitude = ddmm2dd((float(data[5])) / 100)
                data_to_ret.append({"key": "latitude", "value": latitude})
                data_to_ret.append({"key": "longitude", "value": longitude})
                return data_to_ret
            except Exception as error:
                # print("ERRORE")
                # print(error)
                # return None
                # print(traceback.format_exc())
                vet_errore.append({"key": None, "value": error})
                return vet_errore
        else:
            vet_errore.append({"key": None, "value": None})
            return vet_errore

    def get_data(self):
        try:
            return self.get_data_test()
        except:
            raise GPS_Exception
#-------------------------------------------------------


def create_csv_file(nomefile, intestazione):
    with open(nomefile, 'w+') as file:
        file.write(intestazione + "\n")


def update_csv_file(nomefile, nuovariga):
    with open(nomefile, 'a') as file:
        file.write(nuovariga + "\n")

file_error_name = "GPS_errorlog.txt"


def save_error(error):
    print(error)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    t = (traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(t)
    trac = ''
    for x in t:
        trac += x
    line = "Time: " + \
        str(datetime.datetime.now()) + "\n" + str(error) + "\n" + trac
    timex = datetime.datetime.now()
    timeforpath = timex.strftime('%Y-%m-%d')
    print(timeforpath)
    complete_path = os.path.join('/home/pi/Desktop/GPS', 'ErrorLog_GPS')
    complete_file_error_name = timeforpath + file_error_name
    if not os.path.isdir(complete_path):
        os.makedirs(complete_path)

    f = open(complete_path + "/" + complete_file_error_name, "a")
    f.write(str("\n\n------------" + line + "\n"))
    f.close()
    print("ErrorLog riportato sul file: " + file_error_name)


def test():
    gps = GPS()
    data = gps.get_data_test()

    stringa = ''
    if data != None:
        for d in data:
            print(str(d['key']) + " :" + str(d['value']))
        latitude = str(data[0]['value'])
        longitude = str(data[0]['value'])

        stringa += latitude + "," + longitude
    return stringa


def test_loop():
    date = datetime.datetime.now().strftime("%Y-%m-%d___%H-%M-%S")
    nomefile = 'GPSresult_' + date + '.csv'
    intestazione = 'iterazione,timestamp,latitude,longitude'
    create_csv_file(nomefile, intestazione)
    i = 1

    while True:
        print("\n\n\n------ITERAZIONE N: " + str(i))
        nuova_riga = ''
        date_iteration = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        nuova_riga += str(i) + "," + date_iteration + ","
        try:
            nuova_riga += test()
        except Exception as error:
            nuova_riga += '-,-'
            save_error(error)
        finally:
            update_csv_file(nomefile, nuova_riga)
        i += 1
        time.sleep(20)


if __name__ == "__main__":
    print(test())
    test_loop()
