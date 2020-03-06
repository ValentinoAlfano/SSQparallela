# coding=utf-8

import json
import time
import requests
import firebase
import datetime
import codecs
import sort_feed
import CONFIG_CLASS
import utils
import os
from pathlib import Path
import random



# VARIABILI GLOBALI:


URL_Flask = "http://192.168.2.144:5000/send_sample_ssq"



# ------------ Funzione di DEBUG --------------
STR_DEBUG = ""
DEBUG=True

def update_str_debug(messaggio):
    tempo = datetime.datetime.today().strftime("%H:%M:%S")
    stringa_debug = messaggio + "(" + tempo + ")" + "\n"
    return stringa_debug



# --------------------- FUNZIONI --------------------------:

# Funzione controllo internet:
def check_internet():
    try:
        risposta=requests.get("http://www.google.com/")
        if risposta.status_code == 200:
            print("Connessione Riuscita: "+str(risposta.status_code)+" "+str(risposta.reason))
            return True
        else:
            print("Connessione Fallita: "+str(risposta.status_code)+" "+str(risposta.reason))
            return False
    except Exception:
        print("ERRORE CONNESSIONE")



#---------------------- FUNZIONI per Flask -----------------------------------:

# Funzione che verifica se il file "DATABUFFER.json" esiste già:

def lettura_file_vuoto():
	
    if os.path.exists(utils.path+"DATABUFFER.json"):    
        print("\nFile DATABUFFER.json ESISTE\n")
        return 1
    else:
        print("\nFile DATABUFFER.json NON ESISTE\n")
        return 0
    

# non usata, sostituita dalla precedente
def lettura_file_vuoto_old(): 
    try:
        with open(utils.path+"DATABUFFER.json", 'r') as fp:
            readFile = fp.read()
            if readFile == "":
                print("\nFile DATABUFFER.json VUOTO\n")
                return 1
            else:
                print("\nFile DATABUFFER.json contiene DATI\n")
                return 0
    except Exception:
        print("ERRORE: lettura file \"DATABUFFER.json\" non riuscita")



# Funzione che scrive sul file "DATABUFFER.json":
def scrittura_file_BUONA(dato):
    try:
        with open(utils.path+"DATABUFFER.json", 'w') as file:
            json.dump(dato, file)
        print("\nFile DATABUFFER.json aggiornato")
    except Exception as e:
        print("\nERRORE: scrittura del dato sul file non riuscita")
        print(e)

# Funzione che scrive in append sul file "DATABUFFER_YY_MM_DD.json"
def scrittura_file(filename, dato):
	try:		
		with open(filename, 'w') as file:
			json.dump(dato, file)

		print("\nFile " + filename + " aggiornato")
	except Exception as e:		
		print("\n ERRORE: scrittura del dato non riuscita")
		print(e)



# Funzione che ci restituisce la data in un vettore[anno, mese, giorno, ecc.]
def recupero_data(t):
    tempo_fromtimestamp = datetime.datetime.fromtimestamp(t)

    year = tempo_fromtimestamp.strftime('%Y')
    month = tempo_fromtimestamp.strftime('%m')
    day = tempo_fromtimestamp.strftime('%d')
    hour = tempo_fromtimestamp.strftime('%H')
    minute = tempo_fromtimestamp.strftime('%M')
    second = tempo_fromtimestamp.strftime('%S')

    data = [year, month, day, hour, minute, second]

    return data

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
	
	
	
	



# Funzione di invio dati a Firebase, restituisce True se l'invio avviene in modo corretto:

def invio_dati_flask(centralina, data, data_sensor):
	
	global STR_DEBUG

	try:
		STR_DEBUG += update_str_debug("\nINIZIO ESECUZIONE invio_dati_flask: ")

		conn=check_internet()
		#conn=False
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



# Funzione di invio dati a Flask:

