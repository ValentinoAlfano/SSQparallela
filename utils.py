from datetime import datetime
import json
import requests
import os
from pathlib import Path

# Path per il SystemStarter:
#path = os.getcwd() + "/"
path = "/home/pi/Desktop/SSQparallela/"

#Funzione che restituisce la lista di file DATABUFFER
def check_databuffer():
	#print("Sono in check_databuffer()")
	files = Path(path).glob('DATABUFFER_*')	
	#files = Path(Path.cwd()).glob('DATABUFFER_*')	
	file_list = []
	date_list = []
	#creo lista date
	for file in files:
		file_str = str(file)
		#RICAVO LA DATA DAL NOME DEL FILE
		date_str = file_str.split("/")[-1][11:21]
		date = datetime.strptime(date_str, "%Y%m%d%H")
		date_list.append(date)
	#ORDINO LA LISTA DI DATE: PRIMO ELEMENTO -> PIU' RECENTE
	date_list.sort(reverse=True) 

	#converto lista ordinata date in lista file
	for date in date_list:
		date_str = date.strftime("%Y%m%d%H")
		file_str = "DATABUFFER_" + date_str + ".json"
		file_list.append(path + file_str)
	#print(file_list)
	return file_list
	

def checkPath(percorso):
	if os.path.exists(percorso):
		return True
	else:
		os.mkdir(percorso)
		print("La cartella " + path + percorso + " non esisteva, l'ho creata")

def createNameLog():
	checkPath(path + 'Error_Log/')
	return path + 'Error_Log/ErrorLog_'+datetime.today().strftime('%d_%m_%Y')+'.txt'


# def createNameLog_old():

# 	return path+'Error_Log/ErrorLog_'+datetime.today().strftime('%d_%m_%Y')+'.txt'

def createNamePositiveTest():
	checkPath(path + 'Positive_Log/')
	return path + 'Positive_Log/PositiveTest_'+datetime.today().strftime('%d_%m_%Y')+'.txt'


def authflask(url, SECRET_KEY, centralina):


	data2= json.dumps({"key": SECRET_KEY, "_id": centralina} )
	
	

	response=requests.post(url, data=data2)
	
	print (response)

	data =response.json()

	

	return data


def auth_users(url, SECRET_KEY):


	data2= json.dumps({"user_info" : {"password": "Gasrad98", "email": "prova@gmail.com"} })
	
	response=requests.post(url, data=data2)
	
	token =response.json()
	
	token = token['data']['user_info']['token']


	return token 