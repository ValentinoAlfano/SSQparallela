import json
import time
import requests
import datetime
import codecs
import sort_feed
import CONFIG_CLASS
import utils
import os
from pathlib import Path
import random
import psutil


# VARIABILI GLOBALI:
url_auth = "http://192.168.2.144:5000/auth_sensor"
SECRET_KEY = "Gasrad98"

URL_Flask = "http://192.168.2.144:5000/send_sample_ssq"
URL_Flask_File = "http://192.168.2.144:5000/send_file"

STR_DEBUG = ""
DEBUG = True

try:
        with codecs.open(utils.path+"config.json", "r", encoding="latin1") as file:
                __config = json.load(file)

        centralina = __config['FIREBASE_INFO']['ID_CENTRALINA']
        data_sensor = utils.authflask(url_auth, SECRET_KEY, centralina)
except Exception as error:
    print("Errore nel caricamento della configurazione:\n")
    print(error)
    exit(-1)

def file_in_uso(fpath):
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if fpath == item.path:
                        return True
            except Exception:
                pass
        return False

def update_str_debug(messaggio):
    tempo = datetime.datetime.today().strftime("%H:%M:%S")
    stringa_debug = messaggio + "(" + tempo + ")" + "\n"
    return stringa_debug


def check_internet():
        try:
                risposta = requests.get("http://www.google.com/")
                if risposta.status_code == 200:
                        print("Connessione Riuscita: " +
                              str(risposta.status_code) + " " + str(risposta.reason))
                        return True
                else:
                        print("Connessione Fallita: " +
                              str(risposta.status_code) + " " + str(risposta.reason))
                return False
        except Exception:
                print("ERRORE CONNESSIONE")

def send_flask(data_sensor):
        STR_DEBUG = ""
        global DEBUG
        
        # Faccio 3 tentativi di connessione
        
        tentativo_conn = 0
        
        while tentativo_conn < 3:
                print("Tentativo di connessione numero:" + str(tentativo_conn + 1))
                STR_DEBUG += update_str_debug("\n Tentativo connessione numero:" + str(tentativo_conn + 1)+ " ")
                connessione = check_internet()
                print("Stato connessione: " + str(connessione))
                
                if connessione:
                        STR_DEBUG += update_str_debug("Connessione riuscita: invio dati")
                        # LEGGO LISTA FILE PRECEDENTI DA INVIARE
                        print("Lettura lista file da inviare...")
                        # LA LISTA TORNA GIA' ORDINATA CRONOLOGICAMENTE (PRIMO ELEMENTO -> PIU' RECENTE)
                        file_list = utils.check_databuffer()

                        
                        for file in file_list:
                                        start_time = time.time()
                                        if(file == file_list[0]):
                                                while(file_in_uso(file)):
                                                        print("File attualmente in uso. Riprovo tra 2 secondi")
                                                        time.sleep(2)

                                        with open(file, "r") as fp:
                                                # CARICO PACCHETTI DA FILE
                                                data_sample_from_file = json.load(fp)        
                                                print("Leggo: " + file + " ...")
                                                print("Contiene " + str(len(data_sample_from_file)) + " pacchetti")
                        
                                                # se pacchetti < 10 -----> invio_dati_flask_str()
                                                if len(data_sample_from_file): #qui va messo il controllo < 10 per decidere se inviare pacchetti o file
                                                                
                                                        i = 0
                                                        while len(data_sample_from_file):
                                                                esitoInvio = invio_dati_flask_str(data_sample_from_file[0],data_sensor)
                                                                if esitoInvio:
                                                                        print("Pacchetto #" + str(i + 1) + " inviato\n")
                                                                        i += 1
                                                                        data_sample_from_file.pop(0)
                                                                else:
                                                                        print("Pacchetto #" + str(i + 1) + " non inviato\n")
                                                                        break
                                                        print("Numero pacchetti inviati:" + str(i))
                                                        print("Invio completato in %s secondi " % round((time.time() - start_time)))
                                                        if len(data_sample_from_file) == 0:
                                                                print("Ho inviato tutti i pacchetti trovati in " + file)
                                                                # SE ENTRO QUI, HO MANDATO TUTTO IL CONTENUTO DEL FILE
                                                                STR_DEBUG += update_str_debug("DATABUFFER svuotato")
                                                                # cancello file corrente
                                                                print("Elimino " + file)
                                                                os.remove(file)                                        
                                                        else:
                                                                # riscrivo i pacchetti che non sono riuscito a inviare nello stesso file
                                                                scrittura_file(file, data_sample_from_file)
                                                                print("Ho riscritto i pacchetti che non sono riuscito a inviare in " + file)
                                                                break
                                                else:
                                                        # se pacchetti >= 10 ------> invio_dati_flask_file()
                                                        start_time = time.time()
                                                        esitoInvio = invio_dati_flask_file(file, data_sensor)
                                                        if esitoInvio:
                                                                print("File: " + file + " inviato in %s secondi " % round((time.time() - start_time)))
                                                                os.remove(file)
                                                        else:
                                                                print("File: " + file + " non inviato")
                                                                break
                        # tentativo_conn = tentativo_conn + 1                                
                        break
                else:
                        print("Tentativo di connessione n. " + str(tentativo_conn + 1) + " fallito")
                        tentativo_conn = tentativo_conn + 1
                        time.sleep(1)
        
        if DEBUG:
                try:
                        utils.checkPath(utils.path + "InvioDati_Log/")
                        fileName=utils.path+"InvioDati_Log/InvioDati_log_"+datetime.datetime.today().strftime('%d_%m_%Y')+".txt"
                        
                        with open(fileName,'a')as file:
                                file.write(STR_DEBUG)
                        print ("Stampa InvioDati_log.txt riuscita")
                except:
                        print ("Stampa InvioDati_log.txt non riuscita")        