def send_flask_old(centralina,valori,polygons,squares,data_sensor, timestamp):
	global STR_DEBUG
	global DEBUG
	print("Sono in send_flask")
	lat=valori['latitude']
	lon=valori['longitude']
	coordinate=(lat,lon)

	STR_DEBUG += update_str_debug("\n INIZIO ESECUZIONE send_flask")
	
	contenitore_buffer=[]
	
	data=creazione_data_request(centralina,polygons,coordinate,squares, timestamp,valori,data_sensor)	

	if not lettura_file_vuoto():  #se non esiste DATABUFFER.json entra
		STR_DEBUG += update_str_debug("\n Lettura file DATABUFFER vuoto")
		tentativo_conn=0
		#Prova Invio
		while tentativo_conn<3:
			STR_DEBUG += update_str_debug("\n Tentativo connessione numero:" + str(tentativo_conn)+ " ")
			connessione=check_internet()
			if connessione:
				break
			else:
				print("Tentativo di connessione numero:" + str(tentativo_conn))
				tentativo_conn = tentativo_conn +1
				time.sleep(20)
				
		if connessione:
			STR_DEBUG += update_str_debug("Connessione riuscita: invio dati")
			#invio dati
			n_dati_ricevuti = 0
			
			esitoInvio=invio_dati_flask(centralina, data, data_sensor)
			if esitoInvio:
				STR_DEBUG += update_str_debug("Dato inviato con successo")
				n_dati_ricevuti += 1
				print ("Numero dati ricevuti:" + str(n_dati_ricevuti))
			if n_dati_ricevuti==0:
				STR_DEBUG += update_str_debug("Dato non inviato, memorizzato nel buffer")
				print ("Numero dati ricevuti:" + str(n_dati_ricevuti))
				contenitore_buffer.append(data)
				scrittura_file(contenitore_buffer)
		else:
			#connessione fallita
			STR_DEBUG += update_str_debug ("Connessione fallita: invio dati fallito, aggiornamento buffer")
			contenitore_buffer.append(data)
			scrittura_file(contenitore_buffer)
	else:
		#file non vuoto
		#lettura dati dal buffer
		STR_DEBUG += update_str_debug ("Lettura file DATABUFFER pieno")
		pacchetto_dati=[]
		with open(utils.path+"DATABUFFER.json", "r") as fp:
			pacchetto_dati=json.load(fp)
		
		#aggiunta del nuovo oggetto ricevuto più il contenuto del buffer
		pacchetto_dati.append(data)
		
		#prova invio
		tentativo_conn=0
		while tentativo_conn<3:
			STR_DEBUG += update_str_debug ("Tentativo connessione numero:" +str(tentativo_conn)+ " ")
			connessione=check_internet()
			if connessione:
				break
			else:
				print("Tentativo connessione numero:" +str(tentativo_conn))
				tentativo_conn = tentativo_conn +1
				time.sleep(20)
		if connessione:
			#invio dati
			STR_DEBUG += update_str_debug("Connessione riuscita: invio dati")
			dim_pacchetto = len(pacchetto_dati)
			print ("\n Numero di pacchetti da inviare:" +str(dim_pacchetto))
			i=0
			n_dati_ricevuti=0
			while i<dim_pacchetto:
				esitoInvio=invio_dati_flask(centralina,pacchetto_dati[i],data_sensor)
				if esitoInvio:
					print("Pacchetto numero:" + str(i) + "ricevuto\n")
					n_dati_ricevuti +=1
					i +=1
				else:
					print("Pacchetto numero:" + str(i) + "non ricevuto\n")
					break
			print("numero dati ricevuti:" +str(n_dati_ricevuti))
			
			if n_dati_ricevuti==dim_pacchetto:
			#cancellazione databuffer
				STR_DEBUG += update_str_debug("DATABUFFER svuotato")
				os.remove(utils.path+"DATABUFFER.json")
				#with open(utils.path+"DATABUFFER.json","w") as file:
				#	file.write("")
				print ("file DATABUFFER.json eliminato")
			elif 0<n_dati_ricevuti<dim_pacchetto:
				STR_DEBUG += update_str_debug("ricevuti solo alcuni oggetti del pacchetto dati")
				i=0
				j=0
				while j<n_dati_ricevuti:
					#ipotizzo che vengano presi i primi oggetti del pacchetto_dati
					pacchetto_dati.pop(i)
					print ("Primo oggetto del pacchetto_dati eliminato" +str(j))
					j=j+1
				scrittura_file(pacchetto_dati)
			elif n_dati_ricevuti==0:
				
				STR_DEBUG += update_str_debug("Connessione fallita: aggiorno databuffer")
				scrittura_file(pacchetto_dati)
	if DEBUG:
		try:
			utils.checkPath(utils.path + "InvioDati_Log/")
			fileName=utils.path+"InvioDati_Log/InvioDati_log_"+datetime.datetime.today().strftime('%d_%m_%Y')+".txt"
			
			with open(fileName,'a')as file:
				file.write(STR_DEBUG)
			print ("Stampa InvioDati_log.txt riuscita")
		except:
			print ("Stampa InvioDati_log.txt non riuscita")

