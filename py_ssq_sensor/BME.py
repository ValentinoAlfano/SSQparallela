# coding=utf-8

from __future__ import print_function
import bme680
import time
import json
import os, sys, traceback, datetime


class BME_Exception(Exception):
    pass


class BME():
    def __init__(self, test=False):

        self.__initializeBME(test=test)

    def __initializeBME(self, test=False):
        try:
            sensor = bme680.BME680()
            sensor.set_humidity_oversample(bme680.OS_2X)
            sensor.set_pressure_oversample(bme680.OS_4X)
            sensor.set_temperature_oversample(bme680.OS_8X)
            sensor.set_filter(bme680.FILTER_SIZE_3)

            sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
            sensor.set_gas_heater_temperature(320)
            sensor.set_gas_heater_duration(150)
            sensor.select_gas_heater_profile(0)
            self.sensor = sensor
        except Exception as error:
            if test == True:
                raise BME_Exception
            else:
                raise error

    def get_data(self):

        data = None
        try:
            data = self.get_data_test()
        except Exception as error:
            raise BME_Exception
        return data

    def get_data_test(self):
        sensor = self.sensor

        for i in range(10):
            data = []
            #print("-----Iterazione interna al bme " + str(i))
            if sensor.get_sensor_data():
                data.append({"key": "temperatura", "value": sensor.data.temperature})
                data.append({"key": "umidita", "value": sensor.data.humidity})
                data.append({"key": "pressione", "value": sensor.data.pressure})
                if sensor.data.heat_stable:
                    voc = ((sensor.data.gas_resistance) / 1000)
                    data.append({"key": "voc", "value": voc})
                    break

            else:
                time.sleep(1)
        if len(data) > 0:
            return data
        else:
            return None

    def get_row_data(self):
        sensor = self.sensor
        if sensor.get_sensor_data():
            temp = sensor.data.temperature
            hum = sensor.data.humidity
            press = sensor.data.pressure

            if sensor.data.heat_stable:
                gas_resistance = sensor.data.gas_resistance
                return (temp, hum, press, gas_resistance)
            else:
                return None
        else:
            return None


def start_baseLine():  # raise BME_Exception, Baseline_Eception

    bme = BME()
    hum_data = []
    gas_data = []

    sensor = bme.sensor

    hum_bl = 0
    gas_bl = 0

    print("Loading BaseLine...")

    for i in range(50):
        if sensor.get_sensor_data():
            hum_data.append(sensor.data.humidity)
            if sensor.data.heat_stable:
                gas_data.append(sensor.data.gas_resistance)
        time.sleep(5)
        print("Mancano " + str(250 - ((i + 1) * 5)) + " secondi ", end='\r')
        sys.stdout.flush()
    if hum_data and gas_data:
        for values in hum_data:
            hum_bl = hum_bl + values
        hum_bl = hum_bl / len(hum_data)
        for values in gas_data:
            gas_bl = gas_bl + values
        gas_bl = gas_bl / len(gas_data)
    else:
        print("Errore BME : Non ci sono dati per le BaseLine")

    print("BaseLine OK!                   ")


# ----------FUNZIONI UTILITARIE--------------

def create_csv_file(nomefile, intestazione):
    with open(nomefile, 'w+') as file:
        file.write(intestazione + "\n")


def update_csv_file(nomefile, nuovariga):
    with open(nomefile, 'a') as file:
        file.write(nuovariga + "\n")


file_error_name = "BME_errorlog.txt"


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
    complete_path = os.path.join('/home/pi/Desktop/BME', 'ErrorLog_BME')
    complete_file_error_name = timeforpath + file_error_name
    if not os.path.isdir(complete_path):
        os.makedirs(complete_path)

    f = open(complete_path + "/" + complete_file_error_name, "a")
    f.write(str("\n\n------------" + line + "\n"))
    f.close()
    print("ErrorLog riportato sul file: " + file_error_name)


# -------------------------------------------

# ---------FUNZIONI DI TEST------------------
def test():
    bme = BME()

    stringa = ''
    data_bme = bme.get_data_test()

    for d in data_bme:
        print(d['key'] + " :" + str(d['value']))

    temp = str(data_bme[0]['value'])
    hum = str(data_bme[1]['value'])
    press = str(data_bme[2]['value'])
    voc = str(data_bme[3]['value'])
    stringa += temp + "," + hum + "," + press + "," + voc

    return stringa


