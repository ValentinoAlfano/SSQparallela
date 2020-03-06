# coding=utf-8

import os, urllib,time,sys,traceback
import datetime
import subprocess
from functools import wraps
import errno
import os
import signal
from .timeout import timeout



class ANEM_Exception(Exception):

    pass





class ANEM():

    def __init__(self,path_exe='/home/pi/Desktop/TX23',file_path="/home/pi/anem.txt"):
        self.path=path_exe
        self.my_path=file_path

    def get_data(self):

        data = None
        try:
            data=self.get_data_test()
        except Exception as error:
            raise ANEM_Exception
        return data

   

    def get_data_test(self):

        data=[]
        
        @timeout(30, os.strerror(errno.ETIMEDOUT))
        def long_running_function():
            try :
                    direct_output = subprocess.check_output('/home/pi/Desktop/TX23/readTX23', shell=True)
                    param = direct_output.split()
                    for i in range(len(param)) :
                        param[i] = int(param[i])
                    return param
            except Exception as e :
                return None

        param = long_running_function()

        if (param != None) :
            data.append({"key":"direzione_vento", "value":param[0]})
            data.append({"key": "intensita_vento", "value": param[1]})             
            return data
        else:
            return None


def test():
    anem=ANEM()
    data=anem.get_data_test()
    stringa=''

    for d in data:
        print(d['key'] +" :"+ str(d['value']))

    direz = str(data[0]['value'])
    inten=str(data[1]['value'])

    stringa+=direz+","+inten
    return stringa




def test_loop():
    date=datetime.datetime.now().strftime("%Y-%m-%d___%H-%M-%S")
    nomefile='ANEMresult_'+date+'.csv'
    intestazione='iterazione,timestamp,direzione,intensita'
    create_csv_file(nomefile,intestazione)
    i=1

    while True:
        print("\n\n\n------ITERAZIONE N: "+str(i))
        nuova_riga = ''
        date_iteration = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        nuova_riga+=str(i)+","+date_iteration+","
        try:
            nuova_riga+=test()

        except Exception as error:
            nuova_riga+='-,-'
            save_error(error)
        finally:
            update_csv_file(nomefile,nuova_riga)
        i+=1
        time.sleep(10)

def create_csv_file(nomefile,intestazione):
    with open(nomefile,'w+') as file:
        file.write(intestazione+"\n")

def update_csv_file(nomefile,nuovariga):
    with open(nomefile,'a') as file:
        file.write(nuovariga+"\n")

file_error_name = "ANEM_errorlog.txt"

def save_error(error):
    print(error)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    t = (traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(t)
    trac = ''
    for x in t:
        trac += x
    line = "Time: " + str(datetime.datetime.now()) + "\n" + str(error) + "\n" + trac
    timex = datetime.datetime.now()
    timeforpath = timex.strftime('%Y-%m-%d')
    print(timeforpath)
    complete_path = os.path.join('/home/pi/Desktop/ANEM', 'ErrorLog_ANEM')
    complete_file_error_name = timeforpath + file_error_name
    if not os.path.isdir(complete_path):
        os.makedirs(complete_path)

    f = open(complete_path + "/" + complete_file_error_name, "a")
    f.write(str("\n\n------------" + line + "\n"))
    f.close()
    print("ErrorLog riportato sul file: " + file_error_name)



if __name__ == '__main__':
    test_loop()

