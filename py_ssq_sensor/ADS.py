# coding=utf-8

import Adafruit_ADS1x15
import time
import os, sys, traceback, datetime

#input = raw_input

ADDRESS_1 = 0X48
ADDRESS_2 = 0X49
ADDRESS_3 = 0X4A
ADDRESS_4 = 0X4B

GAS_NO2 = 'no2'
GAS_CO = 'co'
GAS_H2S = 'h2s'
GAS_SO2 = 'so2'
GAS_O3 = 'o3'

PIN_A = 0
PIN_B = 1

'''
                                       ADS1015          ADS1115
           // 2/3x gain +/- 6.144V  1 bit = 3mV      0.1875mV (default)
          // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
         // 2x gain   +/- 2.048V  1 bit = 1mV      0.0625mV
        // 4x gain   +/- 1.024V  1 bit = 0.5mV    0.03125mV
       // 8x gain   +/- 0.512V  1 bit = 0.25mV   0.015625mV
      // 16x gain  +/- 0.256V  1 bit = 0.125mV  0.0078125mV

GAIN = 4
mlv = 0.03125
'''


class GAS:
    def __init__(self, name, id, k1, k2, sens):
        self.name = name  # NOME DEL GAS
        self.id = id  # ID DELLA CELLA
        self.k1 = k1  # C1,We0
        self.k2 = k2  # C2,Aux0
        self.sens = sens  # SENSIBILITA' CELLA


class ADS_Exception(Exception):

    def set(self, numb):
        self.number = numb


class ADS:
    GAIN = 4
    mlv = 0.03125

    def __init__(self, address, gas_a, gas_b, test=False):
        self.address = address
        self.gas_a = gas_a
        self.gas_b = gas_b
        if test:
            self.ads = Adafruit_ADS1x15.ADS1115(address)
        else:
            self.initialize_ads(address)

    def initialize_ads(self, address):
        try:
            self.ads = Adafruit_ADS1x15.ADS1115(address)

        except:
            raise ADS_Exception

    # ------funzioni di test-------------------
    def get_raw_data_test(self, pin):

        data = []

        if pin == PIN_A:
            pin1 = 0
            pin2 = 1
            data.append((self.ads.read_adc(pin1, gain=self.GAIN)) * self.mlv)  # op1
            data.append((self.ads.read_adc(pin2, gain=self.GAIN)) * self.mlv)  # op2

        if pin == PIN_B:
            pin1 = 2
            pin2 = 3
            data.append((self.ads.read_adc(pin1, gain=self.GAIN)) * self.mlv)  # op1
            data.append((self.ads.read_adc(pin2, gain=self.GAIN)) * self.mlv)  # op2

        # time.sleep(2)
        return data

    def get_processed_data_test(self, pin, nt):
        # print("sono dentro processed_data")
        coeff = 1
        if pin == PIN_A:
            if (self.gas_a.name == GAS_NO2) :
                coeff = 1
            elif (self.gas_a.name == GAS_H2S) :
                coeff = 1
            elif (self.gas_a.name == GAS_O3) :
                coeff = 1.96*0.044322311851786186 #1/22.562
            # print("sono nel PIN-A")
            data_row_a = self.get_raw_data_test(PIN_A)
            # print("ho letto i grezzi {} ".format(data_row_a))
            # print(data_row_a)
            elab_data_a = (((data_row_a[0] - self.gas_a.k1) - nt * (data_row_a[1] - self.gas_a.k2)) / self.gas_a.sens) * coeff
            # print("dati elaborati {}".format(elab_data_a))
            return {"key": self.gas_a.name, "value": abs(elab_data_a)}
        if pin == PIN_B:
            if (self.gas_b.name == GAS_CO) :
                coeff = 0.00196305880253413*0.13 # (44/22414 * 0.13)
            elif (self.gas_b.name == GAS_SO2) :
                coeff = 1
            # print("Sono nel PIN-B")
            data_row_b = self.get_raw_data_test(PIN_B)
            # print(data_row_b)
            elab_data_b = (((data_row_b[0] - self.gas_b.k1) - nt * (data_row_b[1] - self.gas_b.k2)) / self.gas_b.sens) * coeff
            # print("dati elaborati {}".format(elab_data_b))
            return {"key": self.gas_b.name, "value": abs(elab_data_b)}

    # ------funzioni ufficiali-----------------
    def get_processed_data(self, pin, nt):
        try:
            return self.get_processed_data_test(pin, nt)
        except:
            raise ADS_Exception

    def get_raw_data(self, pin):
        try:
            return self.get_raw_data(pin)
        except:
            raise ADS_Exception

    # Alias-------------
    get_elaborated_data = get_processed_data_test