# MAIN
def main():
                while True:
                        send_flask(data_sensor)
                        time.sleep(5)

# --------------------- FUNZIONI --------------------------:

# FUNZIONE DI TEST CHECK CONNESSIONE
def check_internet_false():
    return False

def check_internet_random():
        return bool(random.getrandbits(1))
        
# Funzione che scrive sul file "DATABUFFER_YY_MM_DD.json"
def scrittura_file(filename, dato):
        try:        
                # print("Provo a scrivere su " + filename)
                with open(filename, 'w') as file:
                        json.dump(dato, file)

                # print("\nFile " + filename + " aggiornato")
        except Exception as e:                
                print("\n ERRORE: scrittura del dato non riuscita")
                print(e)



# Funzione che ci restituisce la data in un vettore[anno, mese, giorno, ecc.]
# def recupero_data(t):
#     tempo_fromtimestamp = datetime.datetime.fromtimestamp(t)

#     year = tempo_fromtimestamp.strftime('%Y')
#     month = tempo_fromtimestamp.strftime('%m')
#     day = tempo_fromtimestamp.strftime('%d')
#     hour = tempo_fromtimestamp.strftime('%H')
#     minute = tempo_fromtimestamp.strftime('%M')
#     second = tempo_fromtimestamp.strftime('%S')

#     data = [year, month, day, hour, minute, second]

#     return data

# FUNZIONE PER LA CREAZIONE DELLE QUERY CON GLI ULTIMI VALORI RILEVATI DALLA CENTRALINA NEL MESE
# def creazione_pattern_today_zone(cap_zona,timestamp,feeds):

#         # anno_mese=timestamp[:6]
#         ora=timestamp[8:10]
        
#         ora_pprec=str(int(ora)-2)
#         minuto=timestamp[10:12]
#         minuto_pprec=str(int(minuto)-2)
        
#         weekday=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
        
#         weekday=weekday.weekday()
        
#         feeds2=dict(feeds)        
#         del feeds2['latitude']
#         del feeds2['longitude']
        
#         if ora=='23':
#                 weekday= (weekday+1) %7
        
#         query={"_id": "Today_zone "+str(weekday)} 
#         new_dict={}


#         for d in feeds2:
#            p=json.dumps(d)
#            p=p[1:len(p)-1]
#            sum_=cap_zona+".medie_hourly."+ora+".feeds."+p+".sum"
#            new_dict[sum_]=feeds[d]
          
#            count=cap_zona+".medie_hourly."+ora+".feeds."+p+".count"
#            new_dict[count]=1
           
#            sum_=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
#            new_dict[sum_]=feeds[d]

#            count=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
#            new_dict[count]=1
           
