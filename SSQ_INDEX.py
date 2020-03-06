# coding=utf-8

import json
import datetime
import time
import traceback
import codecs
import pprint

import CONFIG_CLASS
from py_ssq_sensor import ADS, ANEM, BME, FAN, GPS, HEATER, PMS
#import py_ssq_sensor.ADS, py_ssq_sensor.ANEM, py_ssq_sensor.BME, py_ssq_sensor.FAN, py_ssq_sensor.GPS, py_ssq_sensor.HEATER, py_ssq_sensor.PMS
import ExceptionHandler
import utils
#import invio_dati
# import save_error_log_main
import setNT

# from dotenv import load_dotenv
# load_dotenv()
import os
import sort_feed

# url_auth = os.getenv("URL_AUTH")
# SECRET_KEY = os.getenv("SECRET_KEY")

url_auth = "http://192.168.2.144:5000/auth_sensor"
SECRET_KEY = "Gasrad98"


# ------------ Funzione di DEBUG --------------
STR_DEBUG = ""
DEBUG = True


def update_str_debug(messaggio):
    tempo = datetime.datetime.today().strftime("%H:%M:%S")
    stringa_debug = messaggio + "(" + tempo + ")" + "\n"
    return stringa_debug


# ------ Funzione di salvataggio dell'errore sul file "ErrorLogMain_%D_%M_%Y.txt" ---------
def save_error(errore):
    try:
        nome_file = utils.createNameLog()
        #nome_file = 'ErrorLog_'+datetime.today().strftime('%d_%m_%Y')+'.txt'
        #error_folder_name = "Error_Log/"

        utils.checkPath(utils.path + "Error_Log/") #creo percorso se non esiste

        #with open(utils.path + "Error_Log/" + nome_file, 'a+') as file:
        with open(nome_file, 'a+') as file:
            print("SCRIVO IN " + utils.path + "Error_Log/" + nome_file)
            file.write(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + ' : ' + errore + '\n')
            print("\nERRORE sul SSQ MAIN PROCESS: log memorizzato nel file \"ErrorLog\".")      


    except Exception as e:
        print("\nERRORE: salvataggio sul file \"ErrorLog\" non riuscito.")
        print(e)

# FUNZIONI 

#ex send_flask() (parte di "costruzione" del file)
def creazione_dati_file(centralina, valori, polygons, squares, data_sensor, timestamp):
	global STR_DEBUG
	
	lat = valori['latitude']
	lon = valori['longitude']
	coordinate = (lat,lon)

	STR_DEBUG += update_str_debug("\n INIZIO ESECUZIONE send_flask")
	
	#DATO CAMPIONATO
	data_sample = creazione_data_request(centralina,polygons,coordinate,squares, timestamp,valori,data_sensor)	

	#PRIMA DI SCRIVERE DEVO CONTROLLARE SE ESISTE GIA' IL FILE
	#SE ESISTE DEVO LEGGERNE I PACCHETTI E POI RISCRIVERE LA LISTA COMPLETA COI DATI NUOVI
	filename = utils.path + "DATABUFFER_" + timestamp[:10] + ".json"
	buffer = []
	print("Cerco il file in cui salvare i dati appena campionati...")
	if os.path.exists(filename):
		print("Trovato " + filename)
		#Il file esiste già, quindi leggo i pacchetti che contiene, aggiungo in coda i dati campionati e riscrivo il file completo
		print("Leggo i pacchetti in " + filename + " ...")
		
		with open(filename, "r") as fp:
			data_sample_from_file = json.load(fp)
		
		print("Contiene " + str(len(data_sample_from_file)) + " pacchetti")
		#AGGIUNGO I PACCHETTI ALLA LISTA TEMP
		i = 0
		
		while len(data_sample_from_file):
			i += 1
			print("Pacchetto # " + str(i) + " aggiunto")
			buffer.append(data_sample_from_file[0])
			data_sample_from_file.pop(0)
		print("Pacchetti aggiunti alla lista temp:" + str(i))	
	else:
		#SE NON ESISTE ANCORA IL FILE NON FARE NIENTE
		print(filename + " non esiste ancora")
	#IN CODA AGGIUNGO IL DATO CAMPIONATO ATTUALE
	buffer.append(data_sample)
	#SCRIVO LA LISTA BUFFER SU FILE
	print("Scrittura su " + filename + " ...")
	scrittura_file(filename, buffer)
	print("Ho salvato i dati appena campionati in " + filename)
	
	if DEBUG:
		try:
			utils.checkPath(utils.path + "InvioDati_Log/")
			fileName=utils.path+"InvioDati_Log/InvioDati_log_"+datetime.datetime.today().strftime('%d_%m_%Y')+".txt"
			
			with open(fileName,'a')as file:
				file.write(STR_DEBUG)
			print ("Stampa InvioDati_log.txt riuscita")
		except:
			print ("Stampa InvioDati_log.txt non riuscita")	

# ex send_data()
def creazione_dati(config,valori,polygon,squares, data_sensor, timestamp):
    global STR_DEBUG
    STR_DEBUG += update_str_debug("\n\n\n---- INIZIO ESECUZIONE send_data: ")

    # Verifico se FLASK è attivo a "True" per poter inviare il dato a Flask:

    if config.get_firebase():
        STR_DEBUG += update_str_debug("Flask attivo ")

        # recupero le info per inviare a Flask (nome della centralina):
        print("\nINVIO DATI SU FLASK:")
        info_firebase = config.get_firebase_info()
        centralina = info_firebase['ID_CENTRALINA']           

        creazione_dati_file(centralina, valori, polygon, squares, data_sensor, timestamp)

                # Verifico se ThingSpeak è attivo per poter inviare il dato a ThingSpeak:
                # if config.get_thingspeak():
                #     STR_DEBUG = ""
                #     STR_DEBUG += update_str_debug("\n\n\n---- CONTINUA ESECUZIONE send_data: ")
                #     STR_DEBUG += update_str_debug("ThingSpeak attivo ")

                #     print("\n\nINVIO DATI SU THINGSPEAK:\n")
                #     # recupero le info per inviare a ThingSpeak:
                #     info_thingspeak = config.get_thingspeak_info()

                #     send_thinkspeak(info_thingspeak,valori)

