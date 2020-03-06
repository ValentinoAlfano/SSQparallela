# coding=utf-8


import datetime
#import firebase
import time
import requests

# Funzione di accesso al Firebase:
# def accessdbFirebaseWithAuth(dsn, SECRET_KEY, email, admin=False):
#     '''
#     ------------FUNZIONAMENTO----------------
#     Funzione tramite la quale si apre la connessione col Database

#     Parametri d'ingresso:  dsn -> url del database
#                            SECRET_KEY -> Chiave segreta del database Firebase
#                            email -> email fittizia da attribuire ad ogni centralina  (utile alla scrittura dei log)
#                            admin -> possibilità di accedere al database in modalità admin  (utile all'utilizzo della funzione quando il file viene richiamato come script per effettuare test)
#     Parametro di ritorno:  db -> variabile che contiene il collegamento al database tramite cui si effettuano le operazioni su di esso

#     '''

#     from firebase import firebase
#     import datetime

#     auth = firebase.FirebaseAuthentication(SECRET_KEY, email, admin,
#                                            admin)  # funzione che serve a creare l'autenticazione
#     db = firebase.FirebaseApplication(dsn,
#                                       auth)  # accedo al database con l'url "dsn" e l'autorizzazione e istanzio l'oggetto db

#     return db  # ritorna l'oggetto tramite il quale accediamo al DataBase

# Funzione che mi permette di avere il timestamp, cioè il tempo in decimale (usata per python 2.0):
def to_seconds(date):
    return time.mktime(date.timetuple())

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







# Funzione dell'invio della notifica di errore a Firebase:
def invio_dati(centralina,dato,db):
    try:
        # Recupero tempo, e costruisco il dato tempo_centralina:
        tempo=dato['tempo']
        tempo_centralina=str(tempo)+str("_")+str(centralina)


        percorso="Notifica_Errori/BME/"
        package_notifica=dict(timestamp=tempo, id_centralina=centralina, timestamp_id_centralina=tempo_centralina)

        # invio notifica al database:
        if check_internet():
            db.post(percorso,package_notifica)
            return True
        else:
            return False

    except Exception as e:
        print("ERRORE: invio dati non riuscito")
        return False


# Funzione di invio a Firebase
def send_firebase(centralina,DB):
    # Oggetto "db" per connettersi al Firebase:
    db = accessdbFirebaseWithAuth(DB[0], DB[1], DB[2])

    # Recupero ora e definizione del dato con ora:
    ora = int(to_seconds(datetime.datetime.now()))
    dato = dict(tempo=ora)

    if check_internet():
        esito_invio=invio_dati(centralina,dato,db)
        # print(esito_invio)
        if esito_invio:
            print("\nSalvataggio \"notifica di errore BME\" su Firebase RIUSCITO")
        else:
            print("\nSalvataggio \"notifica di errore BME\" su Firebase FALLITO")







if __name__=='__main__':
    # Variabili di connessione al db di Firebase:
    URL = 'https://prova1-11cd5.firebaseio.com/'
    SECRET_KEY = 'uWNKf5KfWyui3hMcgxzDS3co1TiKuZHcumLj2CR6'
    EMAIL = "test@mail.com"
    accessoDB = [URL, SECRET_KEY, EMAIL]

    cent="ID_CENTRALINA"

    send_firebase(cent,accessoDB)
