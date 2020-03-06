# coding=utf-8

import serial
import RPi.GPIO as GPIO
import time
import serial
import struct
import datetime

ADDRESS_1 = '/dev/ttySC0'
ADDRESS_2 = '/dev/ttySC1'
PIN_S1 = 6
PIN_R1 = 13
PIN_S2 = 19
PIN_R2 = 26


# funzione che verifica se il PMS è acceso o spento, ritorna false se è spento altrimenti true se è acceso:
def is_on(pin_s):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_s,GPIO.OUT)
        value=GPIO.input(pin_s)

        if value==0:
            # print("spenti")
            return False
        elif value==1:
            # print("accesi")
            return True
    except:
        raise PMS_Exception



class PMS_Exception(Exception):
    def set(self, numb):
        self.number = numb

class PmsClass():

    def __init__(self, address, pin_set, pin_reset):

        self.pin_s = pin_set
        self.pin_r = pin_reset
        self.serial = serial.Serial(address, 9600, timeout=0.7)

    def get_data(self):

        self.serial.flushInput()
        time.sleep(0.7)
        data = None
        try:
            for i in range(1, 3):
                verify = False
                time.sleep(0.1)
                for l in range(1, 10):
                    c = self.serial.read(1)  # 1st header
                    if len(c) >= 1:
                        if c[0] == 0x42:
                            c = self.serial.read(1)  # 2nd header
                            if len(c) >= 1:
                                if c[0] == 0x4d:
                                    verify = True
                                    break
                if verify:
                    time.sleep(0.7)
                    pms_data = self.serial.read(30)
                    check = 0x42 + 0x4d
                    for c in pms_data[0:28]:
                        check += c
                    pms7003_data = struct.unpack('!HHHHHHHHHHHHHBBH', pms_data)
                    if check != pms7003_data[15]:
                        continue
                    data = []
                    data.append(("pm1", pms7003_data[1]))
                    data.append(("pm2_5", pms7003_data[2]))
                    data.append(("pm10", pms7003_data[3]))
            if data==None:
                raise Exception("Nessun dato, sensore disconnesso")
        except Exception as error:
            raise PMS_Exception(str(error))
        return data

    def reset(self):
        try:
            GPIO.setup(self.pin_r, GPIO.OUT)
            GPIO.output(self.pin_r, 0)
            time.sleep(3)
            GPIO.cleanup(self.pin_r)
        except:
            raise PMS_Exception

    def turn_on(self):
        try:
            GPIO.setup(self.pin_s, GPIO.OUT)
            GPIO.output(self.pin_s, 1)
        except:
            raise PMS_Exception


    def switch_off(self):
        try:
            GPIO.setup(self.pin_s, GPIO.OUT)
            GPIO.output(self.pin_s, 0)
            self.serial.flushInput()
            while True:
                try:
                    a = self.serial.read(1)
                    if len(a) >= 1:
                        continue
                    else:
                        # print("Non c'e' nulla")
                        return True
                except Exception as error:
                    print("\n\n-----------")
                    print(error)
                    print("\n\n-------------------")
                    return True
        except:
            raise PMS_Exception

    #-------FUNZIONI PER IL TEST------------

    def get_data_test(self):
        iter_int=None
        iter_est=None
        self.serial.flushInput()
        self.serial.flushOutput()
        data = None
        for i in range(1, 3):
            iter_est=i
            verify = False
            time.sleep(0.1)
            for l in range(1, 10):
                iter_int=l
                c = self.serial.read(1)  # 1st header
                if len(c) >= 1:
                    if c[0] == 0x42:
                        c = self.serial.read(1)  # 2nd header
                        if len(c) >= 1:
                            if c[0] == 0x4d:
                                verify = True
                                break
            if verify:
                time.sleep(0.7)
                pms_data = self.serial.read(30)
                check = 0x42 + 0x4d
                for c in pms_data[0:28]:
                    check += c
                pms7003_data = struct.unpack('!HHHHHHHHHHHHHBBH', pms_data)
                if check != pms7003_data[15]:
                    continue
                data = []
                data.append(("pm1", pms7003_data[1]))
                data.append(("pm2_5", pms7003_data[2]))
                data.append(("pm10", pms7003_data[3]))
	# print('Ho fatto il get_data_test')
	# print(data)
        return data,iter_est,iter_int

    def reset_test(self):
        GPIO.setup(self.pin_r, GPIO.OUT)
        GPIO.output(self.pin_r, 0)
        time.sleep(3)
        GPIO.cleanup(self.pin_r)
	# print('Ho fatto il reset_test')

    def turn_on_test(self):
        GPIO.setup(self.pin_s, GPIO.OUT)
        GPIO.output(self.pin_s, 1)
	# print('Ho fatto il turn_on_test')

    def switch_off_test(self):
	# print('Sto in switch_off_test')
        GPIO.setup(self.pin_s, GPIO.OUT)
        GPIO.output(self.pin_s, 0)
        self.serial.flushInput()
        while True:
            try:
                a = self.serial.read(1)
                if len(a) >= 1:
                    continue
                else:
                    # print("Non c'e' nulla")
                    return True
            except Exception as error:
                print("\n\n-----------")
                print(error)
                print("\n\n-------------------")
                return True