#Funzione nuova da testare
def send_flask(centralina, valori, polygons, squares, data_sensor, timestamp):
	global STR_DEBUG
	global DEBUG
	#print("Sono in send_flask")
	lat=valori['latitude']
	lon=valori['longitude']
	coordinate=(lat,lon)

	STR_DEBUG += update_str_debug("\n INIZIO ESECUZIONE send_flask")
	
	#contenitore_buffer = []
	
	#DATO CAMPIONATO
	data_sample = creazione_data_request(centralina,polygons,coordinate,squares, timestamp,valori,data_sensor)	
	#SCRIVO DATO CAMPIONATO SU FILE
	filename = utils.path + "DATABUFFER_" + timestamp[:10] + ".json"
	scrittura_file(filename, data_sample)

	#controllare se file con timestamp esiste
	#creo nome file con la data di oggi
	#epoch=datetime.datetime.utcfromtimestamp(0)        
	#now=datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
	#days_from_epoch=(now-epoch)

	#hours = (now - epoch).total_seconds() / 3600
	
	#CARICO LISTA FILE PRECEDENTI DA INVIARE
	file_list = utils.check_databuffer()

	for file in file_list:
		
		with open(file, "r") as fp:
			#CARICO PACCHETTI DA FILE
			data_sample_from_file = json.load(fp)	
		
		#Faccio 3 tentativi di connessione
		while tentativo_conn < 3: 
			STR_DEBUG += update_str_debug("\n Tentativo connessione numero:" + str(tentativo_conn)+ " ")
			connessione = check_internet()
			print("Stato connessione: " + str(connessione))
			if connessione:
				break
			else:
				print("Tentativo di connessione numero:" + str(tentativo_conn))
				tentativo_conn = tentativo_conn +1
				time.sleep(1)
				
		if connessione:
			STR_DEBUG += update_str_debug("Connessione riuscita: invio dati")
			
			print("Leggo: " + file)
			print("Contiene " + len(data_sample_from_file) + " pacchetti")			

			
			#invio dati
			#n_dati_ricevuti = 0
			i = 0
			#n_dati_ricevuti=0
			while len(data_sample_from_file):
				esitoInvio = invio_dati_flask(centralina,data_sample_from_file[0],data_sensor)
				if esitoInvio:
					print("Pacchetto numero:" + str(i) + " ricevuto\n")
					i += 1
					#n_dati_ricevuti +=1
					#rimuovo primo pacchetto della lista
					data_sample_from_file.pop(0)
					#dim_pacchetto = len(pacchetto_dati)
				else:
					print("Pacchetto numero:" + str(i) + " non ricevuto\n")
					break
				print("numero dati ricevuti:" +str(i))
				
			if len(data_sample_from_file) == 0:
				#SE ENTRO QUI, HO MANDATO TUTTO IL CONTENUTO DEL FILE

				STR_DEBUG += update_str_debug("DATABUFFER svuotato")
				#cancello file corrente
				os.remove(file)
				print("Eliminato " + file)
			else:
				#riscrivo i pacchetti che non sono riuscito a inviare nello stesso file
				scrittura_file(file, data_sample_from_file)

				# if not os.path.exists(utils.path + "DATABUFFER/" + str(hours) + ".json"):
				# 	filename = utils.path + "DATABUFFER_" + datetime.datetime.now().strftime("%Y_%m_%d") + ".json"
				# 	filename = utils.path + "DATABUFFER/" + str(hours) + ".json"
				# 	scrittura_file(filename, contenitore_buffer)
				# else:
				# 	pass #se esiste già non fare niente
				
		else:
			#connessione fallita
			print("Connessione fallita.")
			STR_DEBUG += update_str_debug ("Connessione fallita: invio dati fallito, aggiornamento buffer")
			#scrittura_file(filename, contenitore_buffer)
			
	if DEBUG:
		try:
			utils.checkPath(utils.path + "InvioDati_Log/")
			fileName=utils.path+"InvioDati_Log/InvioDati_log_"+datetime.datetime.today().strftime('%d_%m_%Y')+".txt"
			
			with open(fileName,'a')as file:
				file.write(STR_DEBUG)
			print ("Stampa InvioDati_log.txt riuscita")
		except:
			print ("Stampa InvioDati_log.txt non riuscita")	




#----------------------- FUNZIONI per ThingSpeak ------------------------------:

# Funzione che ritorna url per ThingSpeak:
def url_thingspeak(dati,api,vettore):
    global STR_DEBUG
    STR_DEBUG += update_str_debug("\nINIZIO ESECUZIONE url_thingspeak: ")

    url = "https://api.thingspeak.com/update?"+"api_key="+api
    i=0
    for field in vettore:

        # codifica dei valori field da unicode a latin1:
        field = codecs.encode(field, "latin1")

        if dati.get(field) is not None:
            url+= '&field'+str(i+1)+'='+str(dati[field])
        i=i+1

    return url


