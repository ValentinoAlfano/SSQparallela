# coding=utf-8

import json
# from tkinter import filedialog
# from tkinter import Tk

class ConfigClass():

    def __init__(self, config_data):

        self.pms1=config_data['PM1']
        self.pms2 = config_data['PM2']
        self.pad_termico=config_data['PAD_TERMICO']
        self.anemometro=config_data['ANEMOMETRO']
        self.no2=config_data['NO2']
        if self.no2==True:
            self.no2_info=config_data['NO2_INFO']
        else:
            self.no2_info=None
        self.co = config_data['CO']
        if self.co==True:
            self.co_info=config_data['CO_INFO']
        else:
            self.co_info=None
        self.h2s = config_data['H2S']
        if self.h2s==True:
            self.h2s_info=config_data['H2S_INFO']
        else:
            self.h2s_info=None
        self.so2 = config_data['SO2']
        if self.so2==True:
            self.so2_info=config_data['SO2_INFO']
        else:
            self.so2_info=None
        self.o3 = config_data['O3']
        if self.o3==True:
            self.o3_info=config_data['O3_INFO']
        else:
            self.o3_info=None
        self.rs485 = config_data['RS485']
        self.lte = config_data['LTE']
        self.lan = config_data['LAN']
        self.lora = config_data['LORA']

        if self.lora==True:
            self.lora_info = config_data['LORA_INFO']
        else:
            self.lora_info=None

        self.notifica_errori=config_data['NOTIFICA_ERRORI']
        self.baseline=config_data['BASELINE_HOUR']

        self.gps = config_data['GPS']
        print(self.gps)
        self.gps_info = config_data['GPS_INFO']

        self.firebase=config_data['FIREBASE']

        if self.firebase==True:
            self.firebase_info = config_data['FIREBASE_INFO']
        else:
            self.firebase_info=None

        self.thingspeak = config_data['THINGSPEAK']
        if self.thingspeak==True:
            self.thingspeak_info = config_data['THINGSPEAK_INFO']
        else:
            self.thingspeak_info=None

    def get_pms1(self):
        return self.pms1

    def set_pms1(self,value):
        if value is bool:
            self.pms1=value
        elif value==0:
            value=False
            self.pms1=value
        elif value==1:
            value=True
            self.pms1=value
        else:
            value=False
            self.pms1=value

    def get_pms2(self):
        return self.pms2

    def set_pms2(self,value):
        if value is bool:
            self.pms2=value
        elif value==0:
            value=False
            self.pms2=value
        elif value==1:
            value=True
            self.pms2=value
        else:
            value=False
            self.pms2=value

    def get_pad_termico(self):
        return self.pad_termico

    def set_pad_termico(self,value):
        if value is bool:
            self.pad_termico=value
        elif value==0:
            value=False
            self.pad_termico=value
        elif value==1:
            value=True
            self.pad_termico=value
        else:
            value=False
            self.pad_termico=value

    def get_anemometro(self):
        return self.anemometro

    def set_anemometro(self,value):
        if value is bool:
            self.anemometro=value
        elif value==0:
            value=False
            self.anemometro=value
        elif value==1:
            value=True
            self.anemometro=value
        else:
            value=False
            self.anemometro=value

    def get_no2(self):
        return self.no2

    def set_no2(self,value):
        if value is bool:
            self.no2=value
        elif value==0:
            value=False
            self.no2=value
        elif value==1:
            value=True
            self.no2=value
        else:
            value=False
            self.no2=value

    def get_no2_info(self):
        return self.no2_info

    def get_co(self):
        return self.co

    def set_co(self,value):
        if value is bool:
            self.co=value
        elif value==0:
            value=False
            self.co=value
        elif value==1:
            value=True
            self.co=value
        else:
            value=False
            self.co=value

    def get_co_info(self):
        return self.co_info

    def get_h2s(self):
        return self.h2s

    def set_h2s(self,value):
        if value is bool:
            self.h2s=value
        elif value==0:
            value=False
            self.h2s=value
        elif value==1:
            value=True
            self.h2s=value
        else:
            value=False
            self.h2s=value

    def get_h2s_info(self):
        return self.h2s_info

    def get_so2(self):
        return self.so2

    def set_so2(self,value):
        if value is bool:
            self.so2=value
        elif value==0:
            value=False
            self.so2=value
        elif value==1:
            value=True
            self.so2=value
        else:
            value=False
            self.so2=value

    def get_so2_info(self):
        return self.so2_info

    def get_o3(self):
        return self.o3

    def set_o3(self,value):
        if value is bool:
            self.o3=value
        elif value==0:
            value=False
            self.o3=value
        elif value==1:
            value=True
            self.o3=value
        else:
            value=False
            self.o3=value

    def get_o3_info(self):
        return self.o3_info

    def get_rs485(self):
        return self.rs485

    def set_rs485(self,value):
        if value is bool:
            self.rs485=value
        elif value==0:
            value=False
            self.rs485=value
        elif value==1:
            value=True
            self.rs485=value
        else:
            value=False
            self.rs485=value

    def get_lte(self):
        return self.lte

    def set_lte(self,value):
        if value is bool:
            self.lte=value
        elif value==0:
            value=False
            self.lte=value
        elif value==1:
            value=True
            self.lte=value
        else:
            value=False
            self.lte=value

    def get_lan(self):
        return self.lan

    def set_lan(self,value):
        if value is bool:
            self.lan=value
        elif value==0:
            value=False
            self.lan=value
        elif value==1:
            value=True
            self.lan=value
        else:
            value=False
            self.lan=value

    def get_lora(self):
        return self.lora

    def set_lora(self,value):
        if value is bool:
            self.lora=value
        elif value==0:
            value=False
            self.lora=value
        elif value==1:
            value=True
            self.lora=value
        else:
            value=False
            self.lora=value

    def get_lora_info(self):
        return self.lora_info

    def get_notifica_errori(self):
        return self.notifica_errori

    def set_notifica_errori(self,value):
        if value is bool:
            self.notifica_errori=value
        elif value==0:
            value=False
            self.notifica_errori=value
        elif value==1:
            value=True
            self.notifica_errori=value
        else:
            value=False
            self.notifica_errori=value

    def get_baseline(self):
        return self.baseline

    def set_baseline(self,value):
        self.baseline=value

    def get_gps(self):
        return self.gps

    def set_gps(self,value):
        if value is bool:
            self.gps=value
        elif value==0:
            value=False
            self.gps=value
        elif value==1:
            value=True
            self.gps=value
        else:
            value=False
            self.gps=value

    def get_gps_info(self):
        return self.gps_info

    def get_firebase(self):
        return self.firebase

    def set_firebase(self,value):
        if value is bool:
            self.firebase=value
        elif value==0:
            value=False
            self.firebase=value
        elif value==1:
            value=True
            self.firebase=value
        else:
            value=False
            self.firebase=value

    def get_firebase_info(self):
        return self.firebase_info

    def get_thingspeak(self):
        return self.thingspeak

    def set_thingspeak(self,value):
        if value is bool:
            self.thingspeak=value
        elif value==0:
            value=False
            self.thingspeak=value
        elif value==1:
            value=True
            self.thingspeak=value
        else:
            value=False
            self.thingspeak=value

    def get_thingspeak_info(self):
        return self.thingspeak_info