def test_loop():
    date = datetime.datetime.now().strftime("%Y-%m-%d___%H-%M-%S")
    nomefile = 'BMEresult_' + date + '.csv'
    intestazione = 'iterazione,timestamp,temp,hum,pressione,voc'
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
            nuova_riga += '-,-,-,-'
            save_error(error)
        finally:
            update_csv_file(nomefile, nuova_riga)
        i += 1
        time.sleep(20)


def test_2():
    bme = BME()

    data = bme.get_data_test()
    for d in data:
        print(d)

    with open('result_bme.txt', 'a+') as file:
        json.dump(data, file, ensure_ascii=False)


def calibration_test():
    bme = BME()
    print("----INSERIMENTO PARAMETRI MANUALI----\n")

    while True:
        num_cicli_str = input("Inserire numero di cicli per la  calibrazione: ")
        try:
            num_cicli = int(num_cicli_str)
            break
        except Exception as error:
            print("Inserire un valore valido.")
    while True:
        c_break_time_str = input("Inserire tempo di attesa  tra una lettura e l'altra per la CALIBRAZIONE (secondi): ")
        try:
            c_break_time = float(c_break_time_str)
            break
        except Exception as error:
            print("Inserire un valore valido.")
    while True:
        break_time_str = input(
            "Inserire tempo di attesa  tra una lettura e l'altra per la STABILIZZAZIONE FORZATA (secondi): ")
        try:
            break_time = float(break_time_str)
            break
        except Exception as error:
            print("Inserire un valore valido.")

    print("RIEPILOGO PARAMETRI:")
    print(
        "\nCicli di lettura per calibrazione: {}\nTempo di attesa Calibrazione: {} \n Tempo di attesa Stabilizzazione Forzata: {}".format(
            num_cicli, c_break_time, break_time
        ))
    for _ in range(5):
        print('.')
        time.sleep(1)

    print("\n----CALIBRAZIONE INIZIATA---")
    for i in range(num_cicli):
        data_calibration = bme.get_row_data()
        time.sleep(c_break_time)
        print('.')
    print("\n----CALIBRAZIONE FINITA---")

    if data_calibration != None:

        c_temp = data_calibration[0]
        c_hum = data_calibration[1]
        c_press = data_calibration[2]
        c_gas_r = data_calibration[3]
        print("\nLa calibrazione su {} letture si è conclusa con successo,\n ed ha generato i seguenti valori: ".format(
            num_cicli))
        print(" TEMP {}  HUM {} PRESS {}  GAS_R {}".format(c_temp, c_hum, c_press, c_gas_r))
    else:
        print("\nLa calibrazione su {} letture NON si è conclusa con successo.".format(num_cicli))
        exit(-1)

    print("INIZIALIZZAZIONE STABILIZZAZIONE FORZATA")
    for _ in range(5):
        print('.')
        time.sleep(1)

    print("\n\n----STABILIZZAZIONE FORZATA INIZIATA----")
    for _ in range(3):
        print("Ctrl+C per interrompere.")
        time.sleep(1)

    try:
        while True:
            data = bme.get_row_data()
            if data:
                temp = data[0]
                hum = data[1]
                press = data[2]
                gas_r = data[3]
            else:
                temp = None
                hum = None
                press = None
                gas_r = None

            print("\n TEMP {}  HUM {} PRESS {}  GAS_R {}".format(temp, hum, press, gas_r))
            time.sleep(break_time)
    except KeyboardInterrupt:
        print("\n\n-------------RISULTATI FINALI----------------")
        print("Parametri inseriti : ")
        print("\nCicli di Calibrazione {}\nPeriodo di Calibrazione {}\nPeriodo Stabilizzazione Forzata {}".format(
            num_cicli, c_break_time, break_time
        ))
        print("\n---DATI DELLA CALIBRAZIONE: ")
        print(" TEMP {}  HUM {}  PRESS {}  GAS_R {}".format(c_temp, c_hum, c_press, c_gas_r))
        print("\n----DATI DELLA STABILIZZAZIONE FORZATA")
        print(" TEMP {}  HUM {}  PRESS {}  GAS_R {}".format(temp, hum, press, gas_r))

        print("----DELTA")
        d_temp = temp - c_temp
        d_hum = hum - c_hum
        d_press = press - c_press
        d_gas_r = gas_r - c_gas_r
        print(" TEMP {} \n HUM {} \n PRESS {} \n GAS_R {}".format(d_temp, d_hum, d_press, d_gas_r))


if __name__ == '__main__':
    # start_baseLine()
    # test_loop()
    calibration_test()