# Funzione che costruisce il pattern da inserire nel Firebase:
def creazione_data_request(centralina,polygons,coordinate,squares, timestamp, feeds, data_sensor):
	
	
	cap_zona_square_groups = sort_feed.Sorting_AreasKM(squares, coordinate)
	centralina=str(centralina)
	cap_zona=cap_zona_square_groups['cap']+"_"+cap_zona_square_groups['zona']
	square=str(cap_zona_square_groups['square'])
	groups=cap_zona_square_groups['groups']
	cap=cap_zona_square_groups['cap']	

	#cap=cap_zona_square[:9]
	#users=1
	#users=data_sensor['data']['monitoring']['features']['properties']['group']
	#zona_square=cap_zona_square[10:]
	#zona=cap_zona_square[10:18]
	#square=cap_zona_square[10:]

	#timestamp_giornaliero=timestamp[:8]
	#timestamp_orario=timestamp[:10]
	#timestamp_instant=timestamp[:12]
	
	dati5=creazione_pattern_raw(centralina,cap,square,timestamp,feeds)
	dati6=creazione_pattern_zona(centralina,cap_zona,square,timestamp,feeds)
	dati7=creazione_pattern_today_squares(cap_zona,square,timestamp,feeds)
	dati8=creazione_pattern_today_zone(cap_zona,timestamp,feeds)

	dati={"queries":[dati5,dati6,dati7,dati8]}
	
	
	dati['group']=groups

	
	return dati

# Funzione che scrive sul file "DATABUFFER_YY_MM_DD.json"
def scrittura_file(filename, dato):
	try:	
		#print("Provo a scrivere su " + filename)
		with open(filename, 'w') as file:
			json.dump(dato, file)

		#print("\nFile " + filename + " aggiornato")
	except Exception as e:		
		print("\n ERRORE: scrittura del dato non riuscita")
		print(e)

#FUNZIONE PER LA CREAZIONE DELLE QUERY CON GLI ULTIMI VALORI RILEVATI DALLA CENTRALINA NEL MESE
def creazione_pattern_today_zone(cap_zona,timestamp,feeds):

	#anno_mese=timestamp[:6]
	ora=timestamp[8:10]
	
	ora_pprec=str(int(ora)-2)
	minuto=timestamp[10:12]
	minuto_pprec=str(int(minuto)-2)
	
	weekday=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
	
	weekday=weekday.weekday()
	
	feeds2=dict(feeds)	
	del feeds2['latitude']
	del feeds2['longitude']
	
	if ora=='23':
		weekday= (weekday+1) %7
	
	query={"_id": "Today_zone "+str(weekday)} 
	new_dict={}


	for d in feeds2:
	   p=json.dumps(d)
	   p=p[1:len(p)-1]
	   sum_=cap_zona+".medie_hourly."+ora+".feeds."+p+".sum"
	   new_dict[sum_]=feeds[d]
	  
	   count=cap_zona+".medie_hourly."+ora+".feeds."+p+".count"
	   new_dict[count]=1
	   
	   sum_=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
	   new_dict[sum_]=feeds[d]

	   count=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
	   new_dict[count]=1
	   
	update={"$inc": new_dict, "$unset": {cap_zona+".medie_hourly."+ora+".instantly."+minuto_pprec: "", cap_zona+".medie_hourly."+ora_pprec: ""}}
	result={"data":[query,update]}
	
	return result
	
def creazione_pattern_today_squares(cap_zona,squareid,timestamp,feeds):

	#anno_mese=timestamp[:6]
	ora=timestamp[8:10]
	
	ora_pprec=str(int(ora)-2)
	minuto=timestamp[10:12]
	minuto_pprec=str(int(minuto)-2)
	
	weekday=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
	
	weekday=weekday.weekday()
	
	feeds2=dict(feeds)	
	del feeds2['latitude']
	del feeds2['longitude']
	
	if ora=='23':
		weekday= (weekday+1) %7
	
	query={"_id": "Today_squares "+str(weekday)}
	new_dict={}

	for d in feeds2:
	   p=json.dumps(d)
	   p=p[1:len(p)-1]
	   sum_=cap_zona+"."+squareid+".medie_hourly."+ora+".feeds."+p+".sum"
	   new_dict[sum_]=feeds[d]
	   
	   count=cap_zona+"."+squareid+".medie_hourly."+ora+".feeds."+p+".count"
	   new_dict[count]=1
		
	   sum_=cap_zona+"."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
	   new_dict[sum_]=feeds[d]

	   count=cap_zona+"."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
	   new_dict[count]=1
	
	update={"$inc": new_dict, "$unset": {cap_zona+"."+squareid+".medie_hourly."+ora+".instantly."+minuto_pprec: "", cap_zona+"."+squareid+".medie_hourly."+ora_pprec: ""}}
	result={"data":[query,update]}
	
	return result