def main():

    Tk().withdraw()
    f = filedialog.askopenfilename(initialdir="C:/Users/Windows/PycharmProjects/interfaccia/venv/", title="select file", filetypes=(("Json File", " *.json"),("all files","*.*")))
    with open(f, 'r+') as file:
        data_config = json.load(file)

    istanza=ConfigClass(data_config)
    print_riepilogo(istanza)

    p=int(input("inserisci il valore"))
    istanza.set_baseline(p)
    print_riepilogo(istanza)

    while True:

        x=str(input("Quale settaggio vuoi cambiare?"))
        val=None
        while val==None:
            str_input=input("Quale valore vuoi attribuirgli? (0/1 )(false/true)")
            try:
                val=int(str_input)
                if not(val in [0,1]):
                    print("Input non consentito")
                    val=None
            except:
                if str_input.upper() == "TRUE" or str_input.upper()=='T':
                    val=True
                elif str_input.upper() == "FALSE" or str_input.upper()=='F':
                    val = False
                    break
                else:
                    print("Input non consensito ")

        if x=='pms1':
            istanza.set_pms1(val)
        elif x=='pms2':
            istanza.set_pms2(val)
        elif x=='pad_termico':
            istanza.set_pad_termico(val)
        elif x=='anemometro':
            istanza.set_anemometro(val)
        elif x=='no2':
            istanza.set_no2(val)
        elif x=='co':
            istanza.set_co(val)
        elif x=='h2s':
            istanza.set_h2s(val)
        elif x=='so2':
            istanza.set_so2(val)
        elif x=='o3':
            istanza.set_o3(val)
        elif x=='rs485':
            istanza.set_rs485(val)
        elif x=='lte':
            istanza.set_lte(val)
        elif x=='lan':
            istanza.set_lan(val)
        elif x=='lora':
            istanza.set_lora(val)
        elif x=='notifica_errori':
            istanza.set_notifica_errori(val)
        elif x=='gps':
            istanza.set_gps(val)
        elif x=='firebase':
            istanza.set_firebase(val)
        elif x=='thingspeak':
            istanza.set_thingspeak(val)
        else:
            print("Variabile non presente")

        print_riepilogo(istanza)


def print_riepilogo(istanza):
    print("\n----------Parametri di configurazione---------\n")
    print("PMS1: " + str(istanza.get_pms1()))
    print("PMS2: " + str(istanza.get_pms2()))
    print("PAD_TERMICO: " + str(istanza.get_pad_termico()))
    print("ANEMOMETRO: " + str(istanza.get_anemometro()))
    print("GPS: " + str(istanza.get_gps()))
    print("GPS_INFO: " + str(istanza.get_gps_info()))
    print("NO2: " +str(istanza.get_no2()))
    print("NO2_INFO: " + str(istanza.get_no2_info()))
    print("CO: "+ str(istanza.get_co()))
    print("CO_INFO: " + str(istanza.get_co_info()))
    print("H2S: " + str(istanza.get_h2s()))
    print("H2S_INFO: " + str(istanza.get_h2s_info()))
    print("SO2: " + str(istanza.get_so2()))
    print("SO2_INFO: " + str(istanza.get_so2_info()))
    print("O3: " + str(istanza.get_o3()))
    print("O3_INFO: " + str(istanza.get_o3_info()))
    print("RS485: " + str(istanza.get_rs485()))
    print("LTE: " + str(istanza.get_lte()))
    print("LAN: " + str(istanza.get_lan()))
    print("LORA: " + str(istanza.get_lora()))
    print("LORA_INFO: " + str(istanza.get_lora_info()))
    print("NOTIFICA_ERRORI: " + str(istanza.get_notifica_errori()))
    print("BASELINE: " + str(istanza.get_baseline()))
    print("FIREBASE: " + str(istanza.get_firebase()))
    print("FIREBASE_INFO: " + str(istanza.get_firebase_info()))
    print("THINGSPEAK: " + str(istanza.get_thingspeak()))
    print("THINGSPEAK_INFO: " + str(istanza.get_thingspeak_info()))

if __name__ == '__main__':
    main()