#         update={"$inc": new_dict, "$unset": {cap_zona+".medie_hourly."+ora+".instantly."+minuto_pprec: "", cap_zona+".medie_hourly."+ora_pprec: ""}}
#         result={"data":[query,update]}
        
#         return result
        
# def creazione_pattern_today_squares(cap_zona,squareid,timestamp,feeds):

#         # anno_mese=timestamp[:6]
#         ora=timestamp[8:10]
        
#         ora_pprec=str(int(ora)-2)
#         minuto=timestamp[10:12]
#         minuto_pprec=str(int(minuto)-2)
        
#         weekday=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
        
#         weekday=weekday.weekday()
        
#         feeds2=dict(feeds)        
#         del feeds2['latitude']
#         del feeds2['longitude']
        
#         if ora=='23':
#                 weekday= (weekday+1) %7
        
#         query={"_id": "Today_squares "+str(weekday)}
#         new_dict={}

#         for d in feeds2:
#            p=json.dumps(d)
#            p=p[1:len(p)-1]
#            sum_=cap_zona+"."+squareid+".medie_hourly."+ora+".feeds."+p+".sum"
#            new_dict[sum_]=feeds[d]
           
#            count=cap_zona+"."+squareid+".medie_hourly."+ora+".feeds."+p+".count"
#            new_dict[count]=1
                
#            sum_=cap_zona+"."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
#            new_dict[sum_]=feeds[d]

#            count=cap_zona+"."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
#            new_dict[count]=1
        
#         update={"$inc": new_dict, "$unset": {cap_zona+"."+squareid+".medie_hourly."+ora+".instantly."+minuto_pprec: "", cap_zona+"."+squareid+".medie_hourly."+ora_pprec: ""}}
#         result={"data":[query,update]}
        
#         return result



# def creazione_pattern_raw(centralina,cap,square,timestamp,feeds):
#         result={}
#         anno_mese=timestamp[:6]
#         minuto=timestamp[:12]
        
#         query_raw={"centralina": centralina, "timestamp": anno_mese}
#         update_raw={"$set": { minuto : { "feeds": feeds, "cap": cap, "zona_square": square } }}
        

#         result={"data":[query_raw,update_raw]}
        
#         return result

# def creazione_pattern_zona (centralina,cap_zona,squareid,timestamp,feeds):
        
#         feeds2=dict(feeds)        
#         del feeds2['latitude']
#         del feeds2['longitude']

#         result={}
#         new_dict={}
#         epoch=datetime.datetime.utcfromtimestamp(0)        
#         now=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
#         days_from_epoch=(now-epoch).days
#         # squareid=zona_square[8:]
#         # zona=zona_square[:8]
#         # cap_zona=cap_zona_square[:17]
#         # squareid=cap_zona_square[18:]
#         # giorno=timestamp[:8]
#         ora=timestamp[8:10]        
#         minuto=timestamp[10:12]
#         print(cap_zona)
#         print(squareid)

#         weekday=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
        
#         weekday=weekday.weekday()

#         query_next_day={"_id": weekday+1 , "date": days_from_epoch }
#         query_today={"_id": weekday, "date": days_from_epoch}

#         # creo la query per il pattern del giorno dopo
#         for d in feeds2:
#                 p=json.dumps(d)
#                 p=p[1:len(p)-1]

#                 # sum_=cap+"."+zona+".medie_daily."+p+".sum"
#                 sum_=cap_zona+".medie_daily."+p+".sum"
#                 new_dict[sum_]=feeds[d]
#                 # count=cap+"."+zona+".medie_daily."+p+".count"
#                 count=cap_zona+".medie_daily."+p+".count"
#                 new_dict[count]=1
#                 # sum_=cap+"."+zona+".squares."+squareid+".medie_daily.feeds."+p+".sum"
#                 sum_=cap_zona+".squares."+squareid+".medie_daily.feeds."+p+".sum"
#                 new_dict[sum_]=feeds[d]
#                 # count=cap+"."+zona+".squares."+squareid+".medie_daily.feeds."+p+".count"
#                 count=cap_zona+".squares."+squareid+".medie_daily.feeds."+p+".count"
#                 new_dict[count]=1
#         new_values_nd={"$inc":new_dict}

#         new_dict={}
        
#         # creo pattern per la query del giorno attuale
#         for d in feeds2:
#                 p=json.dumps(d)
#                 p=p[1:len(p)-1]
                