def creazione_pattern_raw(centralina,cap,square,timestamp,feeds):
	result={}
	anno_mese=timestamp[:6]
	minuto=timestamp[:12]
	
	query_raw={"centralina": centralina, "timestamp": anno_mese}
	update_raw={"$set": { minuto : { "feeds": feeds, "cap": cap, "zona_square": square } }}
	

	result={"data":[query_raw,update_raw]}
	
	return result

def creazione_pattern_zona (centralina,cap_zona,squareid,timestamp,feeds):
	
	feeds2=dict(feeds)	
	del feeds2['latitude']
	del feeds2['longitude']

	result={}
	new_dict={}
	epoch=datetime.datetime.utcfromtimestamp(0)        
	now=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
	days_from_epoch=(now-epoch).days
	#squareid=zona_square[8:]
	#zona=zona_square[:8]
	#cap_zona=cap_zona_square[:17]
	#squareid=cap_zona_square[18:]
	#giorno=timestamp[:8]
	ora=timestamp[8:10]	
	minuto=timestamp[10:12]
	print(cap_zona)
	print(squareid)

	weekday=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
	
	weekday=weekday.weekday()

	query_next_day={"_id": weekday+1 , "date": days_from_epoch }
	query_today={"_id": weekday, "date": days_from_epoch}

    #creo la query per il pattern del giorno dopo
	for d in feeds2:
		p=json.dumps(d)
		p=p[1:len(p)-1]

		#sum_=cap+"."+zona+".medie_daily."+p+".sum"
		sum_=cap_zona+".medie_daily."+p+".sum"
		new_dict[sum_]=feeds[d]
		#count=cap+"."+zona+".medie_daily."+p+".count"
		count=cap_zona+".medie_daily."+p+".count"
		new_dict[count]=1
		#sum_=cap+"."+zona+".squares."+squareid+".medie_daily.feeds."+p+".sum"
		sum_=cap_zona+".squares."+squareid+".medie_daily.feeds."+p+".sum"
		new_dict[sum_]=feeds[d]
		#count=cap+"."+zona+".squares."+squareid+".medie_daily.feeds."+p+".count"
		count=cap_zona+".squares."+squareid+".medie_daily.feeds."+p+".count"
		new_dict[count]=1
	new_values_nd={"$inc":new_dict}

	new_dict={}
	
    #creo pattern per la query del giorno attuale
	for d in feeds2:
		p=json.dumps(d)
		p=p[1:len(p)-1]
		
		#sum_=cap+"."+zona+".medie_hourly."+ora+".feeds."+p+".sum"
		sum_=cap_zona+".medie_hourly."+ora+".feeds."+p+".sum"
		new_dict[sum_]=feeds[d]
		#count=cap+"."+zona+".medie_hourly."+ora+".feeds."+p+".count"
		count=cap_zona+".medie_hourly."+ora+".feeds."+p+".count"
		new_dict[count]=1
		#sum_=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".sum"
		sum_=cap_zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".sum"
		new_dict[sum_]=feeds[d]
		#count=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".count"
		count=cap_zona+".squares."+squareid+".medie_hourly."+ora+".feeds."+p+".count"
		new_dict[count]=1

		#sum_=cap+"."+zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
		sum_=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
		new_dict[sum_]=feeds[d]
		#sum_=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
		sum_=cap_zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".sum"
		new_dict[sum_]=feeds[d]		
		#count=cap+"."+zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
		count=cap_zona+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
		new_dict[count]=1
		#count=cap+"."+zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
		count=cap_zona+".squares."+squareid+".medie_hourly."+ora+".instantly."+minuto+".feeds."+p+".count"
		new_dict[count]=1

	new_values_td={"$inc":new_dict}

	result = {"data":[[query_next_day,new_values_nd],[query_today,new_values_td]]}
	
	return result

# ---------------------- CARICAMENTO CONFIGURAZIONE ---------------------------
try:
    # with open("config.json","r") as file:
    # Per python 2.0 utilizzo libreria codecs per poter utilizzare la codifica "latin1" per il parametro "umidità":
    with codecs.open(utils.path+"config.json", "r", encoding="latin1") as file:
        __config = json.load(file)

    CONFIG_DATA = CONFIG_CLASS.ConfigClass(__config)
    # CONFIG_CLASS.print_riepilogo(CONFIG_DATA)

    # Verifico l'attivazione di entrambi i PMS:
    if CONFIG_DATA.get_pms1() and CONFIG_DATA.get_pms2():
        both = True
    else:
        both = False

    # caricamento percorso file dei poligoni

    # PathPol= open("PathPoligoni.conf", "r")
    # filePoligoni= PathPol.readline()
    # pulisco il path eliminando il carattere di fine riga '\n'
    # filePoligoni = filePoligoni[:len(filePoligoni)-1]

    # caricamento dei poligoni
    # with open(filePoligoni) as polygonData:
        	# polygons = json.load(polygonData)

    # caricamento percorso file dei quadratini
    # PathQua= open("PathSquares.conf", "r")
    # fileQuadratini= PathQua.readline()
    # pulisco il path eliminando il carattere di fine riga '\n'
    # fileQuadratini = fileQuadratini[:len(fileQuadratini)-1]
    # caricamento dei quadratini
    # with open(fileQuadratini) as squareData:
        	# squares = json.load(squareData)

    centralina = __config['FIREBASE_INFO']['ID_CENTRALINA']

    data_sensor = utils.authflask(url_auth, SECRET_KEY, centralina)
    # data_sensor=utils.authflask(url_auth, SECRET_KEY)

    polygons = data_sensor['data']['monitoring']['zone']
    squares = data_sensor['data']['monitoring']['squares']


except Exception as error:
    print("Errore nel caricamento della configurazione:\n")
    print(error)
    exit(-1)


