#!/bin/bash

ChoosenFile=$(zenity --file-selection --title "Seleziona il file dei Poligoni" --multiple --file-filter='*.json *.geojson')

if [ -f "PathSquares.conf" ]; then
rm PathSquares.conf	
 fi
echo "$ChoosenFile" >> PathSquares.conf