#                 # sum_=cap+"."+zona+".medie_hourly."+ora+".feeds."+p+".sum"
#                 sum_=cap_zona+".medie_hourly."+ora+".feeds."+p+".sum"
#                 new_dict[sum_]=feeds[d]
#                 # count=cap+"."+zona+".medie_hourly."+ora+".feeds."+p+".count"
#                 count=cap_zona+".medie_hourly."+ora+".feeds."+p+".count"
#                 new_dict[count]=1
#                 # sum_=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".sum"
#                 sum_=cap_zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".sum"
#                 new_dict[sum_]=feeds[d]
#                 # count=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".count"
#                 count=cap_zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".count"
#                 new_dict[count]=1

#                 # sum_=cap+"."+zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
#                 sum_=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
#                 new_dict[sum_]=feeds[d]
#                 # sum_=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
#                 sum_=cap_zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
#                 new_dict[sum_]=feeds[d]                
#                 # count=cap+"."+zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
#                 count=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
#                 new_dict[count]=1
#                 # count=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
#                 count=cap_zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
#                 new_dict[count]=1

#         new_values_td={"$inc":new_dict}

#         result = {"data":[[query_next_day,new_values_nd],[query_today,new_values_td]]}
        
#         return result


# Funzione che costruisce il pattern da inserire nel Firebase:

# def creazione_data_request(centralina,polygons,coordinate,squares, timestamp, feeds, data_sensor):
        
        
#         cap_zona_square_groups = sort_feed.Sorting_AreasKM(squares, coordinate)
#         centralina=str(centralina)
#         cap_zona=cap_zona_square_groups['cap']+"_"+cap_zona_square_groups['zona']
#         square=str(cap_zona_square_groups['square'])
#         groups=cap_zona_square_groups['groups']
#         cap=cap_zona_square_groups['cap']        

#         # cap=cap_zona_square[:9]
#         # users=1
#         # users=data_sensor['data']['monitoring']['features']['properties']['group']
#         # zona_square=cap_zona_square[10:]
#         # zona=cap_zona_square[10:18]
#         # square=cap_zona_square[10:]

#         # timestamp_giornaliero=timestamp[:8]
#         # timestamp_orario=timestamp[:10]
#         # timestamp_instant=timestamp[:12]
        
#         dati5=creazione_pattern_raw(centralina,cap,square,timestamp,feeds)
#         dati6=creazione_pattern_zona(centralina,cap_zona,square,timestamp,feeds)
#         dati7=creazione_pattern_today_squares(cap_zona,square,timestamp,feeds)
#         dati8=creazione_pattern_today_zone(cap_zona,timestamp,feeds)

#         dati={"queries":[dati5,dati6,dati7,dati8]}
        
        
#         dati['group']=groups

        
#         return dati
        
# Funzione che invia la singola stringa a Flask
def invio_dati_flask_str(data, data_sensor):
        
        global STR_DEBUG

        try:
                STR_DEBUG += update_str_debug("\nINIZIO ESECUZIONE invio_dati_flask: ")

                conn=check_internet()
                # conn=False
                if conn:
                        STR_DEBUG += update_str_debug("\n CONNESSIONE RIUSCITA: invio oggetto ")
                        
                        data=json.dumps(data)                       #formatta in JSON                 
                        
                        headers={'Authorization': 'Bearer '+ data_sensor['data']['token']}
                        requests.post(url=URL_Flask, data=data, headers=headers)
                        
                        print ("Salvataggio oggetto riuscito")
                        
                        return True
                        
                else:
                        STR_DEBUG += update_str_debug("\n CONNESSIONE FALLITA nell'invio dell'oggetto temporaneo")
                        print("CRASH CONNESSIONE: salvataggio FALLITO")
                        return False

        except Exception as e:
                STR_DEBUG += update_str_debug("Verificata eccezione su invio_dati_flask")
                print ( "Errore: invio dati non riuscito")
                print (e)
        return False

