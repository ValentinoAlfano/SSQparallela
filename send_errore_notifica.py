# coding=utf-8

import datetime
import json
import CONFIG_CLASS
import firebase
import time
import requests
import os.path
import utils




#--------------- FUNZIONI --------------------:

# Funzione di accesso al Firebase:
def accessdbFirebaseWithAuth(dsn, SECRET_KEY, email, admin=False):
    '''
    ------------FUNZIONAMENTO----------------
    Funzione tramite la quale si apre la connessione col Database

    Parametri d'ingresso:  dsn -> url del database
                           SECRET_KEY -> Chiave segreta del database Firebase
                           email -> email fittizia da attribuire ad ogni centralina  (utile alla scrittura dei log)
                           admin -> possibilità di accedere al database in modalità admin  (utile all'utilizzo della funzione quando il file viene richiamato come script per effettuare test)
    Parametro di ritorno:  db -> variabile che contiene il collegamento al database tramite cui si effettuano le operazioni su di esso

    '''

    from firebase import firebase
    import datetime

    auth = firebase.FirebaseAuthentication(SECRET_KEY, email, admin,
                                           admin)  # funzione che serve a creare l'autenticazione
    db = firebase.FirebaseApplication(dsn,
                                      auth)  # accedo al database con l'url "dsn" e l'autorizzazione e istanzio l'oggetto db

    return db  # ritorna l'oggetto tramite il quale accediamo al DataBase


# Funzione che verifica la connessione:
def check_internet():
    try:
        risposta = requests.get("http://www.google.com/")
        if risposta.status_code == 200:
            # print("Connessione Riuscita:",risposta.status_code,risposta.reason)
            print("Connessione Riuscita: " + str(risposta.status_code) + " " + str(risposta.reason))
            return True
        else:
            # print("Connessione Fallita:",risposta.status_code,risposta.reason)
            print("Connessione Faalita: " + str(risposta.status_code) + " " + str(risposta.reason))
            return False
    except:
        print("ERRORE CONNESSIONE")


# Lettura file di configurazione, restituisce tutti i dati del file di configurazione:
def lettura_file_configurazione():
    try:
        with open(utils.path+"config.json",'r') as f:
            dati_conf=json.load(f)

        print("\nLettura file: \"config.json\" riuscita\n")

        return dati_conf
    except Exception as e:
        print("ERRORE: lettura file \"config.json\" non riuscita\n")
        print(e)


# Funzione che mi permette di avere il timestamp, cioè il tempo in decimale (usata per python 2.0):
def to_seconds(date):
    return time.mktime(date.timetuple())







# Funzione dell'invio della notifica di errore a Firebase:
def invio_dati(centralina,dato,db):
    try:
        # Recupero tempo, data e percorso per la memorizzazione su Firebase:
        tempo=dato['tempo']
        tempo_centralina=str(tempo)+str("_")+str(centralina)

        percorso="Notifica_Errori/Error_Log/"
        package_notifica=dict(timestamp=tempo, id_centralina=centralina, timestamp_id_centralina=tempo_centralina)

        # invio notifica al database:
        if check_internet():
            db.post(percorso,package_notifica)
            return True
        else:
            return False

    except Exception:
        print("ERRORE: invio dati non riuscito")
        return False


# Funzione di invio a Firebase
def send_firebase(centralina, accessoDB):
    # Oggetto "db" per connettersi al Firebase:
    db = accessdbFirebaseWithAuth(accessoDB[0], accessoDB[1], accessoDB[2])

    # Recupero ora e definizione del dato con ora:
    ora=int(to_seconds(datetime.datetime.now()))
    dato= dict(tempo=ora)

    if check_internet():
        esito_invio=invio_dati(centralina,dato,db)
        # print(esito_invio)
        if esito_invio:
            print("\nSalvataggio \"notifica di Error_Log\" su Firebase RIUSCITO")
        else:
            print("\nSalvataggio \"notifica di Error_Log\" su Firebase FALLITO")


# Funzione di chiamata per l'invio dell'errore:
def send_errore(accessoDB):
    # Lettura dal file configurazione e creazione dell'oggetto "dati_configurazione"
    configurazione = CONFIG_CLASS.ConfigClass(lettura_file_configurazione())

    # Verifco se la Notifica Errori è attiva a "True":
    if (configurazione.get_notifica_errori()) :

        # Verifico se Firebase è attivo a "True" per poter inviare il dato a Firebase:
        if (configurazione.get_firebase()):

            # Verifico se esiste il file di Error_log:
            if (os.path.exists(utils.createNameLog())) :

                # recupero le info per inviare a Firebase (nome della centralina):
                print("\nINVIO NOTIFICA ERROR_LOG SU FIREBASE:")

                info_firebase = configurazione.get_firebase_info()
                centralina = info_firebase['ID_CENTRALINA']

                send_firebase(centralina, accessoDB)

            else :
                print('File di log non è presente')

        else :
            print('Firebase non attivo')

    else :
        print('Sistema di notifica non abilitato')





if __name__=='__main__':
    # Variabili di connessione al db di Firebase:
    #URL = 'https://prova1-11cd5.firebaseio.com/'
    #SECRET_KEY = 'uWNKf5KfWyui3hMcgxzDS3co1TiKuZHcumLj2CR6'

    URL='https://sensesquaredb.firebaseio.com/'
    SECRET_KEY = '0JuzXIx0GkGP1OKS4LltwLVgQrnaaYX5MDP421KT'
    EMAIL = "test@mail.com"
    accessoDB = [URL, SECRET_KEY, EMAIL]

    send_errore(accessoDB)