def test_raw():
    gas = GAS("test", "aaa", 1, 1, 1)

    ads_1 = ADS(ADDRESS_1, gas, gas, test=True)
    ads_2 = ADS(ADDRESS_2, gas, gas, test=True)
    ads_3 = ADS(ADDRESS_3, gas, gas, test=True)
    ads_4 = ADS(ADDRESS_4, gas, gas, test=True)

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_1)
    a = ads_1.get_raw_data_test(0)
    b = ads_1.get_raw_data_test(1)
    print("\n\n--Dati ADS1----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_2)
    a = ads_2.get_raw_data_test(0)
    b = ads_2.get_raw_data_test(1)
    print("\n\n--Dati ADS2----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_3)
    a = ads_3.get_raw_data_test(0)
    b = ads_3.get_raw_data_test(1)
    print("\n\n--Dati ADS3----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_4)
    a = ads_4.get_raw_data_test(0)
    b = ads_4.get_raw_data_test(1)
    print("\n\n--Dati ADS4----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))


def test_elaborated():
    stringa = ''

    gas = GAS("test", "aaa", 1, 1, 1)

    ads_1 = ADS(ADDRESS_1, gas, gas, test=True)
    ads_2 = ADS(ADDRESS_2, gas, gas, test=True)
    ads_3 = ADS(ADDRESS_3, gas, gas, test=True)
    ads_4 = ADS(ADDRESS_4, gas, gas, test=True)

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_1)
    a = ads_1.get_elaborated_data(0, 1)
    b = ads_1.get_elaborated_data(1, 1)
    print("\n--Dati ELABORATI ADS1----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))
    stringa += str(a['value']) + "," + str(b['value']) + ","

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_2)
    a = ads_2.get_elaborated_data(0, 1)
    b = ads_2.get_elaborated_data(1, 1)
    print("\n--Dati ELABORATI ADS2----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))
    stringa += str(a['value']) + "," + str(b['value']) + ","

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_3)
    a = ads_3.get_elaborated_data(0, 1)
    b = ads_3.get_elaborated_data(1, 1)
    print("\n--Dati ELABORATI ADS3----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))
    stringa += str(a['value']) + "," + str(b['value']) + ","

    # Lettura dei dati grezzi da entrambe le coppie di pin (ADS_4)
    a = ads_4.get_elaborated_data(0, 1)
    b = ads_4.get_elaborated_data(1, 1)
    print("\n--Dati ELABORATI ADS4----------")
    print("prima coppia di pin: " + str(a))
    print("seconda coppia di pin: " + str(b))
    stringa += str(a['value']) + "," + str(b['value'])

    return stringa


def create_csv_file(nomefile, intestazione):
    with open(nomefile, 'w+') as file:
        file.write(intestazione + "\n")


def update_csv_file(nomefile, nuovariga):
    with open(nomefile, 'a') as file:
        file.write(nuovariga + "\n")


file_error_name = "ADS_errorlog.txt"


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
    complete_path = os.path.join('/home/pi/Desktop', 'ErrorLog_testADS')
    complete_file_error_name = timeforpath + file_error_name
    if not os.path.isdir(complete_path):
        os.makedirs(complete_path)

    f = open(complete_path + "/" + complete_file_error_name, "a")
    f.write(str("\n\n------------" + line + "\n"))
    f.close()
    print("ErrorLog riportato sul file: " + file_error_name)


def test_singolo_ads():
    gas = GAS("test", "aaa", 1, 1, 1)

    ads_1 = ADS(ADDRESS_1, gas, gas, test=True)
    data = ads_1.get_elaborated_data(PIN_A, 1)
    print(data)
    print("\n")
    data = ads_1.get_elaborated_data(PIN_A, 1)
    print(data)


def main():
    str_input = input("Digitare: \n-1 DATI GREZZI\n-2 DATI ELABORATI\n-esc USCIRE\n")
    int_input = -9999
    try:

        int_input = int(str_input)

    except:
        pass

    if int_input == 1:
        while True:
            test_raw()

    elif int_input == 2:
        date = datetime.datetime.now().strftime("%Y-%m-%d___%H-%M-%S")
        nomefile = 'ADSresult_' + date + '.csv'
        intestazione = 'Iterazione,Data,ADS1_A,ADS1_B,ADS2_A,ADS2_B,ADS3_A,ADS3_B,ADS4_A,ADS4_B'
        create_csv_file(nomefile, intestazione)
        i = 1

        while True:
            print("\n\n\n------ITERAZIONE N: " + str(i))
            nuova_riga = ''
            date_iteration = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            nuova_riga += str(i) + "," + date_iteration + ","
            try:
                nuova_riga += test_elaborated()
            except Exception as error:
                nuova_riga += '-,-,-,-,-,-,-,-'
                save_error(error)
            finally:
                update_csv_file(nomefile, nuova_riga)
            i += 1
            time.sleep(60)

    else:
        print("CHIUDO.\n")


def test_eccezioni():
    gas = GAS("test", "aaa", 1, 1, 1)

    ads_1 = ADS(ADDRESS_1, gas, gas, test=True)

    i = 1
    while True:
        print("\n----Iterazione n: " + str(i))
        data = ads_1.get_processed_data(PIN_A, 1)
        print(data)
        data = ads_1.get_processed_data(PIN_B, 1)
        print(data)
        i += 1
        time.sleep(1)


if __name__ == '__main__':
    main()

    # try:
    #     test_eccezioni()
    # except ADS_Exception:
    #     print("Errore gestito")