def crea_csv_file(nome_file, intestazione):
    with open(nome_file, 'w+') as file:
        file.write(intestazione)

def aggiorna_csv_file(nome_file, nuova_riga):
    with open(nome_file, 'a') as file:
        file.write(nuova_riga)

def test():
    GPIO.setmode(GPIO.BCM)
    pms1 = {"add": '/dev/ttySC0', "pin_s": 6, "pin_r": 13}
    pms2 = {"add": '/dev/ttySC1', "pin_s": 19, "pin_r": 26}

    # Istanza primo pms
    istanza = PmsClass(pms1['add'], pms1['pin_s'], pms1['pin_r'])
    # Istanza del secondo pms
    istanza2 = PmsClass(pms2['add'], pms2['pin_s'], pms2['pin_r'])

    istanza.turn_on_test()
    istanza2.turn_on_test()

    intestazione = "Timestamp,Sensore,Num_iter,Iteraz_est, Iteraz_int,PM1,PM2_5,PM10\n"
    nomefile = 'result1.csv'
    nomefile2 = 'result2.csv'
    crea_csv_file(nomefile, intestazione)
    crea_csv_file(nomefile2, intestazione)

    i = 0

    #while True:
    for i in range(4):
        print("\n--------------Iterazione n: " + str(i+1) + "-----------------\n")
        i = i + 1
        num_iter = i
        try:
            pms_data = istanza.get_data_test()
            print("sensore1: " + str(pms_data[0]))
            pms1 = "Sensore 1"

            if pms_data[0] != None:
                dati1 = pms_data[0]
                dato11 = dati1[0][1]
                dato12 = dati1[1][1]
                dato13 = dati1[2][1]
            else:
                dato11 = None
                dato12 = None
                dato13 = None

            timestamp1 = datetime.datetime.now()

            nuova_riga = str(timestamp1) + "," + str(pms1) + "," + str(i) + "," + str(pms_data[1]) + "," + str(pms_data[2]) + "," + str(dato11) + "," + str(dato12) + "," + str(dato13) + "\n"
            aggiorna_csv_file(nomefile, nuova_riga)

            pms_data2 = istanza2.get_data_test()
            print("sensore2: " + str(pms_data2[0]))
            pms2 = "Sensore 2"
            if pms_data2[0] != None:
                dati2 = pms_data2[0]
                dato21 = dati2[0][1]
                dato22 = dati2[1][1]
                dato23 = dati2[2][1]
            else:
                dato21 = None
                dato22 = None
                dato23 = None

            timestamp2 = datetime.datetime.now()

            nuova_riga2 = str(timestamp2) + "," + str(pms2) + "," + str(i) + "," + str(pms_data2[1]) + "," + str(pms_data2[2]) + "," + str(dato21) + "," + str(dato22) + "," + str(dato23) + "\n"
            aggiorna_csv_file(nomefile2, nuova_riga2)

            time.sleep(20) #180

        except Exception as error:
            print(error)

    istanza.switch_off_test()
    istanza2.switch_off_test()

if __name__ == '__main__':
    test()