# Funzione di invio dati a ThingSpeak:
def send_thinkspeak(info,valori):
    global STR_DEBUG
    global DEBUG
    STR_DEBUG += update_str_debug("\nINIZIO ESECUZIONE send_thinkspeak: ")

    n_canali = info['NUMERO_CANALI']
    api_keys = info['API_KEYS']
    campi_canali = info['CAMPI']

    # Creazione url:
    url=[]
    i=0
    while i<n_canali:
        url.append(url_thingspeak(valori,api_keys[i],campi_canali[i]))
        i+=1

    # 10 tentativi di connessione, appena la rete è disponibile invia il dato altrimenti questo viene perso:
    invio_successo=False
    for i in range(10):
        if check_internet()!=True:
            STR_DEBUG += update_str_debug("Connessione fallita: invio dati ")
            STR_DEBUG += update_str_debug("Tentativo di connssione numero " + str((i+1)) + " ")

            print("Tentativo di connessione numero "+str((i+1)))
            i+=1
            time.sleep(1)
        else:
            STR_DEBUG += update_str_debug("Connessione riuscita: invio dati ")

            n = 1
            for j in url:
                try:
                    requests.get(j)
                    print("\ninvio dei dati sul CANALE "+str(n)+" riuscito.")

                    STR_DEBUG += update_str_debug("Invio del dato sul canale " + str(n) + " riuscito ")
                    #time.sleep(5)
                except:
                    STR_DEBUG += update_str_debug("Invio del dato sul canale " + str(n) + " fallito ")
                    print("ERRORE: invio dei dati sul CANALE "+str(n)+" fallito")
                    
                n += 1
            invio_successo=True
            break

    if invio_successo==False:
        STR_DEBUG += update_str_debug("Raggiunto limite di tentativi di invio del dato. Dato perso ")
        
        print("\nERRORE: Raggiunto limite di tentativi. Dato perso")

    if DEBUG:
        try:
            fileName = utils.path + "InvioDati_Log/InvioDati_log_" + datetime.datetime.today().strftime('%d_%m_%Y') + ".txt"
            with open(fileName, 'a') as file:
                file.write(STR_DEBUG)

            print("Stampa InvioDati_log.txt riuscita")

        except:
            print("Stampa InvioDati_log.txt non riuscita")




#------------------------- FUNZIONI per il main --------------------------------------:

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
def send_data(config,valori,polygon,squares, data_sensor, timestamp):
    global STR_DEBUG
    STR_DEBUG += update_str_debug("\n\n\n---- INIZIO ESECUZIONE send_data: ")

    # Verifico se FLASK è attivo a "True" per poter inviare il dato a Flask:

    if config.get_firebase():
        STR_DEBUG += update_str_debug("Flask attivo ")

        # recupero le info per inviare a Flask (nome della centralina):
        print("\nINVIO DATI SU FLASK:")
        info_firebase = config.get_firebase_info()
        centralina = info_firebase['ID_CENTRALINA']

	


        send_flask(centralina, valori, polygon, squares, data_sensor, timestamp)

    # Verifico se ThingSpeak è attivo per poter inviare il dato a ThingSpeak:
    if config.get_thingspeak():
        STR_DEBUG = ""
        STR_DEBUG += update_str_debug("\n\n\n---- CONTINUA ESECUZIONE send_data: ")
        STR_DEBUG += update_str_debug("ThingSpeak attivo ")

        print("\n\nINVIO DATI SU THINGSPEAK:\n")
        # recupero le info per inviare a ThingSpeak:
        info_thingspeak = config.get_thingspeak_info()

        send_thinkspeak(info_thingspeak,valori)

# Funzione main:
def invio_dati(valori):
    # Lettura dal file configurazione e creazione dell'oggetto "dati_configurazione"
    dati_configurazione = CONFIG_CLASS.ConfigClass(lettura_file_configurazione())

    # Invio dati:
    send_data(dati_configurazione,valori,polygon,squares, data_sensor, timestamp)


if __name__ == '__main__':
    valori = {"no2": 30,
              "so2": 50,
              "co": 316.0,
              "cpuTemperature": 42.084,
              "direzione_vento": 6,
              "gas_m": 70,
              "intensita_vento": 2,
              "latitude": 45.06479159126726,
              "longitude": 7.675323486328125,
              "nt": 5.6316710782,
              "pm1": 15.0,
              "pm10": 21.0,
              "pm2_5": 20.0,
              "pressione": 987.82,
              "programStatus": 33,
              "temperatura": 27.87,
              "umidita": 46.48,
              "voc": 24.35}

    invio_dati(valori)