# Funzione che invia direttamente il file a Flask - DA RIVEDERE NON FUNZIONA
def invio_dati_flask_file(file, data_sensor):
        global STR_DEBUG

        try:
                STR_DEBUG += update_str_debug("\nINIZIO ESECUZIONE invio_dati_flask: ")

                conn = check_internet()
                # conn=False
                if conn:
                        STR_DEBUG += update_str_debug("\n CONNESSIONE RIUSCITA: invio oggetto ")
                        
                        # data = json.dumps(file)                       #formatta in JSON                 
                        # file_to_upload = {'file': open(file, 'rb')}
                        # file_to_upload = open(file, 'rb')
                        with open(file, 'rb') as fp:
                                file_to_upload = {'file': fp}
                                headers = {'Authorization': 'Bearer '+ data_sensor['data']['token']}
                                requests.post(URL_Flask_File, files = file_to_upload, headers = headers)
                        # print(requests.get(URL_Flask).status_code)
                        print("Salvataggio oggetto riuscito")
                        
                        return True
                        
                else:
                        STR_DEBUG += update_str_debug("\n CONNESSIONE FALLITA nell'invio dell'oggetto temporaneo")
                        print("CRASH CONNESSIONE: salvataggio FALLITO")
                        return False

        except Exception as e:
                STR_DEBUG += update_str_debug("Verificata eccezione su invio_dati_flask")
                print ( "Errore: invio dati non riuscito")
                print (e)
        return False

# ------------------------- FUNZIONI per il main --------------------------------------:

# Lettura file di configurazione, restituisce tutti i dati del file di configurazione:
def lettura_file_configurazione():
    # try:
    #     with open(utils.path+"config.json",'r') as f:
    #         dati_conf=json.load(f)

    #     print("\nLettura file: \"config.json\" riuscita\n")

    #     return dati_conf
    # except Exception:
    #     print("ERRORE: lettura file di configurazione non riuscita\n")
        if os.path.exists(utils.path + "config.json"):
                dati_conf = json.load(utils.path + "config.json")
                print("\nLettura file: \"config.json\" riuscita\n")
                return dati_conf
        else:
                print("ERRORE: lettura file di configurazione non riuscita\n")



# Funzione di invio dati su Firebase e ThingSpeak:
# def send_data(config,valori,polygon,squares, data_sensor, timestamp):
#     global STR_DEBUG
#     STR_DEBUG += update_str_debug("\n\n\n---- INIZIO ESECUZIONE send_data: ")

#     # Verifico se FLASK è attivo a "True" per poter inviare il dato a Flask:

#     if config.get_firebase():
#         STR_DEBUG += update_str_debug("Flask attivo ")

#         # recupero le info per inviare a Flask (nome della centralina):
#         print("\nINVIO DATI SU FLASK:")
#         info_firebase = config.get_firebase_info()
#         centralina = info_firebase['ID_CENTRALINA']

        


#         send_flask(centralina, valori, polygon, squares, data_sensor, timestamp)

#     # Verifico se ThingSpeak è attivo per poter inviare il dato a ThingSpeak:
#     if config.get_thingspeak():
#         STR_DEBUG = ""
#         STR_DEBUG += update_str_debug("\n\n\n---- CONTINUA ESECUZIONE send_data: ")
#         STR_DEBUG += update_str_debug("ThingSpeak attivo ")

#         print("\n\nINVIO DATI SU THINGSPEAK:\n")
#         # recupero le info per inviare a ThingSpeak:
#         info_thingspeak = config.get_thingspeak_info()

#         send_thinkspeak(info_thingspeak,valori)

# Funzione main:

    # Lettura dal file configurazione e creazione dell'oggetto "dati_configurazione"
    # dati_configurazione = CONFIG_CLASS.ConfigClass(lettura_file_configurazione())

    # Invio dati:
    # send_data(dati_configurazione,valori,polygon,squares, data_sensor, timestamp)


if __name__ == '__main__':
#     valori = {"no2": 30,
#               "so2": 50,
#               "co": 316.0,
#               "cpuTemperature": 42.084,
#               "direzione_vento": 6,
#               "gas_m": 70,
#               "intensita_vento": 2,
#               "latitude": 45.06479159126726,
#               "longitude": 7.675323486328125,
#               "nt": 5.6316710782,
#               "pm1": 15.0,
#               "pm10": 21.0,
#               "pm2_5": 20.0,
#               "pressione": 987.82,
#               "programStatus": 33,
#               "temperatura": 27.87,
#               "umidita": 46.48,
#               "voc": 24.35}

    main()
