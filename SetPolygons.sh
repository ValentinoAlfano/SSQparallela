#!/bin/bash

ChoosenFile=$(zenity --file-selection --title "Seleziona il file dei Poligoni" --multiple --file-filter='*.json *.geojson')

if [ -f "PathPoligoni.conf" ]; then
rm PathPoligoni.conf	
 fi
echo "$ChoosenFile" >> PathPoligoni.conf
