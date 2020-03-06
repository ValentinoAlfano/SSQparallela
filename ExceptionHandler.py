# coding=utf-8


from __future__ import print_function
import traceback
import logging
import CONFIG_CLASS
import json
import time
import utils
import os
import RPi.GPIO as GPIO
from datetime import datetime
from py_ssq_sensor import ADS, ANEM, BME, FAN, GPS, HEATER, PMS
import send_errore_BME
import send_errore_GPS
import invio_dati
import serial

nt = 1
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class HandlerClass():

    def __init__(self, exceptionList, CONFIG_DATA, fileName):
        self.exceptionList = exceptionList
        self.CONFIG_DATA = CONFIG_DATA
        self.fileName = fileName
        self.flagPinA = ''
        self.flagPinB = ''
        self.checkException()


    def checkException(self):
        trueExceptionList = []
        positiveTestList = []
        rebootBME=False
        rebootGPS=False

        for item in self.exceptionList:
            try:
                raise item[0]

            except BME.BME_Exception as e:
                data = None
                rebootBME=False
                for retry in range(10):
                    try:
                        time.sleep(2)
                        data =self.testBME()
                        # data=None
                        if (data != None):
                            stringaEcc = "Test BME numero " + str(retry + 1) + " positivo: nessun errore riscontrato\n"
                            positiveTestList.append(stringaEcc)
                            break
                        else:
                            stringaEcc = "Test BME numero " + str(retry + 1) + " negativo: lettura dati non riuscita\n"
                            trueExceptionList.append(stringaEcc)
                    except Exception as event:
                        trueExceptionList.append(traceback.format_exc())

                if retry>=9 and data==None:
                    stringaEcc = "Test BME falliti. Tra 5 minuti la centralina si riavvia.\n"
                    trueExceptionList.append((stringaEcc))
                    print("\nTest BME falliti. Tra 5 minuti la centralina si riavvia.")
                    rebootBME=True
                    break



            except FAN.FAN_Exception as e:
                for retry in range(3):
                    try:
                        time.sleep(2)
                        self.testFAN()
                        break
                    except Exception as event:
                        trueExceptionList.append(traceback.format_exc())
                        if (retry >= 2):
                            pass



            except HEATER.HEATER_Exception as e:
                for retry in range(3):
                    try:
                        time.sleep(2)
                        self.testHEATER()
                        stringaEcc = "Test HEATER numero " + str(retry + 1) + " positivo: nessun errore riscontrato\n"
                        positiveTestList.append(stringaEcc)
                        break
                    except Exception as event:
                        stringaEcc = "Test HEATER numero " + str(retry + 1) + " negativo: " + traceback.format_exc()
                        trueExceptionList.append(stringaEcc)
                        if (retry >= 2):
                            self.CONFIG_DATA.set_pad_termico(False)



            except PMS.PMS_Exception as e:
                PMSNumber = e.number
                if (PMSNumber == 1 and self.CONFIG_DATA.get_pms1()):
                    ADDRESS_PMS = PMS.ADDRESS_1
                    pinS = PMS.PIN_S1
                    pinR = PMS.PIN_R1
                elif (PMSNumber == 2 and self.CONFIG_DATA.get_pms2()):
                    ADDRESS_PMS = PMS.ADDRESS_2
                    pinS = PMS.PIN_S2
                    pinR = PMS.PIN_R2
                else:
                    continue

                data = None
                for retry in range(3):
                    try:
                        time.sleep(2)
                        data = self.testPMS(ADDRESS_PMS, pinS, pinR)
                        if (data != None):
                            stringaEcc = "Test PMS" + str(PMSNumber) + " numero " + str(
                                retry + 1) + " positivo: nessun errore riscontrato\n"
                            positiveTestList.append(stringaEcc)
                            break
                        else:
                            stringaEcc = "Test PMS" + str(PMSNumber) + " numero " + str(
                                retry + 1) + " negativo: lettura dati non riuscita\n"
                            trueExceptionList.append(stringaEcc)
                    except Exception as event:
                        trueExceptionList.append(traceback.format_exc())

                if (retry >= 2 and data == None):
                    if (PMSNumber == 1):
                        self.CONFIG_DATA.set_pms1(False)
                    else:
                        self.CONFIG_DATA.set_pms2(False)
                i = 0
                if (data != None):
                    if (all([item[1] == 0 for item in data])):
                        try:
                            PMSTest = PMS.PmsClass(ADDRESS_PMS, pinS, pinR)
                            PMSTest.turn_on_test()
                            for i in range(20):
                                time.sleep(1)
                                data, _, _ = PMSTest.get_data_test()
                                if (data == None):
                                    stringaEcc = "Test PMS" + str(
                                        PMSNumber) + " nella lettura \"valori 0\" negativo: lettura dati non riuscita\n"
                                    trueExceptionList.append(stringaEcc)
                                if (any([item[1] != 0 for item in data])):
                                    break
                                if (i % 5 == 0):
                                    PMSTest.reset_test()
                        except Exception as event:
                            trueExceptionList.append(traceback.format_exc())
                        PMSTest.switch_off_test()
                    if (i == 19):
                        stringaEcc = "Test PMS" + str(PMSNumber) + " numero " + str(
                            retry + 1) + " negativo: lettura dati tutti 0\n"
                        trueExceptionList.append(stringaEcc)
                        if (PMSNumber == 1):
                            self.CONFIG_DATA.set_pms1(False)
                        else:
                            self.CONFIG_DATA.set_pms2(False)



            except ADS.ADS_Exception as e:
                ADSNumber = e.number
                ADDRESS_ADS, GAS1, GAS2, pinA, pinB = self.parameterADS(ADSNumber)
                checkPinA = ''
                checkPinB = ''
                for retry in range(3):
                    try:
                        ADSTest = ADS.ADS(ADDRESS_ADS, GAS1, GAS2, test=True)
                    except Exception as event:
                        stringaEcc = "Test ADS" + str(ADSNumber) + " numero " + str(
                            retry + 1) + " negativo: " + traceback.format_exc()
                        trueExceptionList.append(stringaEcc)

                    try:
                        if (pinA != '' and checkPinA != True):
                            time.sleep(2)
                            self.testPinA_ADS(ADSTest, pinA)
                            checkPinA = True
                    except Exception as event:
                        stringaEcc = "Test ADS" + str(ADSNumber) + " numero " + str(
                            retry + 1) + " su pinA negativo: " + traceback.format_exc()
                        trueExceptionList.append(stringaEcc)
                        checkPinA = False

                    try:
                        if (ADSNumber != 3 and pinB != '' and checkPinB != True):
                            time.sleep(2)
                            self.testPinB_ADS(ADSTest, pinB)
                            checkPinB = True
                    except Exception as event:
                        stringaEcc = "Test ADS" + str(ADSNumber) + " numero " + str(
                            retry + 1) + " su pinB negativo: " + traceback.format_exc()
                        trueExceptionList.append(stringaEcc)
                        checkPinB = False

                    if (checkPinA and checkPinB):
                        stringaEcc = "Test ADS" + str(ADSNumber) + " numero " + str(
                            retry + 1) + " positivo: nessun errore riscontrato\n"
                        positiveTestList.append(stringaEcc)
                        break

                if (ADSNumber == 1):
                    self.CONFIG_DATA.set_no2(self.flagPinA)
                    self.CONFIG_DATA.set_co(self.flagPinB)
                elif (ADSNumber == 2):
                    self.CONFIG_DATA.set_h2s(self.flagPinA)
                    self.CONFIG_DATA.set_so2(self.flagPinB)
                elif (ADSNumber == 3):
                    self.CONFIG_DATA.set_o3(self.flagPinA)



            except GPS.GPS_Exception as e:
                if (self.CONFIG_DATA.get_gps()):

                    serial_exc=None

                    for retry in range(3):
                        try:
                            time.sleep(2)
                            data = self.testGPS()
                            if (data[0]["key"] != None):
                                # print("segnale GPS letto: ", data)
                                stringaEcc = "Test GPS numero " + str(
                                    retry + 1) + " positivo: nessun errore riscontrato\n"
                                positiveTestList.append(stringaEcc)
                                break
                            else:
                                # print("segnale GPS non letto")
                                stringaEcc = "Test GPS numero " + str(
                                    retry + 1) + " negativo: lettura dati non riuscita\n"
                                trueExceptionList.append(stringaEcc)
                        except Exception as event:
                            serial_exc=event
                            trueExceptionList.append(traceback.format_exc())

                    if serial_exc != None:
                        try:
                            raise serial_exc

                        except serial.SerialException:
                            stringaEcc = "Test GPS falliti, lettura su porta USB non riuscita. Tra 5 minuti la centralina si riavvia.\n"
                            trueExceptionList.append((stringaEcc))
                            print("\nTest GPS falliti, lettura su porta USB non riuscita. Tra 5 minuti la centralina si riavvia.")
                            rebootGPS = True
                            break

                        except Exception:
                            pass
                else:
                    continue



            except ANEM.ANEM_Exception as e:
                data = None
                for retry in range(3):
                    try:
                        time.sleep(10)
                        data = self.testANEM()
                        if (data != None):
                            stringaEcc = "Test ANEM numero " + str(retry + 1) + " positivo: nessun errore riscontrato\n"
                            positiveTestList.append(stringaEcc)
                            break
                        else:
                            stringaEcc = "Test ANEM numero" + str(retry + 1) + " negativo: lettura dati non riuscita\n"
                            trueExceptionList.append(stringaEcc)
                    except Exception as event:
                        trueExceptionList.append(traceback.format_exc())

                if (retry >= 2 and data == None):
                    self.CONFIG_DATA.set_anemometro(False)


        self.writeLog(trueExceptionList)
        self.writePositiveTest(positiveTestList)


        # Verifico se il sistema deve essere riavviato in caso di guasto del BME:
        if rebootBME==True:
            # Verifico se Flask è attivo a "True" per poter inviare la notifica a Flask:
            if self.CONFIG_DATA.get_flask():
                # # definizione del parametro notifica da inviare a Flask:
                # notifica={"Errore BME":"True"}

                # recupero le info per inviare a Flask (nome della centralina):
                print("\nINVIO NOTIFICA BME SU FLASK:")

                info_flask=self.CONFIG_DATA.get_flask_info()
                centralina=info_flask['ID_CENTRALINA']

                # invio notifica:
               # send_errore_BME.send_flask(centralina,invio_dati.accessdb) ---> non esiste più accessdb

            else:
                print("\nNotifica di riavvio non inviata a Flask perchè è disabilitato.")

            for i in range(1,16):
                time.sleep(20)
                print("Mancano {} secondi".format(300-i*20))
            os.system("sudo shutdown -r now")



        # Verifico se il sistema deve essere riavviato in caso di guasto del GPS:
        if rebootGPS == True:
            # Verifico se Flask è attivo a "True" per poter inviare la notifica a Flask:
            if self.CONFIG_DATA.get_flask():
                # # definizione del parametro notifica da inviare a Flask:
                # notifica={"Errore GPS":"True"}

                # recupero le info per inviare a Flask (nome della centralina):
                print("\nINVIO NOTIFICA GPS SU FLASK:")

                info_flask = self.CONFIG_DATA.get_flask_info()
                centralina = info_flask['ID_CENTRALINA']

                # invio notifica:
                send_errore_GPS.send_flask(centralina, invio_dati)

            else:
                print("\nNotifica di riavvio non inviata a Flask perchè è disabilitato.")

            for i in range(1, 16):
                time.sleep(20)
                print("Mancano {} secondi".format(300 - i * 20))
            os.system("sudo shutdown -r now")


    def parameterADS(self, ADSNumber):
        pinA = ''
        pinB = ''
        if (ADSNumber == 1):
            ADDRESS = ADS.ADDRESS_1
            if (self.CONFIG_DATA.get_no2() == True):
                GAS1 = ADS.GAS(ADS.GAS_NO2,
                               self.CONFIG_DATA.get_no2_info().get("ID"),
                               float(self.CONFIG_DATA.get_no2_info().get("K1")),
                               float(self.CONFIG_DATA.get_no2_info().get("K2")),
                               float(self.CONFIG_DATA.get_no2_info().get("Sens"))
                               )
                pinA = ADS.PIN_A
                self.flagPinA = True
            else:
                GAS1 = None
                pinA = ''
                self.flagPinA = False

            if (self.CONFIG_DATA.get_co() == True):
                GAS2 = ADS.GAS(ADS.GAS_CO,
                               self.CONFIG_DATA.get_co_info().get("ID"),
                               float(self.CONFIG_DATA.get_co_info().get("K1")),
                               float(self.CONFIG_DATA.get_co_info().get("K2")),
                               float(self.CONFIG_DATA.get_co_info().get("Sens"))
                               )
                pinB = ADS.PIN_B
                self.flagPinB = True
            else:
                GAS2 = None
                pinB = ''
                self.flagPinB = False

        elif (ADSNumber == 2):
            ADDRESS = ADS.ADDRESS_2
            if (self.CONFIG_DATA.get_h2s() == True):
                GAS1 = ADS.GAS(ADS.GAS_H2S,
                               self.CONFIG_DATA.get_h2s_info().get("ID"),
                               float(self.CONFIG_DATA.get_h2s_info().get("K1")),
                               float(self.CONFIG_DATA.get_h2s_info().get("K2")),
                               float(self.CONFIG_DATA.get_h2s_info().get("Sens"))
                               )
                pinA = ADS.PIN_A
                self.flagPinA = True
            else:
                GAS1 = None
                pinA = ''
                self.flagPinA = False

            if (self.CONFIG_DATA.get_so2() == True):
                GAS2 = ADS.GAS(ADS.GAS_SO2,
                               self.CONFIG_DATA.get_so2_info().get("ID"),
                               float(self.CONFIG_DATA.get_so2_info().get("K1")),
                               float(self.CONFIG_DATA.get_so2_info().get("K2")),
                               float(self.CONFIG_DATA.get_so2_info().get("Sens"))
                               )
                pinB = ADS.PIN_B
                self.flagPinB = True
            else:
                GAS2 = None
                pinB = ''
                self.flagPinB = False

        elif (ADSNumber == 3):
            ADDRESS = ADS.ADDRESS_3
            if (self.CONFIG_DATA.get_o3() == True):
                GAS1 = ADS.GAS(ADS.GAS_O3,
                               self.CONFIG_DATA.get_o3_info().get("ID"),
                               float(self.CONFIG_DATA.get_o3_info().get("K1")),
                               float(self.CONFIG_DATA.get_o3_info().get("K2")),
                               float(self.CONFIG_DATA.get_o3_info().get("Sens"))
                               )
                pinA = ADS.PIN_A
                self.flagPinA = True
            else:
                GAS1 = None
                pinA = ''
                self.flagPinA = False
            GAS2 = None

        return ADDRESS, GAS1, GAS2, pinA, pinB

    def testPinA_ADS(self, ADSTest, pinA):
        print('-----TEST ADS PIN A-----')
        self.flagPinA = False
        ADSTest.get_raw_data_test(pinA)
        ADSTest.get_processed_data_test(pinA, nt)
        self.flagPinA = True

    def testPinB_ADS(self, ADSTest, pinB):
        print('-----TEST ADS PIN B-----')
        self.flagPinB = False
        ADSTest.get_raw_data_test(pinB)
        ADSTest.get_processed_data_test(pinB, nt)
        self.flagPinB = True

    def testANEM(self):
        print('-------TEST ANEM--------')
        ANEMTest = ANEM.ANEM()
        return ANEMTest.get_data_test()

    def testBME(self):
        print('-------TEST BME---------')
        BMETest = BME.BME(test=True)
        return BMETest.get_data_test()

    def testFAN(self):
        print('-------TEST FAN---------')
        FANTest = FAN.FAN()
        FANTest.turn_on_test(10)

    def testGPS(self):
        print('-------TEST GPS---------')
        GPSTest = GPS.GPS()
        return GPSTest.get_data_test()

    def testHEATER(self):
        print('-------TEST HEATER------')
        HEATERTest = HEATER.HEATER()
        HEATERTest.turn_on_test(10)

    def testPMS(self, ADDRESS_PMS, pinS, pinR):
        print('-------TEST PMS---------')
        PMSTest = PMS.PmsClass(ADDRESS_PMS, pinS, pinR)
        PMSTest.turn_on_test()
        data, _, _ = PMSTest.get_data_test()
        PMSTest.reset_test()
        PMSTest.switch_off_test()
        return data

    def writeLog(self, e):
        if (e):
            with open(self.fileName, 'a+') as f:
                for item in e:
                    f.write(datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + ' : ' + item + '\n')
            print('\nEccezioni memorizzate nel file \"ErrorLog\".')
        else:
            print('\nTEST terminato con successo.')

    def writePositiveTest(self, pos):
        if (pos):
            with open(utils.createNamePositiveTest(), 'a+') as f:
                for item in pos:
                    f.write(datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + ' : ' + item + '\n')
            print('TEST memorizzato nel file \"PositiveTest\".')
        # else :
        #     print('\nPositive Test vuoto')


def main():
    with open('CONFIG_CENTRALINA-TEST.json', 'r+') as file:
        data_config = json.load(file)
    istanza = CONFIG_CLASS.ConfigClass(data_config)
    ADSExce = ADS.ADS_Exception()
    PMSExce = PMS.PMS_Exception()
    ADSExce.set(1)
    PMSExce.set(2)
    exceptionList = [(ADSExce, 'error'), (PMSExce, 'error')]
    handleException = HandlerClass(exceptionList, istanza, utils.createNameLog())
    # handleException.checkException()
    CONFIG_CLASS.print_riepilogo(istanza)


if __name__ == '__main__':
    main()