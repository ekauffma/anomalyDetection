#!/usr/bin/env sh

DRAWDIRECTORY="paperCode/scripts/plotScripts/drawPlots"

python3 $DRAWDIRECTORY/drawScorePlots.py
python3 $DRAWDIRECTORY/drawROCsFromScores.py --HT --L1Axis --LogAxis
python3 $DRAWDIRECTORY/drawCICADAandHTCorrelation.py
python3 $DRAWDIRECTORY/drawTeacherStudentPlots.py
python3 $DRAWDIRECTORY/drawIndividualROCCurves.py
