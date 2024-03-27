#!/usr/bin/env sh

PLOTDIRECTORY="paperCode/scripts/plotScripts"

#Recreate all plots
python3 $PLOTDIRECTORY/createPlots/createAllPlots.py

#draw them
sh $PLOTDIRECTORY/drawPlots/drawAllPlots.sh