# ------------------------------- BASELINE -------------------------------------
hour = datetime.datetime.now().hour
if CONFIG_DATA.get_baseline() == hour:
    pass


# ------------------------------- MAIN -----------------------------------------
def main():
    str_debug = ""
    str_debug += update_str_debug("\n\nINIZIO ESECUZIONE MAIN:\n")

    # ---------------------- INIZIALIZZAZIONE DEI SENSORI ---------------------------
    str_debug += update_str_debug("Fase di INIZIALIZZAZIONE ")

    print("\n\nProcedo con \"INIZIALIZZAZIONE DEI SENSORI\":\n")
    time.sleep(1)
    valori = {}
    GENERATED_EXCEPTIONS = []

    # inizializzazione BME:
    print("Inizializzazione BME")
    str_debug += update_str_debug("Inizializzazione BME ")
    try:
        bme_obj = BME.BME()
    except Exception as error:
        GENERATED_EXCEPTIONS.append([BME.BME_Exception(), error])
        print("ERRORE inizializzazione BME")

    # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
    time.sleep(2)

    # inizializzazione FAN:
    print("\nInizializzazione FAN")
    str_debug += update_str_debug("Inizializzazione FAN ")
    try:
        fan_obj = FAN.FAN()
    except Exception as error:
        GENERATED_EXCEPTIONS.append([FAN.FAN_Exception(), error])
        print("ERRORE inizializzazione FAN")

    # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
    time.sleep(2)

    # inizializzazione PAD TERMICO:
    if CONFIG_DATA.get_pad_termico():
        str_debug += update_str_debug("Inizializzazione PAD TERMICO")
        print("\nInizializzazione PAD TERMICO")
        try:
            pad_termico_obj = HEATER.HEATER()
        except Exception as error:
            GENERATED_EXCEPTIONS.append([HEATER.HEATER_Exception(), error])
            print("ERRORE inizializzazione PAD TERMICO")

        # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
        time.sleep(1)

    # inizializzazione PM1 o PM2

    # In questo modo verifichiamo si i PMS sono accesi al al primo avvio della centralina. In caso affermativo
    # forziamo lo spegnimento:
    if PMS.is_on(PMS.PIN_S1):
        str_debug += update_str_debug("Spegnimento primo avvio PM1 ")
        print("\nPM1 è acceso al primo avvio, procedo allo spegnimento")
        pms_1_obj = PMS.PmsClass(PMS.ADDRESS_1, PMS.PIN_S1, 13)
        pms_1_obj.switch_off()
        # print("PM1 spento")

    if PMS.is_on(PMS.PIN_S2):
        str_debug += update_str_debug("Spegnimento primo avvio PM2 ")
        print("\nPM2 è acceso al primo avvio, procedo allo spegnimento")
        pms_2_obj = PMS.PmsClass(PMS.ADDRESS_2, PMS.PIN_S2, 26)
        pms_2_obj.switch_off()
        # print("PM2 spento")

    if CONFIG_DATA.get_pms1() or CONFIG_DATA.get_pms2():
        str_debug += update_str_debug("Inizializzazione PMS ")

        # Verifica modalità di funzione dei PMS "singola" o "entrambi":
        if both:
            str_debug += update_str_debug("Modalità Both dei PMS")

            # ------------- Modalità entrambi PMS attivi --------------:

            if CONFIG_DATA.get_pms1():
                str_debug += update_str_debug("Inizializzazione PM1 ")
                # disattivo il PM2:
                CONFIG_DATA.set_pms2(False)

                print("\nInizializzazione PM1")
                try:
                    pms_1_obj = PMS.PmsClass(PMS.ADDRESS_1, 6, 13)
                    pms_1_obj.turn_on()
                except Exception as error:
                    # riattivo il PM2 in caso di guasto del PM1:
                    CONFIG_DATA.set_pms2(True)

                    ex = PMS.PMS_Exception()
                    ex.set(1)
                    GENERATED_EXCEPTIONS.append([ex, error])
                    print("ERRORE inizializzazione 1°PMS")

            elif CONFIG_DATA.get_pms2():
                str_debug += update_str_debug("Inizializzazione PM2 ")
                print("\nInizializzaizone PM2")
                try:
                    pms_2_obj = PMS.PmsClass(PMS.ADDRESS_2, 19, 26)
                    pms_2_obj.turn_on()
                except Exception as error:
                    ex = PMS.PMS_Exception()
                    ex.set(2)
                    GENERATED_EXCEPTIONS.append([ex, error])
                    print("ERRORE inizializzazione 2°PMS")

        else:
            str_debug += update_str_debug("Modalità singola dei PMS ")

            # ------------- Modalità singoli PMS attivi --------------

            # inizializzazione PM1:
            if CONFIG_DATA.get_pms1():
                str_debug += update_str_debug("Inizializzazione PM1 ")
                print("\nInizializzazione PM1")
                try:
                    pms_1_obj = PMS.PmsClass(PMS.ADDRESS_1, 6, 13)
                    pms_1_obj.turn_on()
                except Exception as error:
                    ex = PMS.PMS_Exception()
                    ex.set(1)
                    GENERATED_EXCEPTIONS.append([ex, error])
                    print("ERRORE inizializzazione 1°PMS")

            # inizializzazione PM2:
            if CONFIG_DATA.get_pms2():
                str_debug += update_str_debug("Inizializzazione PM2 ")
                print("\nInizializzaizone PM2")
                try:
                    pms_2_obj = PMS.PmsClass(PMS.ADDRESS_2, 19, 26)
                    pms_2_obj.turn_on()
                except Exception as error:
                    ex = PMS.PMS_Exception()
                    ex.set(2)
                    GENERATED_EXCEPTIONS.append([ex, error])
                    print("ERRORE inizializzazione 2°PMS")

        # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
        time.sleep(1)

    # inizializzazione primo ADS: NO2, CO
    if CONFIG_DATA.get_no2() or CONFIG_DATA.get_co():
        str_debug += update_str_debug("Inizializzazione ADS 1 ")
        print("\nInizializzazione 1°ADS: NO2 e CO")
        try:
            no2_gas = None
            co_gas = None

            if CONFIG_DATA.get_no2():
                no2_info = CONFIG_DATA.get_no2_info()
                no2_gas = ADS.GAS(ADS.GAS_NO2, no2_info['ID'],
                                  float(no2_info['K1']), float(no2_info['K2']), float(no2_info['Sens']))

            if CONFIG_DATA.get_co():
                co_info = CONFIG_DATA.get_co_info()
                co_gas = ADS.GAS(ADS.GAS_CO, co_info['ID'],
                                 float(co_info['K1']), float(co_info['K2']), float(co_info['Sens']))

            ads_1_obj = ADS.ADS(ADS.ADDRESS_1, no2_gas, co_gas)

        except Exception as error:
            ex = ADS.ADS_Exception()
            ex.set(1)
            GENERATED_EXCEPTIONS.append([ex, error])
            print("ERRORE inizializzazione 1°ADS")

        # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
        time.sleep(1)

    # inizializzazione secondo ADS: H2S, SO2
    if CONFIG_DATA.get_h2s() or CONFIG_DATA.get_so2():
        str_debug += update_str_debug("Inizializzazione ADS 2 ")
        print("\nInizializzazione 2°ADS: H2S e SO2")
        try:
            h2s_gas = None
            so2_gas = None

            if CONFIG_DATA.get_h2s():
                h2s_info = CONFIG_DATA.get_h2s_info()
                h2s_gas = ADS.GAS(ADS.GAS_H2S, h2s_info['ID'],
                                  float(h2s_info['K1']), float(h2s_info['K2']), float(h2s_info['Sens']))

            if CONFIG_DATA.get_so2():
                so2_info = CONFIG_DATA.get_co_info()
                so2_gas = ADS.GAS(ADS.GAS_SO2, so2_info['ID'],
                                  float(so2_info['K1']), float(so2_info['K2']), float(so2_info['Sens']))

            ads_2_obj = ADS.ADS(ADS.ADDRESS_2, h2s_gas, so2_gas)

        except Exception as error:
            ex = ADS.ADS_Exception()
            ex.set(2)
            GENERATED_EXCEPTIONS.append([ex, error])
            print("ERRORE inizializzazione 2°ADS")

        # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
        time.sleep(1)

    # inizializzazione terzo ADS: O3
    if CONFIG_DATA.get_o3():
        str_debug += update_str_debug("Inizializzazione ADS 3 ")
        print("\nInizializzazione 3°ADS: O3")
        try:
            o3_info = CONFIG_DATA.get_o3_info()
            o3_gas = ADS.GAS(ADS.GAS_O3, o3_info['ID'],
                             float(o3_info['K1']), float(o3_info['K2']), float(o3_info['Sens']))

            ads_3_obj = ADS.ADS(ADS.ADDRESS_3, o3_gas, None)

        except Exception as error:
            ex = ADS.ADS_Exception()
            ex.set(3)
            GENERATED_EXCEPTIONS.append([ex, error])
            print("ERRORE inizializzazione 3°ADS")

        # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
        time.sleep(1)

    # inizializzazione GPS:
    if CONFIG_DATA.get_gps():
        str_debug += update_str_debug("Inizializzazione GPS ")
        print("\nInizializzazione GPS")
        try:
            gps_obj = GPS.GPS()
        except Exception as error:
            GENERATED_EXCEPTIONS.append([GPS.GPS_Exception(), error])
            print("ERRORE inizializzazione GPS")

        # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
        time.sleep(1)

    # inizializzazione ANEMOMETRO:
    if CONFIG_DATA.get_anemometro():
        str_debug += update_str_debug("Inizializzazione ANEM")
        print("\nInizializzazione Anemometro")
        try:
            anem_obj = ANEM.ANEM()
        except Exception as error:
            GENERATED_EXCEPTIONS.append([ANEM.ANEM_Exception(), error])
            print("ERRORE inizializzazione Anemometro")

        # print("Stampa vettore GENERATED_EXCEPTIONS: ", GENERATED_EXCEPTIONS)
        time.sleep(1)

    # ----------------------- ERRORE SENSORI: NELLA FASE DI INIZIALIZZAZIONE ------------------------------
    dim_GENERATED_EXCEPTIONS = len(GENERATED_EXCEPTIONS)

    if dim_GENERATED_EXCEPTIONS > 0:
        str_debug += update_str_debug(
            "Generate eccezioni nella fase di INIZIALIZZAZIONE ")
        print("\nGenerate eccezioni nella fase di \"INIZIALIZZAZIONE DEI SENSORI\":")
        print("Stampa vettore dell'eccezioni: ")
        pprint.pprint(GENERATED_EXCEPTIONS, indent=2)

        print("\nProcedo con la fase di \"TEST\":\n")
        ExceptionHandler.HandlerClass(
            GENERATED_EXCEPTIONS, CONFIG_DATA, utils.createNameLog())
        time.sleep(2)

        CONFIG_CLASS.print_riepilogo(CONFIG_DATA)
    elif dim_GENERATED_EXCEPTIONS == 0:
        str_debug += update_str_debug(
            "Nessuna eccezione generata nella fase di INIZIALIZZAZIONE ")
        print(
            "\nNessuna eccezione generata nella fase di \"INIZIALIZZAZIONE DEI SENSORI\".")
        time.sleep(2)

    # ---------------------------------- CAMPIONAMENTO DEI DATI ---------------------------------------

	# rilevamento timestamp

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    str_debug += update_str_debug("Fase di CAMPIONAMENTO ")
    print("\n\nProcedo con il \"CAMPIONAMENTO DEI DATI\":\n")
    ERRORI_CAMPIONAMENTO = []

        # campionamento FAN:
    str_debug += update_str_debug("Campionamento FAN ")
    print("Campionamento FAN")
    try:
            # start=datetime.datetime.now()
            fan_obj.turn_on_test(10)
            # end=datetime.datetime.now()
            # print("Ventola in funzione per "+str(end-start))
            time.sleep(1)

    except Exception as error:
            ERRORI_CAMPIONAMENTO.append([FAN.FAN_Exception(), error])
            print("ERRORE nel campionamento sul FAN")
            time.sleep(2)

        # campionmento BME:
    str_debug += update_str_debug("Campionamento BME ")
    print("\nCampionamento BME")
    try:
        bme_vetDict = bme_obj.get_data()

            # faccio il controllo con l'if perchè bme_vetDict può essere uguale a None:
        if bme_vetDict != None:
                for i in bme_vetDict:
                    valori[i["key"]] = i['value']

            # print("Stampa valori: ")
            # print(valori)
        time.sleep(1)

    except Exception as error:
            ERRORI_CAMPIONAMENTO.append([BME.BME_Exception(), error])
            print("ERRORE nel campionamento sul BME")
            time.sleep(2)



        # campionamento PAD_TERMICO (HEATER):
    if CONFIG_DATA.get_pad_termico():
            if "temperatura" in valori:
                if valori["temperatura"]<15:
                    str_debug += update_str_debug("Campionamento HEATER ")

                    print("\nCampionamento HEATER")
                    try:
                        pad_termico_obj.turn_on_test(15)
                        time.sleep(1)

                    except Exception as error:
                        ERRORI_CAMPIONAMENTO.append([HEATER.HEATER_Exception(), error])
                        print("ERRORE nel campionamento sul HEATER")
                        time.sleep(2)



        # campionamento PM1 e/o PM2:
    if CONFIG_DATA.get_pms1() or CONFIG_DATA.get_pms2():
            str_debug += update_str_debug("Campionamento PMS ")

            # Verifica modalità di funzione dei PMS "singola" o "entrambi":
            if both:
                str_debug += update_str_debug("Modalità Both dei PMS")

                # ------------- Modalità entrambi PMS attivi -------------:

                if CONFIG_DATA.get_pms1():
                    str_debug += update_str_debug("Campionamento PM1 ")

                    # disattivo il PM2:
                    CONFIG_DATA.set_pms2(False)

                    print("\nCampionamento PM1")
                    try:
                        pms_1_vetVet = pms_1_obj.get_data()

                        # faccio il controllo con l'if perchè pms_1_vetVet può essere uguale a None:
                        if pms_1_vetVet != None:
                            for i in range(len(pms_1_vetVet)):
                                temp = pms_1_vetVet[i]
                                valori[temp[0]] = temp[1]

                        pms_1_obj.switch_off()

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        # riattivo il PM2 in caso di guasto del PM1:
                        CONFIG_DATA.set_pms2(True)

                        ex = PMS.PMS_Exception()
                        ex.set(1)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento PM1")
                        time.sleep(2)

                elif CONFIG_DATA.get_pms2():
                    str_debug += update_str_debug("Campionamento PM2 ")

                    print("\nCampionamento PM2")
                    try:
                        pms_2_vetVet = pms_2_obj.get_data()

                        # faccio il controllo con l'if perchè pms_2_vetVet può essere uguale a None:
                        if pms_2_vetVet != None:
                            for i in range(len(pms_2_vetVet)):
                                temp = pms_2_vetVet[i]
                                valori[temp[0]] = temp[1]

                        pms_2_obj.switch_off()

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = PMS.PMS_Exception()
                        ex.set(2)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento PM2")
                        time.sleep(2)

            else:

                # -------------- Modalità singoli PMS attivi -------------:
                str_debug += update_str_debug("Modalità singola dei PMS ")

                # campionamento PM1
                if CONFIG_DATA.get_pms1():
                    str_debug += update_str_debug("Campionamento PM1 ")

                    print("\nCampionamento PM1")
                    try:
                        pms_1_vetVet = pms_1_obj.get_data()

                        # faccio il controllo con l'if perchè pms_1_vetVet può essere uguale a None:
                        if pms_1_vetVet != None:
                            for i in range(len(pms_1_vetVet)):
                                temp = pms_1_vetVet[i]
                                valori[temp[0]] = temp[1]

                        pms_1_obj.switch_off()

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = PMS.PMS_Exception()
                        ex.set(1)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento PM1")
                        time.sleep(2)

                # campionamento PM2
                if CONFIG_DATA.get_pms2():
                    str_debug += update_str_debug("Campionamento PM2 ")

                    print("\nCampionamento PM2")
                    try:
                        pms_2_vetVet = pms_2_obj.get_data()

                        # faccio il controllo con l'if perchè pms_2_vetVet può essere uguale a None:
                        if pms_2_vetVet != None:
                            for i in range(len(pms_2_vetVet)):
                                temp = pms_2_vetVet[i]
                                valori[temp[0]] = temp[1]

                        pms_2_obj.switch_off()

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = PMS.PMS_Exception()
                        ex.set(2)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento PM2")
                        time.sleep(2)



        # campionamento ADS:
        # se il BME non riesce a calcolare la temperatura, nessun ADS viene calcolato:
    if "temperatura" in valori:
            temperatura = valori["temperatura"]

            # campionamento ADS1: NO2 e CO

            if CONFIG_DATA.get_no2():
                str_debug += update_str_debug("Campionamento ADS 1: NO2 ")

                print("\nCampionamento 1°ADS: NO2")
                # nella fase di inizializzazione "no2_gas" potrebbe essere rimasto a None.
                # quindi il campionamento lo fai solo se "no2_gas" è diverso da None:
                if no2_gas != None:
                    try:
                        ads1_dict = ads_1_obj.get_processed_data(ADS.PIN_A,
                                                                 setNT.set_nt(ADS.GAS_NO2, temperatura))

                        valori[ads1_dict["key"]] = ads1_dict["value"]

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = ADS.ADS_Exception()
                        ex.set(1)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento NO2")
                        time.sleep(2)

            if CONFIG_DATA.get_co():
                str_debug += update_str_debug("Campionamento ADS 1: CO ")

                print("\nCampionamento 1°ADS: CO")
                # nella fase di inizializzazione "co_gas" potrebbe essere rimasto a None.
                # quindi il campionamento lo fai solo se "co_gas" è diverso da None:
                if co_gas != None:
                    try:
                        ads1_dict = ads_1_obj.get_processed_data(ADS.PIN_B,
                                                                 setNT.set_nt(ADS.GAS_CO, temperatura))

                        valori[ads1_dict["key"]] = ads1_dict["value"]

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = ADS.ADS_Exception()
                        ex.set(1)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento CO")
                        time.sleep(2)


            # campionamento ADS2: H2S e SO2

            if CONFIG_DATA.get_h2s():
                str_debug += update_str_debug("Campionamento ADS 2: H2S ")

                print("\nCampionamento 2°ADS: H2S")
                # nella fase di inizializzazione "h2s_gas" potrebbe essere rimasto a None.
                # quindi il campionamento lo fai solo se "h2s_gas" è diverso da None:
                if h2s_gas != None:
                    try:
                        ads2_dict = ads_2_obj.get_processed_data(ADS.PIN_A,
                                                                 setNT.set_nt(ADS.GAS_H2S, temperatura))

                        valori[ads2_dict["key"]] = ads2_dict["value"]

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = ADS.ADS_Exception()
                        ex.set(2)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento H2S")
                        time.sleep(2)

            if CONFIG_DATA.get_so2():
                str_debug += update_str_debug("Campionamento ADS 2: SO2 ")

                print("\nCampionamento 2°ADS: SO2")
                # nella fase di inizializzazione "so2_gas" potrebbe essere rimasto a None.
                # quindi il campionamento lo fai solo se "so2_gas" è diverso da None:
                if so2_gas != None:
                    try:
                        ads2_dict = ads_2_obj.get_processed_data(ADS.PIN_B,
                                                                 setNT.set_nt(ADS.GAS_SO2, temperatura))

                        valori[ads2_dict["key"]] = ads2_dict["value"]

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = ADS.ADS_Exception()
                        ex.set(2)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento SO2")
                        time.sleep(2)


            # campionamento ADS3: O3

            if CONFIG_DATA.get_o3():
                str_debug += update_str_debug("Campionamento ADS 3: O3 ")

                print("\nCampionamento 3°ADS: O3")
                # nella fase di inizializzazione "o3_gas" potrebbe essere rimasto a None se "O3" è su False.
                # quindi il campionamento lo fai solo se "o3_gas" è diverso da None:
                if o3_gas != None:
                    try:
                        ads3_dict = ads_3_obj.get_processed_data(ADS.PIN_A,
                                                                 setNT.set_nt(ADS.GAS_O3, temperatura))

                        valori[ads3_dict["key"]] = ads3_dict["value"]

                        # print("Stampa valori: ")
                        # print(valori)
                        time.sleep(1)

                    except Exception as error:
                        ex = ADS.ADS_Exception()
                        ex.set(3)
                        ERRORI_CAMPIONAMENTO.append([ex, error])
                        print("ERRORE nel campionamento O3")
                        time.sleep(2)
    else:
            print("\nCampionamento ADS non eseguito, temperatura non disponibile")
            time.sleep(1)


        # campionamento GPS:
    if CONFIG_DATA.get_gps():
            str_debug += update_str_debug("Campionamento GPS ")

            print("\nCampionamento GPS")
            # Centralina MOBILE:
            try:
                gps_vetDict = gps_obj.get_data()

                # faccio il controllo con l'if perchè gps_vetDict può essere uguale a None:
                if gps_vetDict[0]["key"] != None:
                    for i in gps_vetDict:
                        valori[i["key"]] = i['value']

                    # print("Stampa valori: ")
                    # print(valori)
                    time.sleep(1)

                elif gps_vetDict[0]["key"] == None:
                    ERRORI_CAMPIONAMENTO.append([GPS.GPS_Exception(), gps_vetDict[0]["value"]])
                    print("ERRORE nel campionamento GPS")
                    time.sleep(2)

            except Exception as error:
                ERRORI_CAMPIONAMENTO.append([GPS.GPS_Exception(), error])
                print("ERRORE nel campionamento GPS")
                time.sleep(2)

    else:
            print("\nCampionamento GPS")
            # Centralina FISSA:
            try:
                # Inserimento di LATI e LONG in "valori" presi dal file di configurazione:
                info_gps = CONFIG_DATA.get_gps_info()
                valori["latitude"] = info_gps.get("LATITUDINE")
                valori["longitude"] = info_gps.get("LONGITUDINE")
            except Exception as error:
                ERRORI_CAMPIONAMENTO.append([GPS.GPS_Exception(), error])
                print("ERRORE nel campionamento GPS")
                time.sleep(2)

            # print("Stampa valori: ")
            # print(valori)
            time.sleep(1)



        # campionamento ANEMOMETRO:
    if CONFIG_DATA.get_anemometro():
            str_debug += update_str_debug("Campionamento ANEM ")
            print("\nCampionamento Anemometro")
            try:
                str_debug += update_str_debug("---------------Inizio lettura anem ")
                anem_vetDict = anem_obj.get_data()
                str_debug += update_str_debug("---------------Fine lettura  ANEM ")

                # faccio il controllo con l'if perchè anem_vetDict può essere uguale a None:
                str_debug += update_str_debug("INIZIO CICLO ESTERNO (MAIN)  CAMPIONAMENTO ANEM ")
                str_debug += update_str_debug("ANEM_VETDICT {}  ".format(anem_vetDict))
                if anem_vetDict != None:
                    index=1
                    for i in anem_vetDict:
                        str_debug += update_str_debug("Iterazione n {} ".format(index))
                        valori[i['key']] = i['value']
                        index+=1

                str_debug += update_str_debug("FINE CICLO ESTERNO (MAIN) CAMPIONAMENTO ANEM ")

                # print("Stampa valori: ")
                # print(valori)
                time.sleep(1)

            except Exception as error:
                ERRORI_CAMPIONAMENTO.append([ANEM.ANEM_Exception(), error])
                print("ERRORE nel campionamento sull'Anemometro")
                time.sleep(2)






        # ----------------- ERRORE SENSORI: NELLA FASE DI CAMPIONAMENTO DEI DATI --------------------------
    dim_ERRORI_CAMPIONAMENTO = len(ERRORI_CAMPIONAMENTO)

    if dim_ERRORI_CAMPIONAMENTO > 0:
            str_debug += update_str_debug("Generate eccezioni nella fase di CAMPIONAMENTO ")

            print("\nGenerate eccezioni nella fase di \"CAMPIONAMENTO DEI DATI\":")
            print("Stampa vettore dell'eccezioni: ")
            pprint.pprint(ERRORI_CAMPIONAMENTO, indent=2)

            print("\n\nProcedo con la fase di \"TEST\":\n")
            ExceptionHandler.HandlerClass(ERRORI_CAMPIONAMENTO, CONFIG_DATA, utils.createNameLog())
            time.sleep(2)

            CONFIG_CLASS.print_riepilogo(CONFIG_DATA)
    elif dim_ERRORI_CAMPIONAMENTO == 0:
            str_debug += update_str_debug("Nessuna eccezione generata nella fase di CAMPIONAMENTO ")

            print("\nNessuna eccezione generata nella fase di \"CAMPIONAMENTO DEI DATI\".")
            time.sleep(2)


        # controllo del pacchetto dati prima di procedere all'invio:
    if "latitude" not in valori or "longitude" not in valori:
            str_debug += update_str_debug("Dato non inviato perchè non ha acquisito il GPS ")

            print("\n\nERRORE: parametri GPS non acquisiti, dato NON INVIATO.")
            time.sleep(2)

    elif len(valori)==2 and "latitude"  in valori and "longitude" in valori:
            str_debug += update_str_debug("Dato non inviato perchè è presente solo LATI e LONG ")

            print("\n\nERRORE: pacchetto dati contiene solo i parametri GPS, dato NON INVIATO")
            time.sleep(2)

    else:
            # ----------------------------- INVIO DEI DATI (BUFFERIZZAZIONE) ------------------------------
            str_debug += update_str_debug("Fase di INVIO DEI DATI ")

            # conversione dei dati:
            for i in valori:
                if i == "latitude":
                    # print(type(valori[i]))

                    # prendi il dato e poi lo converti da stringa a float:
                    dato_lati = valori[i]
                    valori[i] = float(dato_lati)

                    # print(type(valori[i]))
                    # print(valori[i])

                elif i == "longitude":
                    # print(type(valori[i]))

                    # prendi il dato e poi lo converti da stringa a float:
                    dato_lati = valori[i]
                    valori[i] = float(dato_lati)

                    # print(type(valori[i]))
                    # print(valori[i])

                else:
                    # prendo il dato e lo converto in un float con max 3 decimali:
                    dato = valori[i]
                    valori[i] = round(float(dato), 3)

            print("\n\nProcedo con \"INVIO DEI DATI (BUFFERIZZAZIONE)\":")
            print("Valori da inviare: ")
            pprint.pprint(valori, indent=2)
            time.sleep(2)

                  
            creazione_dati_file(CONFIG_DATA, valori,polygons,squares, data_sensor, timestamp)


    if DEBUG:
            try:
                utils.checkPath(utils.path + "Main_Log/")
                fileName=utils.path+"Main_Log/Main_Log_"+datetime.datetime.today().strftime('%d_%m_%Y')+".txt"
                with open(fileName, 'a') as file:
                    file.write("PROVA")
                    file.write(str_debug)

                print("Stampa Main_log.txt riuscita")

            except:
                print("Stampa Main_log.txt non riuscita")





if __name__ == '__main__':
    try:
        while True:
            main()
            time.sleep(60)

    except:
        # ------------------------ ERRORE NON GESTITO ------------------------------ #

        # Invoco la funzione "save_error" che mi salva l'errore verificato nel main:
        save_error(traceback.format_exc())
